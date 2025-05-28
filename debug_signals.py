#!/usr/bin/env python3
"""
Debug the exact signal generation process step by step.
"""

import os
import sys
sys.path.append('src')

from enhanced_sniper_bot import EnhancedSniperBot
import pandas as pd

def debug_signal_generation():
    """Debug the signal generation process step by step."""
    print("🔧 DEBUGGING: Signal Generation Process")
    print("=" * 50)
    
    # Set API keys
    os.environ['POLYGON_API_KEY'] = "rwd4Vdja4BxDutJIoulw9K40r7Qf8xdE"
    os.environ['ALPHA_VANTAGE_API_KEY'] = "PITRBDQSWC2015J1"
    
    bot = EnhancedSniperBot(initial_capital=5000, max_daily_trades=5)
    
    # Get news data directly
    print("1. Getting news data...")
    news_data = bot.news_manager.get_aggregated_news(['AAPL', 'TSLA', 'NVDA', 'GOOGL', 'MSFT'], limit=50)
    print(f"   Retrieved: {len(news_data)} articles")
    
    if news_data.empty:
        print("   ❌ No news data - this is the problem!")
        return
    
    print("\n2. Processing each article...")
    signals_created = []
    
    for i, (_, article) in enumerate(news_data.head(10).iterrows(), 1):
        print(f"\n   Article {i}: {article['headline'][:60]}...")
        
        # Extract tickers
        tickers = bot.extract_tickers(article['headline'])
        print(f"   Tickers found: {tickers}")
        
        if not tickers:
            print("   ❌ No tickers found - skipping")
            continue
        
        # Analyze sentiment
        sentiment = bot.analyze_sentiment(article['headline'])
        print(f"   Sentiment: {sentiment:.3f}")
        
        # Calculate confidence
        confidence = bot.calculate_confidence_score(sentiment, article['headline'], article['source'])
        print(f"   Confidence: {confidence:.3f}")
        
        # Check if meets threshold
        threshold = 0.1
        if confidence >= threshold:
            print(f"   ✅ Meets threshold {threshold}")
            
            for ticker in tickers:
                signal_type = "BUY" if sentiment > 0 else "SELL"
                print(f"   📈 Would create {signal_type} signal for {ticker}")
                signals_created.append((ticker, signal_type, confidence, sentiment))
        else:
            print(f"   ❌ Below threshold {threshold}")
    
    print(f"\n📊 RESULTS:")
    print(f"   Total signals that would be created: {len(signals_created)}")
    
    if signals_created:
        print("   Signals:")
        for ticker, signal_type, confidence, sentiment in signals_created:
            print(f"   - {ticker}: {signal_type} (confidence: {confidence:.3f}, sentiment: {sentiment:.3f})")
    
    # Test the actual generate_daily_signals method
    print(f"\n3. Testing actual generate_daily_signals method...")
    actual_signals = bot.generate_daily_signals(confidence_threshold=0.1)
    print(f"   Actual signals generated: {len(actual_signals)}")
    
    return signals_created, actual_signals

if __name__ == "__main__":
    debug_signal_generation() 