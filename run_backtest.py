#!/usr/bin/env python3
"""
🎯 Quick Backtest Runner
Run this to test your trading bot against historical data
"""

import sys
import os
sys.path.append('src')

from src.yfinance_backtest import YFinanceBacktester
from datetime import datetime, timedelta

def run_quick_backtest():
    """Run a quick backtest over the last 2 weeks."""
    print("🎯 TRADING BOT HISTORICAL BACKTEST")
    print("=" * 50)
    print("Testing your exact bot logic against real Yahoo Finance data...")
    print()
    
    # Initialize backtester
    backtester = YFinanceBacktester()
    
    # Test over last 2 weeks (more manageable for quick test)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=14)
    
    print(f"📅 Testing Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"📊 Currency Pairs: {', '.join(backtester.pairs_to_test.keys())}")
    print(f"📊 Minimum Confidence: {backtester.min_confidence:.1%}")
    print(f"📊 Scan Interval: Every 6 hours")
    print()
    print("🔄 Running backtest... (this may take a few minutes)")
    print("=" * 50)
    
    try:
        # Run the backtest
        results = backtester.run_backtest(
            start_date=start_date,
            end_date=end_date,
            scan_interval_hours=6
        )
        
        if 'error' in results:
            print(f"❌ Backtest failed: {results['error']}")
            return
        
        # Generate detailed report
        backtester.generate_report(results, 'backtest_report.html')
        
        # Display summary
        print("\n🎯 BACKTEST RESULTS SUMMARY")
        print("=" * 50)
        print(f"📊 Total Trades Executed: {results['total_trades']}")
        print(f"📊 Winning Trades: {results['winning_trades']}")
        print(f"📊 Losing Trades: {results['losing_trades']}")
        print(f"📊 Timeout Trades: {results['timeout_trades']}")
        print()
        print(f"🎯 WIN RATE: {results['win_rate']:.1%}")
        print(f"💰 TOTAL PROFIT: ${results['total_profit']:.2f}")
        print(f"📈 PROFIT FACTOR: {results['profit_factor']:.2f}")
        print(f"⏱️  AVERAGE HOLD TIME: {results['avg_hold_time_hours']:.1f} hours")
        print()
        
        # Show performance by pair
        if results['pair_results']['outcome']:
            print("💱 PERFORMANCE BY CURRENCY PAIR:")
            print("-" * 40)
            for pair, win_rate in results['pair_results']['outcome'].items():
                profit = results['pair_results']['profit_loss'][pair]
                pips = results['pair_results']['pips_gained'][pair]
                print(f"{pair:8} | Win Rate: {win_rate:.1%} | Profit: ${profit:6.2f} | Pips: {pips:6.1f}")
        
        print()
        print("📊 DETAILED REPORT:")
        print(f"📄 Full report saved to: backtest_report.html")
        print("🌐 Open this file in your browser for detailed analysis!")
        print()
        
        # Performance assessment
        if results['win_rate'] >= 0.6:
            print("✅ EXCELLENT! Your bot shows strong performance!")
        elif results['win_rate'] >= 0.5:
            print("✅ GOOD! Your bot is profitable with room for improvement.")
        else:
            print("⚠️  NEEDS WORK: Consider adjusting confidence thresholds.")
        
        if results['profit_factor'] > 1.5:
            print("✅ STRONG PROFIT FACTOR: Your wins significantly outweigh losses!")
        elif results['profit_factor'] > 1.0:
            print("✅ PROFITABLE: Positive expectancy confirmed!")
        else:
            print("⚠️  PROFIT FACTOR BELOW 1.0: System needs optimization.")
        
        print("\n🚀 Ready to deploy your bot to the cloud for 24/7 trading!")
        
    except Exception as e:
        print(f"❌ Error running backtest: {e}")
        print("💡 Make sure you're in the correct directory and have all dependencies installed.")

if __name__ == "__main__":
    run_quick_backtest() 