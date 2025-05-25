#!/usr/bin/env python3
"""
Test API timing and date ranges to see why real-time vs cached data differs.
"""

import os
import sys
sys.path.append('src')

from enhanced_sniper_bot import NewsAPIManager, EnhancedSniperBot
import pandas as pd
from datetime import datetime, timedelta

def test_api_timing():
    """Test different time ranges and API call patterns."""
    print("🕐 TESTING: API Timing and Date Ranges")
    print("=" * 60)
    
    # Set API keys
    os.environ['POLYGON_API_KEY'] = "rwd4Vdja4BxDutJIoulw9K40r7Qf8xdE"
    os.environ['ALPHA_VANTAGE_API_KEY'] = "PITRBDQSWC2015J1"
    
    news_manager = NewsAPIManager()
    
    print("1. Testing Alpha Vantage with different limits...")
    for limit in [10, 50, 100]:
        alpha_news = news_manager.get_news_from_alpha_vantage(['AAPL', 'TSLA', 'NVDA'], limit=limit)
        print(f"   Limit {limit}: {len(alpha_news)} articles")
        
        if alpha_news:
            # Check date range
            dates = [item.get('date', '') for item in alpha_news if item.get('date')]
            if dates:
                print(f"   Date range: {min(dates)} to {max(dates)}")
            
            # Show sample headlines with dates
            print("   Recent headlines:")
            for i, item in enumerate(alpha_news[:3], 1):
                print(f"   {i}. {item.get('headline', '')[:60]}...")
                print(f"      Date: {item.get('date', 'N/A')}")
        print()
    
    print("2. Testing aggregated news with different ticker sets...")
    
    # Test 1: High-profile tickers
    print("   High-profile tickers (AAPL, TSLA, NVDA):")
    news1 = news_manager.get_aggregated_news(['AAPL', 'TSLA', 'NVDA'], limit=50)
    print(f"   Retrieved: {len(news1)} articles")
    
    # Test 2: Broader tech tickers
    print("   Broader tech tickers:")
    tech_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX']
    news2 = news_manager.get_aggregated_news(tech_tickers, limit=50)
    print(f"   Retrieved: {len(news2)} articles")
    
    # Test 3: No specific tickers (general market news)
    print("   General market news (no specific tickers):")
    news3 = news_manager.get_aggregated_news(None, limit=50)
    print(f"   Retrieved: {len(news3)} articles")
    
    # Analyze the best dataset
    best_news = news1 if len(news1) > len(news2) else news2
    if len(news3) > len(best_news):
        best_news = news3
    
    print(f"\n3. Analyzing best dataset ({len(best_news)} articles)...")
    
    if not best_news.empty:
        # Check date distribution
        now = datetime.now()
        today = now.date()
        yesterday = today - timedelta(days=1)
        
        today_count = len(best_news[best_news['date'].dt.date == today])
        yesterday_count = len(best_news[best_news['date'].dt.date == yesterday])
        older_count = len(best_news[best_news['date'].dt.date < yesterday])
        
        print(f"   Today: {today_count} articles")
        print(f"   Yesterday: {yesterday_count} articles") 
        print(f"   Older: {older_count} articles")
        
        # Test signal generation on this dataset
        print(f"\n4. Testing signal generation on best dataset...")
        bot = EnhancedSniperBot(initial_capital=5000, max_daily_trades=5)
        
        # Manually process the news data
        signals_found = []
        for _, row in best_news.head(20).iterrows():
            headline = row.get('headline', '')
            source = row.get('source', '')
            
            # Extract tickers
            tickers = bot.extract_tickers(headline)
            if not tickers:
                continue
                
            # Analyze sentiment
            sentiment = bot.analyze_sentiment(headline)
            if abs(sentiment) < 0.1:
                continue
                
            # Calculate confidence
            confidence = bot.calculate_confidence_score(sentiment, headline, source)
            
            if confidence >= 0.1:  # Low threshold
                for ticker in tickers:
                    signal_type = "BUY" if sentiment > 0 else "SELL"
                    signals_found.append({
                        'ticker': ticker,
                        'type': signal_type,
                        'confidence': confidence,
                        'sentiment': sentiment,
                        'headline': headline[:60] + "...",
                        'date': row['date']
                    })
        
        print(f"   Manual processing found: {len(signals_found)} potential signals")
        
        if signals_found:
            print("   Top signals:")
            for i, signal in enumerate(signals_found[:5], 1):
                print(f"   {i}. {signal['ticker']} {signal['type']} (conf: {signal['confidence']:.3f})")
                print(f"      {signal['headline']}")
                print(f"      Date: {signal['date']}")
                print()
        
        # Now test the actual bot method
        print("5. Testing bot.generate_daily_signals()...")
        actual_signals = bot.generate_daily_signals(confidence_threshold=0.1)
        print(f"   Bot generated: {len(actual_signals)} signals")
        
        if actual_signals:
            for signal in actual_signals:
                print(f"   - {signal.ticker} {signal.signal_type} (conf: {signal.confidence_score:.3f})")
    
    return best_news, signals_found

if __name__ == "__main__":
    test_api_timing() 