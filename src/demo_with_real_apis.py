#!/usr/bin/env python3
"""
Demo script showing the Enhanced Sniper Bot with real news APIs
This demonstrates the full pipeline from news fetching to signal generation.
"""

import os
import sys
import time
from datetime import datetime, timedelta

# Add src directory to path
sys.path.append(os.path.dirname(__file__))

from enhanced_sniper_bot import EnhancedSniperBot, NewsAPIManager
import pandas as pd

def setup_demo_environment():
    """Setup demo environment with sample API keys if none exist."""
    print("🔧 Setting up demo environment...")
    
    # Check for existing API keys
    apis_configured = []
    
    if os.getenv('ALPHA_VANTAGE_API_KEY'):
        apis_configured.append('Alpha Vantage')
    
    if os.getenv('POLYGON_API_KEY'):
        apis_configured.append('Polygon.io')
    
    if os.getenv('STOCK_NEWS_API_KEY'):
        apis_configured.append('Stock News API')
    
    if apis_configured:
        print(f"✅ Found API keys for: {', '.join(apis_configured)}")
    else:
        print("⚠️ No API keys found. Using demo mode.")
        print("\n📝 To use real APIs, set these environment variables:")
        print("   export ALPHA_VANTAGE_API_KEY='your_key_here'")
        print("   export POLYGON_API_KEY='your_key_here'")
        print("   export STOCK_NEWS_API_KEY='your_key_here'")
    
    return len(apis_configured) > 0

def demo_news_fetching():
    """Demonstrate news fetching from multiple APIs."""
    print("\n" + "="*60)
    print("📰 DEMO: News Fetching from Multiple APIs")
    print("="*60)
    
    news_manager = NewsAPIManager()
    
    # Test each API
    print("\n1️⃣ Testing Alpha Vantage API...")
    alpha_news = news_manager.get_news_from_alpha_vantage(['AAPL', 'TSLA', 'GOOGL'], limit=5)
    print(f"   Retrieved {len(alpha_news)} articles from Alpha Vantage")
    
    print("\n2️⃣ Testing Polygon.io API...")
    polygon_news = news_manager.get_news_from_polygon('AAPL', limit=5)
    print(f"   Retrieved {len(polygon_news)} articles from Polygon.io")
    
    print("\n3️⃣ Testing Stock News API...")
    stock_news = news_manager.get_news_from_stock_news_api(['AAPL', 'MSFT'], limit=5)
    print(f"   Retrieved {len(stock_news)} articles from Stock News API")
    
    # Aggregate all news
    print("\n4️⃣ Aggregating news from all sources...")
    aggregated_news = news_manager.get_aggregated_news(['AAPL', 'TSLA', 'MSFT'], limit=20)
    
    if not aggregated_news.empty:
        print(f"   📊 Total aggregated articles: {len(aggregated_news)}")
        print("\n📋 Sample headlines:")
        for i, row in aggregated_news.head(3).iterrows():
            print(f"   • {row['headline'][:80]}...")
            print(f"     Source: {row['source']} | Date: {row['date'].strftime('%Y-%m-%d %H:%M')}")
        
        return aggregated_news
    else:
        print("   ⚠️ No news data retrieved (likely due to missing API keys)")
        return pd.DataFrame()

