#!/usr/bin/env python3
"""
Forex Sniper Bot - Real-time forex trading with OANDA API
Simpler and more profitable than stocks!
"""

import pandas as pd
import numpy as np
import re
import warnings
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from textblob import TextBlob
import requests
import json
import time
import logging
import os
from dataclasses import dataclass
import sqlite3

# OANDA API
import oandapyV20
from oandapyV20 import API
from oandapyV20.endpoints import instruments, pricing, orders, trades, accounts
from oandapyV20.contrib.requests import MarketOrderRequest, TakeProfitDetails, StopLossDetails

warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ForexSignal:
    """Data class for forex trading signals."""
    id: str
    date: datetime
    pair: str
    signal_type: str  # BUY, SELL
    confidence_score: float
    entry_price: float
    target_price: float
    stop_loss: float
    headline: str
    source: str
    sentiment_score: float
    status: str  # PENDING, EXECUTED, CANCELLED, EXPIRED
    created_at: datetime
    expires_at: datetime
    pip_target: int
    pip_stop: int

class ForexNewsManager:
    """Manages forex news from multiple sources."""
    
    def __init__(self):
        self.apis = {
            'alpha_vantage': {
                'base_url': 'https://www.alphavantage.co/query',
                'key': os.getenv('ALPHA_VANTAGE_API_KEY'),
            },
            'forex_factory': {
                'base_url': 'https://nfs.faireconomy.media/ff_calendar_thisweek.json',
                'key': None  # Free API
            }
        }
    
    def get_forex_news(self, limit: int = 50) -> List[Dict]:
        """Fetch forex-specific news."""
        all_news = []
        
        # Get news from Alpha Vantage (forex-focused)
        try:
            if self.apis['alpha_vantage']['key']:
                params = {
                    'function': 'NEWS_SENTIMENT',
                    'apikey': self.apis['alpha_vantage']['key'],
                    'topics': 'forex',
                    'limit': limit
                }
                
                response = requests.get(self.apis['alpha_vantage']['base_url'], params=params)
                data = response.json()
                
                if 'feed' in data:
                    for item in data['feed']:
                        all_news.append({
                            'headline': item.get('title', ''),
                            'summary': item.get('summary', ''),
                            'source': item.get('source', ''),
                            'date': item.get('time_published', ''),
                            'sentiment_score': float(item.get('overall_sentiment_score', 0)),
                            'api_source': 'alpha_vantage'
                        })
        except Exception as e:
            logger.warning(f"Error fetching forex news: {e}")
        
        # Get economic calendar events (affects forex)
        try:
            response = requests.get(self.apis['forex_factory']['base_url'])
            events = response.json()
            
            for event in events[:20]:  # Limit to recent events
                if event.get('impact') in ['High', 'Medium']:  # Only important events
                    all_news.append({
                        'headline': f"{event.get('country', '')} - {event.get('title', '')}",
                        'summary': f"Impact: {event.get('impact', '')} | Forecast: {event.get('forecast', 'N/A')}",
                        'source': 'Forex Factory',
                        'date': event.get('date', ''),
                        'sentiment_score': 0,
                        'api_source': 'forex_factory'
                    })
        except Exception as e:
            logger.warning(f"Error fetching economic calendar: {e}")
        
        return all_news

