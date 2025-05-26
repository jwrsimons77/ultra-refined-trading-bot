#!/usr/bin/env python3
"""
🎯 Optimized Advanced Trading System Backtest
Balanced approach: Quality filtering + Opportunity capture
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OptimizedAdvancedBacktest:
    """
    Optimized backtest with balanced quality vs opportunity approach
    """
    
    def __init__(self, initial_balance: float = 1000):
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        
        # OPTIMIZED Trading parameters
        self.min_confidence = 0.45  # Lowered from 0.65 to capture more opportunities
        self.max_concurrent_positions = 8  # Increased from 5
        self.base_risk_pct = 0.025  # Slightly reduced risk per trade
        
        # Enhanced signal generation
        self.technical_threshold = 0.2  # Lowered from 0.3 for more signals
        self.session_bonus_multiplier = 1.5  # Increased session impact
        
        # Results tracking
        self.executed_trades = []
        self.all_signals = []
        self.filtered_signals = []
        self.rejected_signals = []
        
        logger.info("🎯 Optimized Advanced Backtest initialized")
    
    def get_forex_data(self, pair: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get forex data from Yahoo Finance."""
        try:
            yf_symbols = {
                'EUR/USD': 'EURUSD=X', 'GBP/USD': 'GBPUSD=X', 'USD/JPY': 'USDJPY=X',
                'USD/CHF': 'USDCHF=X', 'AUD/USD': 'AUDUSD=X', 'USD/CAD': 'USDCAD=X',
                'NZD/USD': 'NZDUSD=X'
            }
            
            symbol = yf_symbols.get(pair)
            if not symbol:
                return pd.DataFrame()
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date, interval='1h')
            
            if data.empty:
                return pd.DataFrame()
            
            # Convert timezone-aware index to timezone-naive
            if data.index.tz is not None:
                data.index = data.index.tz_convert('UTC').tz_localize(None)
            
            logger.info(f"📊 Retrieved {len(data)} hourly candles for {pair}")
            return data
            
        except Exception as e:
            logger.error(f"Error getting data for {pair}: {e}")
            return pd.DataFrame()
    
    def calculate_enhanced_technical_score(self, data: pd.DataFrame) -> Dict:
        """Calculate enhanced technical analysis with multiple signals."""
        try:
            if len(data) < 50:
                return {'score': 0.0, 'signals': [], 'strength': 'weak'}
            
            close = data['Close']
            high = data['High']
            low = data['Low']
            
            signals = []
            total_score = 0.0
            
            # 1. RSI Analysis (More sensitive)
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            if current_rsi < 35:  # Oversold (relaxed from 30)
                total_score += 0.25
                signals.append("RSI Oversold")
            elif current_rsi > 65:  # Overbought (relaxed from 70)
                total_score -= 0.25
                signals.append("RSI Overbought")
            
            # 2. Moving Average Confluence
            ma_10 = close.rolling(window=10).mean()
            ma_20 = close.rolling(window=20).mean()
            ma_50 = close.rolling(window=50).mean()
            current_price = close.iloc[-1]
            
            # Multiple MA alignment
            if current_price > ma_10.iloc[-1] > ma_20.iloc[-1] > ma_50.iloc[-1]:
                total_score += 0.35
                signals.append("Strong Bullish MA")
            elif current_price < ma_10.iloc[-1] < ma_20.iloc[-1] < ma_50.iloc[-1]:
                total_score -= 0.35
                signals.append("Strong Bearish MA")
            elif current_price > ma_20.iloc[-1] > ma_50.iloc[-1]:
                total_score += 0.2
                signals.append("Bullish MA")
            elif current_price < ma_20.iloc[-1] < ma_50.iloc[-1]:
                total_score -= 0.2
                signals.append("Bearish MA")
            
            # 3. MACD with Signal Line
            exp1 = close.ewm(span=12).mean()
            exp2 = close.ewm(span=26).mean()
            macd = exp1 - exp2
            signal_line = macd.ewm(span=9).mean()
            macd_histogram = macd - signal_line
            
            # MACD crossovers and momentum
            if len(macd_histogram) >= 2:
                if macd_histogram.iloc[-1] > 0 and macd_histogram.iloc[-2] <= 0:
                    total_score += 0.3
                    signals.append("MACD Bullish Cross")
                elif macd_histogram.iloc[-1] < 0 and macd_histogram.iloc[-2] >= 0:
                    total_score -= 0.3
                    signals.append("MACD Bearish Cross")
                elif macd_histogram.iloc[-1] > 0:
                    total_score += 0.1
                    signals.append("MACD Bullish")
                elif macd_histogram.iloc[-1] < 0:
                    total_score -= 0.1
                    signals.append("MACD Bearish")
            
            # 4. Bollinger Bands
            bb_period = 20
            bb_std = 2
            bb_middle = close.rolling(window=bb_period).mean()
            bb_std_dev = close.rolling(window=bb_period).std()
            bb_upper = bb_middle + (bb_std_dev * bb_std)
            bb_lower = bb_middle - (bb_std_dev * bb_std)
            
            if current_price <= bb_lower.iloc[-1]:
                total_score += 0.2
                signals.append("BB Oversold")
            elif current_price >= bb_upper.iloc[-1]:
                total_score -= 0.2
                signals.append("BB Overbought")
            
            # 5. Price momentum
            price_change_5 = (current_price - close.iloc[-6]) / close.iloc[-6] * 100
            if abs(price_change_5) > 0.5:  # Significant momentum
                if price_change_5 > 0:
                    total_score += 0.15
                    signals.append("Bullish Momentum")
                else:
                    total_score -= 0.15
                    signals.append("Bearish Momentum")
            
            # Determine signal strength
            abs_score = abs(total_score)
            if abs_score > 0.6:
                strength = 'strong'
            elif abs_score > 0.3:
                strength = 'moderate'
            else:
                strength = 'weak'
            
            final_score = max(-1.0, min(1.0, total_score))
            
            return {
                'score': final_score,
                'signals': signals,
                'strength': strength,
                'rsi': current_rsi,
                'price_vs_ma20': (current_price - ma_20.iloc[-1]) / ma_20.iloc[-1] * 100
            }
            
        except Exception as e:
            logger.error(f"Error calculating technical score: {e}")
            return {'score': 0.0, 'signals': [], 'strength': 'weak'}
    
    def generate_optimized_signal(self, pair: str, price: float, technical_analysis: Dict, timestamp: datetime) -> Optional[Dict]:
        """Generate optimized trading signal with better opportunity capture."""
        try:
            technical_score = technical_analysis['score']
            
            # More lenient signal generation
            if abs(technical_score) < self.technical_threshold:
                return None
            
            signal_type = "BUY" if technical_score > 0 else "SELL"
            
            # Dynamic pip targets based on volatility and strength
            if 'JPY' in pair:
                pip_value = 0.01
                if technical_analysis['strength'] == 'strong':
                    target_pips = np.random.uniform(25, 45)
                    stop_pips = np.random.uniform(15, 25)
                else:
                    target_pips = np.random.uniform(20, 35)
                    stop_pips = np.random.uniform(12, 20)
            else:
                pip_value = 0.0001
                if technical_analysis['strength'] == 'strong':
                    target_pips = np.random.uniform(30, 55)
                    stop_pips = np.random.uniform(18, 28)
                else:
                    target_pips = np.random.uniform(25, 40)
                    stop_pips = np.random.uniform(15, 25)
            
            if signal_type == "BUY":
                target_price = price + (target_pips * pip_value)
                stop_loss = price - (stop_pips * pip_value)
            else:
                target_price = price - (target_pips * pip_value)
                stop_loss = price + (stop_pips * pip_value)
            
            # Enhanced confidence calculation
            base_confidence = min(abs(technical_score) * 0.8, 0.85)  # More achievable
            
            # Session analysis with enhanced bonuses
            hour = timestamp.hour
            session_bonus = 0.0
            session_name = "Off-hours"
            
            if 13 <= hour <= 17:  # London-NY overlap
                session_bonus = 0.15 * self.session_bonus_multiplier
                session_name = "London-NY Overlap"
            elif 8 <= hour <= 12:  # London session
                session_bonus = 0.1 * self.session_bonus_multiplier
                session_name = "London Session"
            elif 18 <= hour <= 22:  # NY session
                session_bonus = 0.08 * self.session_bonus_multiplier
                session_name = "NY Session"
            elif 0 <= hour <= 7:  # Asian session
                session_bonus = 0.05 * self.session_bonus_multiplier
                session_name = "Asian Session"
            else:
                session_bonus = -0.05
            
            # Technical strength bonus
            strength_bonus = 0.0
            if technical_analysis['strength'] == 'strong':
                strength_bonus = 0.1
            elif technical_analysis['strength'] == 'moderate':
                strength_bonus = 0.05
            
            confidence = max(0.2, min(0.95, base_confidence + session_bonus + strength_bonus))
            
            # Market sentiment (more realistic)
            market_sentiment = np.random.uniform(-0.3, 0.3)
            if signal_type == "BUY":
                news_sentiment = max(market_sentiment, 0) + np.random.uniform(0, 0.2)
            else:
                news_sentiment = min(market_sentiment, 0) - np.random.uniform(0, 0.2)
            
            return {
                'pair': pair,
                'signal_type': signal_type,
                'entry_price': price,
                'target_price': target_price,
                'stop_loss': stop_loss,
                'confidence': confidence,
                'pips_target': target_pips,
                'pips_risk': stop_pips,
                'technical_score': technical_score,
                'technical_signals': technical_analysis['signals'],
                'technical_strength': technical_analysis['strength'],
                'news_sentiment': news_sentiment,
                'session_name': session_name,
                'timestamp': timestamp,
                'reason': f"Tech: {technical_score:.2f} ({technical_analysis['strength']}), Session: {session_name}"
            }
            
        except Exception as e:
            logger.error(f"Error generating signal: {e}")
            return None
    
    def analyze_optimized_signal_quality(self, signal: Dict) -> Dict:
        """Optimized signal quality analysis with balanced filtering."""
        try:
            score = 0.0
            factors = []
            
            # 1. Technical strength (weighted more heavily)
            tech_strength = abs(signal['technical_score'])
            if tech_strength > 0.5:
                score += 0.25
                factors.append("Strong Technical")
            elif tech_strength > 0.3:
                score += 0.2
                factors.append("Good Technical")
            elif tech_strength > 0.2:
                score += 0.15
                factors.append("Moderate Technical")
            
            # 2. Technical signal count
            signal_count = len(signal['technical_signals'])
            if signal_count >= 3:
                score += 0.15
                factors.append("Multiple Signals")
            elif signal_count >= 2:
                score += 0.1
                factors.append("Dual Signals")
            
            # 3. Confidence level (more lenient)
            if signal['confidence'] > 0.75:
                score += 0.2
                factors.append("High Confidence")
            elif signal['confidence'] > 0.6:
                score += 0.15
                factors.append("Good Confidence")
            elif signal['confidence'] > 0.45:
                score += 0.1
                factors.append("Fair Confidence")
            
            # 4. Risk/Reward ratio
            risk_reward = signal['pips_target'] / signal['pips_risk']
            if risk_reward > 1.8:
                score += 0.15
                factors.append("Excellent R:R")
            elif risk_reward > 1.4:
                score += 0.12
                factors.append("Good R:R")
            elif risk_reward > 1.1:
                score += 0.08
                factors.append("Fair R:R")
            
            # 5. Session timing (enhanced)
            if signal['session_name'] == "London-NY Overlap":
                score += 0.12
                factors.append("Peak Session")
            elif signal['session_name'] in ["London Session", "NY Session"]:
                score += 0.08
                factors.append("Good Session")
            elif signal['session_name'] == "Asian Session":
                score += 0.04
                factors.append("Asian Session")
            
            # 6. Technical strength category
            if signal['technical_strength'] == 'strong':
                score += 0.1
                factors.append("Strong Setup")
            elif signal['technical_strength'] == 'moderate':
                score += 0.05
                factors.append("Moderate Setup")
            
            # 7. News sentiment alignment
            signal_direction = 1 if signal['signal_type'] == "BUY" else -1
            sentiment_direction = 1 if signal['news_sentiment'] > 0 else -1
            if signal_direction == sentiment_direction:
                score += 0.08
                factors.append("Sentiment Aligned")
            
            should_trade = score >= self.min_confidence
            
            return {
                'quality_score': score,
                'factors': factors,
                'should_trade': should_trade,
                'rejection_reason': None if should_trade else f"Quality score {score:.2f} < {self.min_confidence:.2f}"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing signal quality: {e}")
            return {'quality_score': 0.0, 'should_trade': False, 'rejection_reason': 'Analysis error'}
    
    def calculate_optimized_position_size(self, signal: Dict, quality_score: float) -> Dict:
        """Calculate optimized position size with better scaling."""
        try:
            # Base risk amount
            base_risk = self.current_balance * self.base_risk_pct
            
            # Quality multiplier (more aggressive for high quality)
            if quality_score > 0.7:
                quality_multiplier = 1.4
            elif quality_score > 0.6:
                quality_multiplier = 1.2
            elif quality_score > 0.5:
                quality_multiplier = 1.0
            else:
                quality_multiplier = 0.8
            
            # Session multiplier (enhanced)
            if signal['session_name'] == "London-NY Overlap":
                session_multiplier = 1.3
            elif signal['session_name'] in ["London Session", "NY Session"]:
                session_multiplier = 1.15
            elif signal['session_name'] == "Asian Session":
                session_multiplier = 1.0
            else:
                session_multiplier = 0.85
            
            # Technical strength multiplier
            if signal['technical_strength'] == 'strong':
                strength_multiplier = 1.2
            elif signal['technical_strength'] == 'moderate':
                strength_multiplier = 1.1
            else:
                strength_multiplier = 1.0
            
            # Compound growth multiplier
            growth_factor = self.current_balance / self.initial_balance
            compound_multiplier = min(growth_factor ** 0.5, 1.8)  # Square root scaling, capped at 1.8x
            
            # Final risk amount
            final_risk = base_risk * quality_multiplier * session_multiplier * strength_multiplier * compound_multiplier
            final_risk = max(15, min(final_risk, self.current_balance * 0.1))  # 10% max risk
            
            # Calculate units
            stop_distance_pips = signal['pips_risk']
            pip_value_usd = 0.10  # $0.10 per pip for 1000 units
            
            units = int(final_risk / (stop_distance_pips * pip_value_usd))
            units = max(1000, min(units, 150000))  # 1k to 150k units
            
            return {
                'units': units,
                'risk_amount': final_risk,
                'quality_multiplier': quality_multiplier,
                'session_multiplier': session_multiplier,
                'strength_multiplier': strength_multiplier,
                'compound_multiplier': compound_multiplier,
                'total_multiplier': quality_multiplier * session_multiplier * strength_multiplier * compound_multiplier
            }
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return {'units': 1000, 'risk_amount': 25.0}
    
    def simulate_optimized_trade(self, signal: Dict, position_info: Dict, future_data: pd.DataFrame) -> Dict:
        """Simulate trade with optimized exit strategy."""
        try:
            entry_price = signal['entry_price']
            target_price = signal['target_price']
            stop_loss = signal['stop_loss']
            units = position_info['units']
            
            # Track trade progress
            highest_favorable = entry_price
            current_stop = stop_loss
            partial_profits_taken = 0
            
            for i, (timestamp, row) in enumerate(future_data.iterrows()):
                current_price = row['Close']
                
                # Update highest favorable
                if signal['signal_type'] == "BUY":
                    if current_price > highest_favorable:
                        highest_favorable = current_price
                else:
                    if current_price < highest_favorable:
                        highest_favorable = current_price
                
                # Enhanced trailing stop logic
                if signal['signal_type'] == "BUY":
                    progress = (highest_favorable - entry_price) / (target_price - entry_price)
                    
                    # Partial profit taking
                    if progress > 0.6 and partial_profits_taken == 0:
                        # Take 30% profit at 60% to target
                        partial_profits_taken = 0.3
                        # Move stop to breakeven
                        current_stop = max(current_stop, entry_price)
                    elif progress > 0.4:
                        # Trailing stop at 40% progress
                        trail_distance = (highest_favorable - entry_price) * 0.4
                        new_stop = highest_favorable - trail_distance
                        current_stop = max(current_stop, new_stop)
                    elif progress > 0.25:
                        # Conservative trailing at 25% progress
                        trail_distance = (highest_favorable - entry_price) * 0.6
                        new_stop = highest_favorable - trail_distance
                        current_stop = max(current_stop, new_stop)
                        
                else:  # SELL
                    progress = (entry_price - highest_favorable) / (entry_price - target_price)
                    
                    if progress > 0.6 and partial_profits_taken == 0:
                        partial_profits_taken = 0.3
                        current_stop = min(current_stop, entry_price)
                    elif progress > 0.4:
                        trail_distance = (entry_price - highest_favorable) * 0.4
                        new_stop = highest_favorable + trail_distance
                        current_stop = min(current_stop, new_stop)
                    elif progress > 0.25:
                        trail_distance = (entry_price - highest_favorable) * 0.6
                        new_stop = highest_favorable + trail_distance
                        current_stop = min(current_stop, new_stop)
                
                # Check exit conditions
                if signal['signal_type'] == "BUY":
                    if current_price <= current_stop:
                        # Stop loss hit
                        profit_pips = (current_stop - entry_price) / (0.01 if 'JPY' in signal['pair'] else 0.0001)
                        profit_usd = profit_pips * 0.10 * (units / 1000) * (1 - partial_profits_taken)
                        
                        # Add partial profits if any
                        if partial_profits_taken > 0:
                            partial_pips = (highest_favorable - entry_price) / (0.01 if 'JPY' in signal['pair'] else 0.0001)
                            profit_usd += partial_pips * 0.10 * (units / 1000) * partial_profits_taken
                        
                        return {
                            'outcome': 'STOP_LOSS',
                            'exit_price': current_stop,
                            'profit_pips': profit_pips,
                            'profit_usd': profit_usd,
                            'hold_hours': i + 1,
                            'partial_profits': partial_profits_taken
                        }
                        
                    elif current_price >= target_price:
                        # Target hit
                        profit_pips = (target_price - entry_price) / (0.01 if 'JPY' in signal['pair'] else 0.0001)
                        profit_usd = profit_pips * 0.10 * (units / 1000)
                        
                        return {
                            'outcome': 'TARGET_HIT',
                            'exit_price': target_price,
                            'profit_pips': profit_pips,
                            'profit_usd': profit_usd,
                            'hold_hours': i + 1,
                            'partial_profits': partial_profits_taken
                        }
                        
                else:  # SELL
                    if current_price >= current_stop:
                        profit_pips = (entry_price - current_stop) / (0.01 if 'JPY' in signal['pair'] else 0.0001)
                        profit_usd = profit_pips * 0.10 * (units / 1000) * (1 - partial_profits_taken)
                        
                        if partial_profits_taken > 0:
                            partial_pips = (entry_price - highest_favorable) / (0.01 if 'JPY' in signal['pair'] else 0.0001)
                            profit_usd += partial_pips * 0.10 * (units / 1000) * partial_profits_taken
                        
                        return {
                            'outcome': 'STOP_LOSS',
                            'exit_price': current_stop,
                            'profit_pips': profit_pips,
                            'profit_usd': profit_usd,
                            'hold_hours': i + 1,
                            'partial_profits': partial_profits_taken
                        }
                        
                    elif current_price <= target_price:
                        profit_pips = (entry_price - target_price) / (0.01 if 'JPY' in signal['pair'] else 0.0001)
                        profit_usd = profit_pips * 0.10 * (units / 1000)
                        
                        return {
                            'outcome': 'TARGET_HIT',
                            'exit_price': target_price,
                            'profit_pips': profit_pips,
                            'profit_usd': profit_usd,
                            'hold_hours': i + 1,
                            'partial_profits': partial_profits_taken
                        }
                
                # Timeout after 72 hours (extended)
                if i >= 72:
                    if signal['signal_type'] == "BUY":
                        profit_pips = (current_price - entry_price) / (0.01 if 'JPY' in signal['pair'] else 0.0001)
                    else:
                        profit_pips = (entry_price - current_price) / (0.01 if 'JPY' in signal['pair'] else 0.0001)
                    
                    profit_usd = profit_pips * 0.10 * (units / 1000) * (1 - partial_profits_taken)
                    
                    if partial_profits_taken > 0:
                        if signal['signal_type'] == "BUY":
                            partial_pips = (highest_favorable - entry_price) / (0.01 if 'JPY' in signal['pair'] else 0.0001)
                        else:
                            partial_pips = (entry_price - highest_favorable) / (0.01 if 'JPY' in signal['pair'] else 0.0001)
                        profit_usd += partial_pips * 0.10 * (units / 1000) * partial_profits_taken
                    
                    return {
                        'outcome': 'TIMEOUT',
                        'exit_price': current_price,
                        'profit_pips': profit_pips,
                        'profit_usd': profit_usd,
                        'hold_hours': 72,
                        'partial_profits': partial_profits_taken
                    }
            
            return {'outcome': 'NO_EXIT', 'reason': 'End of data'}
            
        except Exception as e:
            logger.error(f"Error simulating trade: {e}")
            return {'outcome': 'ERROR', 'reason': str(e)}
    
    def run_optimized_backtest(self, pairs: List[str], start_date: datetime, end_date: datetime) -> Dict:
        """Run the optimized backtest."""
        try:
            logger.info(f"🎯 Starting optimized backtest: {start_date} to {end_date}")
            
            # Get data for all pairs
            pair_data = {}
            for pair in pairs:
                data = self.get_forex_data(pair, start_date, end_date)
                if not data.empty:
                    pair_data[pair] = data
            
            if not pair_data:
                return {'error': 'No data retrieved'}
            
            # Generate scan times (every 4 hours for more opportunities)
            scan_times = []
            current_time = start_date
            while current_time <= end_date:
                scan_times.append(current_time)
                current_time += timedelta(hours=4)  # More frequent scanning
            
            logger.info(f"📅 Generated {len(scan_times)} scan times")
            
            # Process each scan time
            for scan_time in scan_times:
                for pair in pairs:
                    if pair not in pair_data:
                        continue
                    
                    try:
                        data = pair_data[pair]
                        
                        # Get data up to scan time
                        scan_data = data[data.index <= scan_time]
                        if len(scan_data) < 50:
                            continue
                        
                        current_price = scan_data['Close'].iloc[-1]
                        
                        # Enhanced technical analysis
                        technical_analysis = self.calculate_enhanced_technical_score(scan_data)
                        
                        # Generate optimized signal
                        signal = self.generate_optimized_signal(pair, current_price, technical_analysis, scan_time)
                        
                        if signal:
                            self.all_signals.append(signal)
                            
                            # Analyze quality with optimized thresholds
                            quality_analysis = self.analyze_optimized_signal_quality(signal)
                            
                            if quality_analysis['should_trade']:
                                # Check position limits
                                if len([t for t in self.executed_trades if t['trade_result']['outcome'] not in ['TARGET_HIT', 'STOP_LOSS', 'TIMEOUT']]) >= self.max_concurrent_positions:
                                    self.rejected_signals.append({
                                        'signal': signal,
                                        'reason': 'Max concurrent positions reached'
                                    })
                                    continue
                                
                                # Calculate optimized position size
                                position_info = self.calculate_optimized_position_size(signal, quality_analysis['quality_score'])
                                
                                # Get future data for simulation
                                future_data = data[data.index > scan_time].head(80)  # More data for longer trades
                                
                                if len(future_data) > 0:
                                    # Simulate trade
                                    trade_result = self.simulate_optimized_trade(signal, position_info, future_data)
                                    
                                    if trade_result['outcome'] not in ['NO_EXIT', 'ERROR']:
                                        # Record trade
                                        trade_record = {
                                            'signal': signal,
                                            'quality_analysis': quality_analysis,
                                            'position_info': position_info,
                                            'trade_result': trade_result
                                        }
                                        
                                        self.executed_trades.append(trade_record)
                                        self.filtered_signals.append(signal)
                                        
                                        # Update balance
                                        self.current_balance += trade_result['profit_usd']
                                        
                                        outcome = 'WIN' if trade_result['profit_usd'] > 0 else 'LOSS'
                                        logger.info(f"✅ {pair} {signal['signal_type']} → {outcome} ${trade_result['profit_usd']:.2f} "
                                                  f"(Quality: {quality_analysis['quality_score']:.2f})")
                                
                            else:
                                self.rejected_signals.append({
                                    'signal': signal,
                                    'reason': quality_analysis['rejection_reason']
                                })
                    
                    except Exception as e:
                        logger.error(f"Error processing {pair} at {scan_time}: {e}")
                        continue
            
            # Calculate results
            results = self.calculate_results()
            logger.info("🎯 Optimized backtest completed successfully")
            
            return results
            
        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            return {'error': str(e)}
    
    def calculate_results(self) -> Dict:
        """Calculate comprehensive backtest results."""
        try:
            if not self.executed_trades:
                return {'total_trades': 0, 'error': 'No trades executed'}
            
            total_trades = len(self.executed_trades)
            winning_trades = [t for t in self.executed_trades if t['trade_result']['profit_usd'] > 0]
            losing_trades = [t for t in self.executed_trades if t['trade_result']['profit_usd'] < 0]
            
            win_rate = len(winning_trades) / total_trades
            total_profit = sum(t['trade_result']['profit_usd'] for t in self.executed_trades)
            total_return = ((self.current_balance / self.initial_balance) - 1) * 100
            
            avg_win = np.mean([t['trade_result']['profit_usd'] for t in winning_trades]) if winning_trades else 0
            avg_loss = np.mean([t['trade_result']['profit_usd'] for t in losing_trades]) if losing_trades else 0
            
            profit_factor = abs(avg_win * len(winning_trades) / (avg_loss * len(losing_trades))) if losing_trades else float('inf')
            
            avg_hold_time = np.mean([t['trade_result']['hold_hours'] for t in self.executed_trades])
            
            # Pair performance
            pair_performance = {}
            for trade in self.executed_trades:
                pair = trade['signal']['pair']
                if pair not in pair_performance:
                    pair_performance[pair] = {'trades': 0, 'wins': 0, 'profit': 0, 'pips': 0}
                
                pair_performance[pair]['trades'] += 1
                pair_performance[pair]['profit'] += trade['trade_result']['profit_usd']
                pair_performance[pair]['pips'] += trade['trade_result']['profit_pips']
                
                if trade['trade_result']['profit_usd'] > 0:
                    pair_performance[pair]['wins'] += 1
            
            for pair in pair_performance:
                pair_performance[pair]['win_rate'] = pair_performance[pair]['wins'] / pair_performance[pair]['trades']
            
            return {
                'total_trades': total_trades,
                'winning_trades': len(winning_trades),
                'losing_trades': len(losing_trades),
                'win_rate': win_rate,
                'total_profit': total_profit,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'profit_factor': profit_factor,
                'initial_balance': self.initial_balance,
                'final_balance': self.current_balance,
                'total_return': total_return,
                'avg_hold_time': avg_hold_time,
                'pair_performance': pair_performance,
                'all_signals_count': len(self.all_signals),
                'filtered_signals_count': len(self.filtered_signals),
                'rejected_signals_count': len(self.rejected_signals),
                'signal_filter_rate': len(self.filtered_signals) / len(self.all_signals) if self.all_signals else 0,
                'executed_trades': self.executed_trades,
                'compound_metrics': {
                    'performance_rating': 'excellent' if win_rate > 0.7 else 'good' if win_rate > 0.6 else 'average'
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating results: {e}")
            return {'error': str(e)}

def run_optimized_backtest():
    """Run the optimized backtest."""
    try:
        backtest = OptimizedAdvancedBacktest(initial_balance=1000)
        
        pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD']
        start_date = datetime(2024, 12, 1)
        end_date = datetime(2024, 12, 15)
        
        results = backtest.run_optimized_backtest(pairs, start_date, end_date)
        return results
        
    except Exception as e:
        logger.error(f"Error in backtest: {e}")
        return {'error': str(e)}

if __name__ == "__main__":
    print("🎯 OPTIMIZED ADVANCED TRADING SYSTEM BACKTEST")
    print("=" * 60)
    
    results = run_optimized_backtest()
    
    if 'error' in results:
        print(f"❌ Error: {results['error']}")
    else:
        print(f"📊 Total Trades: {results['total_trades']}")
        print(f"🎯 Win Rate: {results['win_rate']:.1%}")
        print(f"💰 Total Profit: ${results['total_profit']:.2f}")
        print(f"📈 Total Return: {results['total_return']:.1f}%")
        print(f"⚡ Profit Factor: {results['profit_factor']:.2f}")
        print(f"🔍 Signal Filter Rate: {results['signal_filter_rate']:.1%}") 