def demo_signal_generation():
    """Demonstrate signal generation from real news."""
    print("\n" + "="*60)
    print("🎯 DEMO: Trading Signal Generation")
    print("="*60)
    
    # Initialize enhanced bot
    bot = EnhancedSniperBot(initial_capital=5000, max_daily_trades=5)
    
    print("\n🔍 Generating signals from real-time news...")
    try:
        signals = bot.generate_daily_signals(confidence_threshold=0.6)  # Lower threshold for demo
        
        if signals:
            print(f"✅ Generated {len(signals)} trading signals!")
            
            print("\n📊 Signal Summary:")
            buy_signals = [s for s in signals if s.signal_type == 'BUY']
            sell_signals = [s for s in signals if s.signal_type == 'SELL']
            
            print(f"   📈 BUY signals: {len(buy_signals)}")
            print(f"   📉 SELL signals: {len(sell_signals)}")
            
            avg_confidence = sum(s.confidence_score for s in signals) / len(signals)
            print(f"   🎯 Average confidence: {avg_confidence:.2f}")
            
            print("\n🏆 Top 3 Signals:")
            for i, signal in enumerate(signals[:3], 1):
                print(f"\n   {i}. {signal.ticker} - {signal.signal_type}")
                print(f"      💰 Entry: ${signal.entry_price:.2f}")
                print(f"      🎯 Target: ${signal.target_price:.2f}")
                print(f"      🛡️ Stop Loss: ${signal.stop_loss:.2f}")
                print(f"      📊 Confidence: {signal.confidence_score:.2f}")
                print(f"      📰 News: {signal.headline[:60]}...")
                
                # Calculate potential return
                if signal.signal_type == 'BUY':
                    potential_return = ((signal.target_price - signal.entry_price) / signal.entry_price) * 100
                else:
                    potential_return = ((signal.entry_price - signal.target_price) / signal.entry_price) * 100
                print(f"      💹 Potential Return: {potential_return:.1f}%")
            
            return signals
        else:
            print("⚠️ No signals generated. This could be due to:")
            print("   • No recent high-impact news")
            print("   • Confidence threshold too high")
            print("   • API rate limits or missing keys")
            return []
            
    except Exception as e:
        print(f"❌ Error generating signals: {e}")
        return []

def demo_signal_management():
    """Demonstrate signal management and database operations."""
    print("\n" + "="*60)
    print("💾 DEMO: Signal Management & Database")
    print("="*60)
    
    bot = EnhancedSniperBot()
    
    # Get active signals from database
    active_signals = bot.signal_db.get_active_signals()
    print(f"\n📊 Active signals in database: {len(active_signals)}")
    
    if active_signals:
        print("\n🎯 Active Signals:")
        for signal in active_signals[:3]:  # Show first 3
            print(f"   • {signal.ticker} {signal.signal_type} - Confidence: {signal.confidence_score:.2f}")
            print(f"     Created: {signal.created_at.strftime('%Y-%m-%d %H:%M')}")
            print(f"     Status: {signal.status}")
        
        # Demonstrate signal status updates
        print(f"\n🔄 Demonstrating signal status updates...")
        test_signal = active_signals[0]
        
        print(f"   Original status: {test_signal.status}")
        bot.signal_db.update_signal_status(test_signal.id, 'EXECUTED', execution_price=test_signal.entry_price)
        print(f"   Updated to: EXECUTED")
        
        # Revert for demo
        bot.signal_db.update_signal_status(test_signal.id, 'PENDING')
        print(f"   Reverted to: PENDING")

def demo_backtesting():
    """Demonstrate backtesting with simulated historical data."""
    print("\n" + "="*60)
    print("📈 DEMO: Backtesting with Historical Data")
    print("="*60)
    
    bot = EnhancedSniperBot(initial_capital=10000)
    
    # Run backtest
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    print(f"\n🔍 Running backtest from {start_date} to {end_date}...")
    
    results = bot.backtest_with_real_news(start_date, end_date, confidence_threshold=0.8)
    
    print(f"\n📊 Backtest Results:")
    print(f"   💼 Total Trades: {results['total_trades']}")
    print(f"   🏆 Wins: {results['wins']}")
    print(f"   💔 Losses: {results['losses']}")
    print(f"   📈 Win Rate: {results['win_rate']*100:.1f}%")
    print(f"   💰 Total Return: {results['total_return_pct']:.2f}%")
    print(f"   ⚡ Sharpe Ratio: {results['sharpe_ratio']:.2f}")
    print(f"   📉 Max Drawdown: {results['max_drawdown_pct']:.2f}%")
    
    if results['trades']:
        print(f"\n🏆 Best Trade:")
        best_trade = max(results['trades'], key=lambda x: x['return_pct'])
        print(f"   {best_trade['ticker']} on {best_trade['date']}: {best_trade['return_pct']:+.2f}%")
        
        print(f"\n💔 Worst Trade:")
        worst_trade = min(results['trades'], key=lambda x: x['return_pct'])
        print(f"   {worst_trade['ticker']} on {worst_trade['date']}: {worst_trade['return_pct']:+.2f}%")
    
    return results

