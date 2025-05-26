#!/usr/bin/env python3
"""
🎯 Monthly Backtest with $10,000
Full 30-day performance analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from linear_scaled_backtest import LinearScaledBacktest
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def run_monthly_backtest():
    """Run a full month backtest with $10,000."""
    try:
        # Initialize with $10,000
        backtest = LinearScaledBacktest(initial_balance=10000)
        
        pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD']
        
        # Full month: December 1-31, 2024 (30 days)
        start_date = datetime(2024, 12, 1)
        end_date = datetime(2024, 12, 31)
        
        print(f"🎯 MONTHLY BACKTEST: $10,000 ACCOUNT")
        print(f"📅 Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} (30 days)")
        print("=" * 60)
        
        results = backtest.run_optimized_backtest(pairs, start_date, end_date)
        
        # Add scaling information
        results['scale_factor'] = backtest.scale_factor
        results['base_balance'] = backtest.base_balance
        results['period_days'] = 30
        
        return results
        
    except Exception as e:
        print(f"Error in monthly backtest: {e}")
        return {'error': str(e)}

def generate_monthly_report(results):
    """Generate comprehensive monthly performance report."""
    if 'error' in results:
        print(f"❌ Error: {results['error']}")
        return
    
    # Extract key metrics
    initial_balance = results['initial_balance']
    final_balance = results['final_balance']
    total_profit = results['total_profit']
    total_return = results['total_return']
    total_trades = results['total_trades']
    win_rate = results['win_rate']
    profit_factor = results['profit_factor']
    avg_win = results['avg_win']
    avg_loss = results['avg_loss']
    avg_hold_time = results['avg_hold_time']
    
    # Calculate daily averages
    daily_profit = total_profit / 30
    daily_return = total_return / 30
    daily_trades = total_trades / 30
    
    # Calculate annual projections
    annual_return = total_return * 12
    annual_profit = total_profit * 12
    
    print(f"\n📊 MONTHLY PERFORMANCE SUMMARY")
    print("=" * 50)
    print(f"💰 Account Performance:")
    print(f"   Initial Balance: ${initial_balance:,.2f}")
    print(f"   Final Balance: ${final_balance:,.2f}")
    print(f"   Total Profit: ${total_profit:,.2f}")
    print(f"   Monthly Return: {total_return:.2f}%")
    print(f"   Daily Average: ${daily_profit:.2f} ({daily_return:.3f}%)")
    print()
    
    print(f"📈 Trading Statistics:")
    print(f"   Total Trades: {total_trades}")
    print(f"   Win Rate: {win_rate:.1%}")
    print(f"   Profit Factor: {profit_factor:.2f}")
    print(f"   Average Win: ${avg_win:.2f}")
    print(f"   Average Loss: ${avg_loss:.2f}")
    print(f"   Average Hold Time: {avg_hold_time:.1f} hours")
    print(f"   Daily Trade Average: {daily_trades:.1f}")
    print()
    
    print(f"🚀 Annual Projections:")
    print(f"   Annual Return: {annual_return:.1f}%")
    print(f"   Annual Profit: ${annual_profit:,.2f}")
    print(f"   Year-End Balance: ${initial_balance + annual_profit:,.2f}")
    print()
    
    # Performance rating
    if total_return > 8:
        rating = "🚀 EXCELLENT"
        comment = "Outstanding monthly performance!"
    elif total_return > 5:
        rating = "✅ VERY GOOD"
        comment = "Strong monthly returns."
    elif total_return > 3:
        rating = "👍 GOOD"
        comment = "Solid monthly performance."
    elif total_return > 0:
        rating = "📈 POSITIVE"
        comment = "Profitable month."
    else:
        rating = "⚠️ NEGATIVE"
        comment = "Loss this month."
    
    print(f"🎯 Performance Rating: {rating}")
    print(f"   {comment}")
    print()
    
    # Risk analysis
    max_risk_per_trade = (avg_loss * -1) if avg_loss < 0 else 0
    max_monthly_risk = max_risk_per_trade * total_trades * 0.3  # Assume 30% loss rate
    risk_percentage = (max_monthly_risk / initial_balance) * 100
    
    print(f"⚖️ Risk Analysis:")
    print(f"   Max Risk Per Trade: ${max_risk_per_trade:.2f}")
    print(f"   Estimated Monthly Risk: ${max_monthly_risk:.2f} ({risk_percentage:.1f}%)")
    print(f"   Risk-Adjusted Return: {total_return / max(risk_percentage, 1):.2f}")
    print()
    
    # Pair performance
    if 'pair_performance' in results:
        print(f"💱 Top Performing Pairs:")
        pair_performance = results['pair_performance']
        sorted_pairs = sorted(pair_performance.items(), key=lambda x: x[1]['profit'], reverse=True)
        
        for i, (pair, stats) in enumerate(sorted_pairs[:3]):
            print(f"   {i+1}. {pair}: ${stats['profit']:,.2f} ({stats['win_rate']:.1%} win rate, {stats['trades']} trades)")
        print()
    
    # Scaling demonstration
    print(f"📊 SCALING COMPARISON:")
    print(f"   $1,000 Account (projected): ${total_profit/10:.2f}")
    print(f"   $10,000 Account (actual): ${total_profit:.2f}")
    print(f"   $50,000 Account (projected): ${total_profit*5:,.2f}")
    print(f"   $100,000 Account (projected): ${total_profit*10:,.2f}")

def main():
    """Run monthly backtest and generate report."""
    print("🎯 MONTHLY TRADING SYSTEM BACKTEST")
    print("💰 $10,000 Account - 30 Day Analysis")
    print("=" * 60)
    
    # Run the backtest
    results = run_monthly_backtest()
    
    # Generate comprehensive report
    generate_monthly_report(results)
    
    return results

if __name__ == "__main__":
    main() 