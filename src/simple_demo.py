#!/usr/bin/env python3
"""
Simple Demo of Sniper Bot Core Functionality
This script demonstrates the basic components without heavy ML dependencies.
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta
from data_generator import NewsDataGenerator

class SimpleSniperBot:
    """Simplified version of the Sniper Bot for demonstration."""
    
    def __init__(self):
        self.sp500_tickers = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM',
            'V', 'PG', 'HD', 'MA', 'DIS', 'PYPL', 'BAC', 'ADBE', 'CRM', 'NFLX'
        ]
        
        self.event_weights = {
            'earnings': 2.0,
            'merger': 2.0,
            'acquisition': 2.0,
            'product launch': 2.0,
            'executive': 1.5,
            'partnership': 1.3,
            'default': 1.0
        }
        
        self.source_weights = {
            'bloomberg': 1.5,
            'wsj': 1.5,
            'reuters': 1.4,
            'cnbc': 1.3,
            'marketwatch': 1.2,
            'default': 1.0
        }
    
    def extract_tickers(self, headline):
        """Extract ticker symbols from headline."""
        ticker_pattern = r'\b[A-Z]{1,5}\b'
        potential_tickers = re.findall(ticker_pattern, headline)
        return [t for t in potential_tickers if t in self.sp500_tickers]
    
    def simple_sentiment_analysis(self, text):
        """Simple rule-based sentiment analysis."""
        positive_words = [
            'beat', 'beats', 'strong', 'growth', 'record', 'announce', 'launch',
            'partnership', 'acquisition', 'upgrade', 'buyback', 'breakthrough'
        ]
        
        negative_words = [
            'miss', 'misses', 'decline', 'disappointing', 'lawsuit', 'resign',
            'layoffs', 'downgrade', 'disruption', 'loses', 'scandal'
        ]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 0.7  # Positive
        elif negative_count > positive_count:
            return -0.7  # Negative
        else:
            return 0.0  # Neutral
    
    def get_event_weight(self, headline):
        """Get event type weight."""
        headline_lower = headline.lower()
        for event_type, weight in self.event_weights.items():
            if event_type in headline_lower:
                return weight
        return self.event_weights['default']
    
    def get_source_weight(self, source):
        """Get source weight."""
        source_lower = source.lower()
        for source_name, weight in self.source_weights.items():
            if source_name in source_lower:
                return weight
        return self.source_weights['default']
    
    def calculate_confidence_score(self, sentiment_score, headline, source):
        """Calculate confidence score."""
        event_weight = self.get_event_weight(headline)
        source_weight = self.get_source_weight(source)
        return abs(sentiment_score) * event_weight * source_weight
    
    def filter_event_driven_news(self, df):
        """Filter for event-driven news."""
        event_keywords = [
            'earnings', 'quarterly', 'revenue', 'profit', 'merger', 'acquisition',
            'launch', 'announce', 'ceo', 'cfo', 'executive', 'partnership'
        ]
        
        pattern = '|'.join(event_keywords)
        mask = df['headline'].str.contains(pattern, case=False, na=False)
        return df[mask].copy()
    
    def analyze_news(self, news_df, confidence_threshold=0.6):
        """Analyze news and generate trade signals."""
        # Filter for event-driven news
        filtered_df = self.filter_event_driven_news(news_df)
        print(f"📰 Filtered to {len(filtered_df)} event-driven articles")
        
        trade_signals = []
        
        for _, row in filtered_df.iterrows():
            headline = row['headline']
            date = row['date']
            source = row['source']
            
            # Extract tickers
            tickers = self.extract_tickers(headline)
            if not tickers:
                continue
            
            # Analyze sentiment
            sentiment_score = self.simple_sentiment_analysis(headline)
            
            # Calculate confidence
            confidence_score = self.calculate_confidence_score(sentiment_score, headline, source)
            
            # Generate signal if confidence is high enough
            if confidence_score >= confidence_threshold:
                for ticker in tickers:
                    signal = {
                        'date': date,
                        'ticker': ticker,
                        'headline': headline,
                        'source': source,
                        'sentiment_score': sentiment_score,
                        'confidence_score': confidence_score,
                        'signal': 'BUY' if sentiment_score > 0 else 'SELL'
                    }
                    trade_signals.append(signal)
        
        return pd.DataFrame(trade_signals)

def main():
    print("🎯 Simple Sniper Bot Demo")
    print("=" * 50)
    
    # Step 1: Generate sample data
    print("\n1️⃣ Generating sample news data...")
    generator = NewsDataGenerator()
    news_df = generator.generate_sample_data(num_articles=100)
    print(f"✅ Generated {len(news_df)} news articles")
    
    # Show sample headlines
    print("\n📰 Sample Headlines:")
    for _, row in news_df.head(5).iterrows():
        print(f"  • {row['headline']}")
    
    # Step 2: Initialize simple bot
    print("\n2️⃣ Initializing Simple Sniper Bot...")
    bot = SimpleSniperBot()
    print("✅ Bot initialized")
    
    # Step 3: Analyze news
    print("\n3️⃣ Analyzing news for trading signals...")
    signals_df = bot.analyze_news(news_df, confidence_threshold=0.5)
    
    if signals_df.empty:
        print("⚠️ No trading signals generated. Try lowering the confidence threshold.")
        return
    
    # Step 4: Display results
    print(f"\n4️⃣ Generated {len(signals_df)} trading signals:")
    print("-" * 50)
    
    # Group by signal type
    buy_signals = signals_df[signals_df['signal'] == 'BUY']
    sell_signals = signals_df[signals_df['signal'] == 'SELL']
    
    print(f"📈 BUY signals: {len(buy_signals)}")
    print(f"📉 SELL signals: {len(sell_signals)}")
    
    # Show top signals
    print(f"\n🏆 Top 5 Highest Confidence Signals:")
    top_signals = signals_df.nlargest(5, 'confidence_score')
    for _, signal in top_signals.iterrows():
        print(f"  {signal['signal']} {signal['ticker']} | Confidence: {signal['confidence_score']:.3f} | {signal['date']}")
    
    # Show signal distribution by ticker
    print(f"\n📊 Signals by Ticker:")
    ticker_counts = signals_df['ticker'].value_counts().head(10)
    for ticker, count in ticker_counts.items():
        print(f"  {ticker}: {count} signals")
    
    # Save results
    output_path = 'data/simple_signals.csv'
    signals_df.to_csv(output_path, index=False)
    print(f"\n💾 Signals saved to: {output_path}")
    
    print("\n✨ Simple demo completed!")
    print("💡 This demonstrates the core logic without heavy ML dependencies.")
    print("🚀 For full functionality with FinBERT and backtesting, use the complete version.")

if __name__ == "__main__":
    main() 