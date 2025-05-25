#!/usr/bin/env python3
"""
Quick diagnostic to see what's happening with the APIs and signal generation.
"""

import os
import sys
sys.path.append('src')

from enhanced_sniper_bot import NewsAPIManager, EnhancedSniperBot
import pandas as pd

def test_news_apis():
    """Test what news data we're actually getting."""
    print("🔍 DIAGNOSTIC: Testing News APIs")
    print("=" * 50)
    
    # Set API keys
    os.environ['POLYGON_API_KEY'] = "rwd4Vdja4BxDutJIoulw9K40r7Qf8xdE"
    os.environ['ALPHA_VANTAGE_API_KEY'] = "PITRBDQSWC2015J1"
    
    news_manager = NewsAPIManager()
    
    print("1. Testing Alpha Vantage...")
    alpha_news = news_manager.get_news_from_alpha_vantage(['AAPL', 'TSLA'], limit=10)
    print(f"   Retrieved: {len(alpha_news)} articles")
    
    if alpha_news:
        print("   Sample headlines:")
        for i, article in enumerate(alpha_news[:3], 1):
            print(f"   {i}. {article['headline'][:80]}...")
            print(f"      Sentiment: {article.get('sentiment_score', 'N/A')}")
    
    print("\n2. Testing Polygon.io...")
    polygon_news = news_manager.get_news_from_polygon('AAPL', limit=10)
    print(f"   Retrieved: {len(polygon_news)} articles")
    
    if polygon_news:
        print("   Sample headlines:")
        for i, article in enumerate(polygon_news[:3], 1):
            print(f"   {i}. {article['headline'][:80]}...")
    
    print("\n3. Testing aggregated news...")
    aggregated = news_manager.get_aggregated_news(['AAPL', 'TSLA', 'NVDA'], limit=20)
    print(f"   Total aggregated: {len(aggregated)} articles")
    
    if not aggregated.empty:
        print("   Recent headlines:")
        for i, (_, row) in enumerate(aggregated.head(5).iterrows(), 1):
            print(f"   {i}. {row['headline'][:80]}...")
            print(f"      Date: {row['date']} | Source: {row['source']}")
    
    return aggregated

def test_signal_generation_detailed():
    """Test signal generation with detailed output."""
    print("\n🎯 DIAGNOSTIC: Signal Generation Process")
    print("=" * 50)
    
    bot = EnhancedSniperBot(initial_capital=5000, max_daily_trades=5)
    
    # Test with very low confidence threshold
    print("Testing with confidence threshold 0.1 (very low)...")
    signals_low = bot.generate_daily_signals(confidence_threshold=0.1)
    print(f"Signals generated (0.1 threshold): {len(signals_low)}")
    
    # Test with medium threshold
    print("\nTesting with confidence threshold 0.5 (medium)...")
    signals_med = bot.generate_daily_signals(confidence_threshold=0.5)
    print(f"Signals generated (0.5 threshold): {len(signals_med)}")
    
    # Test with high threshold
    print("\nTesting with confidence threshold 0.8 (high)...")
    signals_high = bot.generate_daily_signals(confidence_threshold=0.8)
    print(f"Signals generated (0.8 threshold): {len(signals_high)}")
    
    if signals_low:
        print(f"\n📊 Sample signals (threshold 0.1):")
        for i, signal in enumerate(signals_low[:3], 1):
            print(f"{i}. {signal.ticker} {signal.signal_type}")
            print(f"   Confidence: {signal.confidence_score:.3f}")
            print(f"   Sentiment: {signal.sentiment_score:.3f}")
            print(f"   Headline: {signal.headline[:60]}...")
            print(f"   Source: {signal.source}")
            print()
    
    return signals_low

def test_manual_signal_creation():
    """Test creating signals manually to see if the logic works."""
    print("\n🧪 DIAGNOSTIC: Manual Signal Creation Test")
    print("=" * 50)
    
    bot = EnhancedSniperBot()
    
    # Test sentiment analysis
    test_headlines = [
        "Apple reports record quarterly earnings, beats expectations",
        "Tesla stock plunges after disappointing delivery numbers",
        "NVIDIA announces breakthrough AI chip technology",
        "Microsoft faces major security breach concerns",
        "Amazon Prime Day sales exceed all previous records"
    ]
    
    print("Testing sentiment analysis:")
    for headline in test_headlines:
        sentiment = bot.analyze_sentiment(headline)
        event_weight = bot.get_event_weight(headline)
        source_weight = bot.get_source_weight("Reuters")
        confidence = bot.calculate_confidence_score(sentiment, headline, "Reuters")
        
        print(f"Headline: {headline[:50]}...")
        print(f"  Sentiment: {sentiment:.3f} | Event Weight: {event_weight:.1f} | Confidence: {confidence:.3f}")
        print()

if __name__ == "__main__":
    print("🚀 QUICK DIAGNOSTIC: API & Signal Generation Test")
    print("=" * 60)
    
    # Test 1: News APIs
    news_data = test_news_apis()
    
    # Test 2: Signal generation
    signals = test_signal_generation_detailed()
    
    # Test 3: Manual testing
    test_manual_signal_creation()
    
    print("\n📋 SUMMARY:")
    print(f"- News articles retrieved: {len(news_data) if not news_data.empty else 0}")
    print(f"- Signals generated (low threshold): {len(signals) if signals else 0}")
    print("\n💡 RECOMMENDATIONS:")
    if not news_data.empty and not signals:
        print("- APIs working but no signals generated")
        print("- Try lowering confidence threshold to 0.1-0.3")
        print("- Check if sentiment analysis is working correctly")
    elif news_data.empty:
        print("- No news data retrieved - API issue")
        print("- Check API keys and rate limits")
    else:
        print("- System working correctly!") 