def demo_revenue_projection():
    """Demonstrate revenue projection based on backtest results."""
    print("\n" + "="*60)
    print("💹 DEMO: Revenue Projection Analysis")
    print("="*60)
    
    # Run multiple backtests with different parameters
    bot = EnhancedSniperBot(initial_capital=10000)
    
    scenarios = [
        {'confidence': 0.6, 'capital': 5000, 'name': 'Conservative'},
        {'confidence': 0.8, 'capital': 10000, 'name': 'Moderate'},
        {'confidence': 1.2, 'capital': 20000, 'name': 'Aggressive'}
    ]
    
    print("\n📊 Revenue Projections for Different Scenarios:")
    
    for scenario in scenarios:
        print(f"\n🎯 {scenario['name']} Strategy:")
        print(f"   💰 Capital: ${scenario['capital']:,}")
        print(f"   📊 Confidence Threshold: {scenario['confidence']}")
        
        # Simulate results
        results = bot.backtest_with_real_news(
            (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d'),
            datetime.now().strftime('%Y-%m-%d'),
            confidence_threshold=scenario['confidence']
        )
        
        if results['total_trades'] > 0:
            final_value = scenario['capital'] * (1 + results['total_return_pct'] / 100)
            profit = final_value - scenario['capital']
            
            print(f"   📈 Total Return: {results['total_return_pct']:.2f}%")
            print(f"   💵 Final Value: ${final_value:,.2f}")
            print(f"   💰 Profit: ${profit:,.2f}")
            
            # Annualized projection
            days_traded = 90
            annual_return = (results['total_return_pct'] / days_traded) * 365
            annual_profit = scenario['capital'] * (annual_return / 100)
            
            print(f"   📅 Projected Annual Return: {annual_return:.1f}%")
            print(f"   💎 Projected Annual Profit: ${annual_profit:,.2f}")

def main():
    """Main demo function."""
    print("🎯 Enhanced Sniper Bot - Real API Integration Demo")
    print("=" * 60)
    
    # Setup
    has_real_apis = setup_demo_environment()
    
    # Demo 1: News Fetching
    news_data = demo_news_fetching()
    
    # Demo 2: Signal Generation
    signals = demo_signal_generation()
    
    # Demo 3: Signal Management
    demo_signal_management()
    
    # Demo 4: Backtesting
    backtest_results = demo_backtesting()
    
    # Demo 5: Revenue Projections
    demo_revenue_projection()
    
    # Summary
    print("\n" + "="*60)
    print("🎉 DEMO COMPLETE - Summary")
    print("="*60)
    
    print(f"\n✅ Demonstrations completed:")
    print(f"   📰 News API integration: {'✅ Real APIs' if has_real_apis else '⚠️ Demo mode'}")
    print(f"   🎯 Signal generation: {'✅ Generated' if signals else '⚠️ No signals'}")
    print(f"   💾 Database management: ✅ Working")
    print(f"   📈 Backtesting: ✅ Completed")
    print(f"   💹 Revenue projections: ✅ Calculated")
    
    print(f"\n🚀 Next Steps:")
    print(f"   1. Set up real API keys for live data")
    print(f"   2. Launch the web interface: python src/signal_manager_app.py")
    print(f"   3. Configure your trading parameters")
    print(f"   4. Start generating and managing signals!")
    
    print(f"\n📱 Mobile-friendly web interface available at:")
    print(f"   streamlit run src/signal_manager_app.py")

if __name__ == "__main__":
    main() 