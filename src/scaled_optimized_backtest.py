#!/usr/bin/env python3
"""
🎯 Scaled Optimized Trading System Backtest
$10,000 starting capital version
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from optimized_advanced_backtest import OptimizedAdvancedBacktest
from datetime import datetime

def run_scaled_backtest():
    """Run the optimized backtest with $10,000 starting capital."""
    try:
        # Initialize with $10,000 instead of $1,000
        backtest = OptimizedAdvancedBacktest(initial_balance=10000)
        
        pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD']
        start_date = datetime(2024, 12, 1)
        end_date = datetime(2024, 12, 15)
        
        results = backtest.run_optimized_backtest(pairs, start_date, end_date)
        return results
        
    except Exception as e:
        print(f"Error in backtest: {e}")
        return {'error': str(e)}

if __name__ == "__main__":
    print("🎯 SCALED OPTIMIZED TRADING SYSTEM BACKTEST")
    print("💰 Starting Capital: $10,000")
    print("=" * 60)
    
    results = run_scaled_backtest()
    
    if 'error' in results:
        print(f"❌ Error: {results['error']}")
    else:
        print(f"\n📊 SCALED BACKTEST RESULTS:")
        print(f"   Initial Balance: ${results['initial_balance']:,.2f}")
        print(f"   Final Balance: ${results['final_balance']:,.2f}")
        print(f"   Total Profit: ${results['total_profit']:,.2f}")
        print(f"   Total Return: {results['total_return']:.1f}%")
        print(f"   Total Trades: {results['total_trades']}")
        print(f"   Win Rate: {results['win_rate']:.1%}")
        print(f"   Profit Factor: {results['profit_factor']:.2f}")
        print(f"   Signal Filter Rate: {results['signal_filter_rate']:.1%}")
        
        # Calculate monthly and annual projections
        monthly_return = results['total_return'] * 2.14  # 14 days to 30 days
        annual_return = monthly_return * 12
        
        print(f"\n🚀 PROJECTIONS:")
        print(f"   Monthly Return: {monthly_return:.1f}%")
        print(f"   Annual Return: {annual_return:.1f}%")
        print(f"   Monthly Profit: ${results['total_profit'] * 2.14:,.2f}")
        print(f"   Annual Profit: ${results['total_profit'] * 2.14 * 12:,.2f}")
        
        if results['total_profit'] > 0:
            print(f"\n🎉 EXCELLENT! System is highly profitable with larger capital.")
        else:
            print(f"\n⚠️  Negative results. System needs optimization.") 