class ForexSignalDatabase:
    """SQLite database for forex signals."""
    
    def __init__(self, db_path: str = 'data/forex_signals.db'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS forex_signals (
                id TEXT PRIMARY KEY,
                date TEXT,
                pair TEXT,
                signal_type TEXT,
                confidence_score REAL,
                entry_price REAL,
                target_price REAL,
                stop_loss REAL,
                headline TEXT,
                source TEXT,
                sentiment_score REAL,
                status TEXT,
                created_at TEXT,
                expires_at TEXT,
                pip_target INTEGER,
                pip_stop INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_signal(self, signal: ForexSignal):
        """Save a forex signal."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO forex_signals 
            (id, date, pair, signal_type, confidence_score, entry_price, target_price, 
             stop_loss, headline, source, sentiment_score, status, created_at, expires_at,
             pip_target, pip_stop)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            signal.id, signal.date.isoformat(), signal.pair, signal.signal_type,
            signal.confidence_score, signal.entry_price, signal.target_price,
            signal.stop_loss, signal.headline, signal.source, signal.sentiment_score,
            signal.status, signal.created_at.isoformat(), signal.expires_at.isoformat(),
            signal.pip_target, signal.pip_stop
        ))
        
        conn.commit()
        conn.close()
    
    def get_active_signals(self) -> List[ForexSignal]:
        """Get active forex signals."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM forex_signals 
            WHERE status = 'PENDING' AND expires_at > ?
            ORDER BY confidence_score DESC, created_at DESC
        ''', (datetime.now().isoformat(),))
        
        signals = []
        for row in cursor.fetchall():
            signals.append(self._row_to_signal(row))
        
        conn.close()
        return signals
    
    def _row_to_signal(self, row) -> ForexSignal:
        """Convert database row to ForexSignal."""
        return ForexSignal(
            id=row[0], date=datetime.fromisoformat(row[1]), pair=row[2],
            signal_type=row[3], confidence_score=row[4], entry_price=row[5],
            target_price=row[6], stop_loss=row[7], headline=row[8],
            source=row[9], sentiment_score=row[10], status=row[11],
            created_at=datetime.fromisoformat(row[12]),
            expires_at=datetime.fromisoformat(row[13]),
            pip_target=row[14], pip_stop=row[15]
        )

class ForexSniperBot:
    """Forex Sniper Bot with OANDA integration."""
    
    def __init__(self, oanda_api_key: str, account_id: str, environment: str = "practice"):
        self.logger = logging.getLogger(__name__)
        
        # OANDA Setup
        self.api_key = oanda_api_key
        self.account_id = account_id
        self.environment = environment  # "practice" or "live"
        self.api = API(access_token=oanda_api_key, environment=environment)
        
        # Components
        self.news_manager = ForexNewsManager()
        self.signal_db = ForexSignalDatabase()
        
        # Major forex pairs
        self.major_pairs = [
            'EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CHF',
            'AUD_USD', 'USD_CAD', 'NZD_USD'
        ]
        
        # Currency impact mapping
        self.currency_impact = {
            'USD': ['EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CHF', 'AUD_USD', 'USD_CAD', 'NZD_USD'],
            'EUR': ['EUR_USD', 'EUR_GBP', 'EUR_JPY', 'EUR_CHF'],
            'GBP': ['GBP_USD', 'EUR_GBP', 'GBP_JPY', 'GBP_CHF'],
            'JPY': ['USD_JPY', 'EUR_JPY', 'GBP_JPY', 'AUD_JPY'],
            'CHF': ['USD_CHF', 'EUR_CHF', 'GBP_CHF'],
            'AUD': ['AUD_USD', 'AUD_JPY', 'EUR_AUD'],
            'CAD': ['USD_CAD', 'CAD_JPY'],
            'NZD': ['NZD_USD', 'NZD_JPY']
        }
        
        self.logger.info(f"Forex Sniper Bot initialized with OANDA {environment} environment")
    
    def get_current_price(self, pair: str) -> Dict:
        """Get current bid/ask prices for a forex pair."""
        try:
            params = {"instruments": pair}
            r = pricing.PricingInfo(accountID=self.account_id, params=params)
            response = self.api.request(r)
            
            price_data = response['prices'][0]
            return {
                'bid': float(price_data['bids'][0]['price']),
                'ask': float(price_data['asks'][0]['price']),
                'spread': float(price_data['asks'][0]['price']) - float(price_data['bids'][0]['price']),
                'time': price_data['time']
            }
        except Exception as e:
            self.logger.error(f"Error getting price for {pair}: {e}")
            return None
    
    def calculate_pip_value(self, pair: str, price: float) -> float:
        """Calculate pip value for position sizing."""
        # For most pairs, 1 pip = 0.0001
        # For JPY pairs, 1 pip = 0.01
        if 'JPY' in pair:
            return 0.01
        else:
            return 0.0001
    
    def extract_currency_pairs(self, headline: str) -> List[str]:
        """Extract relevant currency pairs from news headline."""
        found_pairs = []
        headline_upper = headline.upper()
        
        # Direct currency mentions
        currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'NZD']
        mentioned_currencies = [curr for curr in currencies if curr in headline_upper]
        
        # Country/region to currency mapping
        country_mapping = {
            'UNITED STATES': 'USD', 'US': 'USD', 'AMERICA': 'USD', 'FEDERAL RESERVE': 'USD', 'FED': 'USD',
            'EUROPE': 'EUR', 'EUROPEAN': 'EUR', 'ECB': 'EUR', 'EUROZONE': 'EUR',
            'BRITAIN': 'GBP', 'UK': 'GBP', 'ENGLAND': 'GBP', 'BOE': 'GBP',
            'JAPAN': 'JPY', 'JAPANESE': 'JPY', 'BOJ': 'JPY',
            'SWITZERLAND': 'CHF', 'SWISS': 'CHF', 'SNB': 'CHF',
            'AUSTRALIA': 'AUD', 'AUSTRALIAN': 'AUD', 'RBA': 'AUD',
            'CANADA': 'CAD', 'CANADIAN': 'CAD', 'BOC': 'CAD',
            'NEW ZEALAND': 'NZD', 'RBNZ': 'NZD'
        }
        
        for country, currency in country_mapping.items():
            if country in headline_upper:
                mentioned_currencies.append(currency)
        
        # Find relevant pairs
        for currency in set(mentioned_currencies):
            if currency in self.currency_impact:
                found_pairs.extend(self.currency_impact[currency])
        
        # If no specific currencies found, use major pairs for general forex news
        if not found_pairs and any(word in headline_upper for word in ['FOREX', 'CURRENCY', 'EXCHANGE', 'RATE']):
            found_pairs = ['EUR_USD', 'GBP_USD', 'USD_JPY']
        
        return list(set(found_pairs))
    
    def analyze_sentiment(self, text: str) -> float:
        """Enhanced sentiment analysis for forex."""
        try:
            blob = TextBlob(text)
            base_sentiment = blob.sentiment.polarity
            
            # Forex-specific keywords
            bullish_keywords = [
                'rate hike', 'hawkish', 'strong economy', 'gdp growth', 'employment up',
                'inflation target', 'economic expansion', 'currency strength', 'positive outlook',
                'beats expectations', 'exceeds forecast', 'robust', 'surge', 'rally'
            ]
            
            bearish_keywords = [
                'rate cut', 'dovish', 'recession', 'unemployment', 'inflation concern',
                'economic slowdown', 'currency weakness', 'negative outlook', 'disappointing',
                'misses expectations', 'below forecast', 'decline', 'plunge', 'crisis'
            ]
            
            text_lower = text.lower()
            sentiment_boost = 0
            
            for keyword in bullish_keywords:
                if keyword in text_lower:
                    sentiment_boost += 0.2
            
            for keyword in bearish_keywords:
                if keyword in text_lower:
                    sentiment_boost -= 0.2
            
            enhanced_sentiment = base_sentiment + sentiment_boost
            return max(-1.0, min(1.0, enhanced_sentiment))
            
        except Exception as e:
            self.logger.warning(f"Error in sentiment analysis: {e}")
            return 0.0
    
    def calculate_trade_levels(self, pair: str, current_price: Dict, sentiment_score: float, confidence_score: float) -> Dict:
        """Calculate entry, target, and stop loss levels for forex."""
        pip_value = self.calculate_pip_value(pair, current_price['ask'])
        
        # Dynamic pip targets based on confidence and volatility
        base_target_pips = 20  # Base target: 20 pips
        base_stop_pips = 10    # Base stop: 10 pips
        
        # Adjust based on confidence (higher confidence = larger targets)
        confidence_multiplier = min(2.0, 1 + confidence_score)
        target_pips = int(base_target_pips * confidence_multiplier)
        stop_pips = int(base_stop_pips * confidence_multiplier * 0.8)  # Slightly tighter stops
        
        if sentiment_score > 0:  # Bullish - BUY
            entry_price = current_price['ask']
            target_price = entry_price + (target_pips * pip_value)
            stop_loss = entry_price - (stop_pips * pip_value)
            signal_type = 'BUY'
        else:  # Bearish - SELL
            entry_price = current_price['bid']
            target_price = entry_price - (target_pips * pip_value)
            stop_loss = entry_price + (stop_pips * pip_value)
            signal_type = 'SELL'
        
        return {
            'signal_type': signal_type,
            'entry_price': entry_price,
            'target_price': target_price,
            'stop_loss': stop_loss,
            'pip_target': target_pips,
            'pip_stop': stop_pips,
            'spread': current_price['spread']
        }
    
    def generate_forex_signals(self, confidence_threshold: float = 0.3) -> List[ForexSignal]:
        """Generate forex trading signals from news."""
        self.logger.info("Generating forex signals from news...")
        
        news_items = self.news_manager.get_forex_news(limit=50)
        
        if not news_items:
            self.logger.warning("No forex news retrieved")
            return []
        
        self.logger.info(f"Processing {len(news_items)} forex news items...")
        
        signals = []
        today = datetime.now().date()
        
        for news in news_items:
            headline = news.get('headline', '')
            source = news.get('source', '')
            
            if not headline:
                continue
            
            # Extract relevant currency pairs
            pairs = self.extract_currency_pairs(headline)
            if not pairs:
                continue
            
            # Analyze sentiment
            sentiment_score = news.get('sentiment_score', 0)
            if sentiment_score == 0:
                sentiment_score = self.analyze_sentiment(headline)
            
            # Skip neutral sentiment
            if abs(sentiment_score) < 0.1:
                continue
            
            # Calculate confidence (simpler for forex)
            confidence_score = abs(sentiment_score) * 1.5  # Scale up for forex
            
            if confidence_score < confidence_threshold:
                continue
            
            # Generate signals for each relevant pair
            for pair in pairs[:2]:  # Limit to top 2 pairs per news item
                current_price = self.get_current_price(pair)
                if not current_price:
                    continue
                
                trade_levels = self.calculate_trade_levels(pair, current_price, sentiment_score, confidence_score)
                
                signal = ForexSignal(
                    id=f"{pair}_{int(time.time())}_{hash(headline) % 10000}",
                    date=datetime.now(),
                    pair=pair,
                    signal_type=trade_levels['signal_type'],
                    confidence_score=confidence_score,
                    entry_price=trade_levels['entry_price'],
                    target_price=trade_levels['target_price'],
                    stop_loss=trade_levels['stop_loss'],
                    headline=headline,
                    source=source,
                    sentiment_score=sentiment_score,
                    status='PENDING',
                    created_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(hours=4),  # Shorter expiry for forex
                    pip_target=trade_levels['pip_target'],
                    pip_stop=trade_levels['pip_stop']
                )
                
                signals.append(signal)
                self.signal_db.save_signal(signal)
                
                # Limit total signals
                if len(signals) >= 5:
                    break
            
            if len(signals) >= 5:
                break
        
        self.logger.info(f"Generated {len(signals)} forex signals")
        return signals
    
    def place_order(self, signal: ForexSignal, units: int = 1000) -> bool:
        """Place a forex order via OANDA API."""
        try:
            # Create market order with TP and SL
            order_data = {
                "order": {
                    "type": "MARKET",
                    "instrument": signal.pair,
                    "units": str(units if signal.signal_type == 'BUY' else -units),
                    "takeProfitOnFill": {
                        "price": str(round(signal.target_price, 5))
                    },
                    "stopLossOnFill": {
                        "price": str(round(signal.stop_loss, 5))
                    }
                }
            }
            
            r = orders.OrderCreate(accountID=self.account_id, data=order_data)
            response = self.api.request(r)
            
            self.logger.info(f"Order placed: {signal.pair} {signal.signal_type} at {signal.entry_price}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            return False
    
    def get_account_summary(self) -> Dict:
        """Get OANDA account summary."""
        try:
            r = accounts.AccountSummary(accountID=self.account_id)
            response = self.api.request(r)
            
            account = response['account']
            return {
                'balance': float(account['balance']),
                'unrealized_pl': float(account['unrealizedPL']),
                'margin_used': float(account['marginUsed']),
                'margin_available': float(account['marginAvailable']),
                'open_trades': int(account['openTradeCount']),
                'currency': account['currency']
            }
        except Exception as e:
            self.logger.error(f"Error getting account summary: {e}")
            return {}

if __name__ == "__main__":
    # Example usage
    api_key = os.getenv('OANDA_API_KEY', 'your_oanda_api_key_here')
    account_id = os.getenv('OANDA_ACCOUNT_ID', 'your_account_id_here')
    
    bot = ForexSniperBot(api_key, account_id, environment="practice")
    
    # Generate signals
    signals = bot.generate_forex_signals(confidence_threshold=0.3)
    
    print(f"Generated {len(signals)} forex signals:")
    for signal in signals:
        print(f"  {signal.pair} {signal.signal_type} @ {signal.entry_price:.5f} "
              f"(Target: {signal.pip_target} pips, Stop: {signal.pip_stop} pips)") 