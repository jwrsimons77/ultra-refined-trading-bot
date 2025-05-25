#!/usr/bin/env python3
"""
Detailed backtest analysis showing actual trades and confidence threshold comparison.
"""

import os
import sys
sys.path.append('src')

from enhanced_sniper_bot import EnhancedSniperBot
import pandas as pd
from datetime import datetime, timedelta

def analyze_backtest_trades():
    """Show detailed backtest trades and confidence threshold analysis."""
    print("📊 BACKTEST ANALYSIS: Trades & Confidence Thresholds")
    print("=" * 70)
    
    # Set API keys
    os.environ['POLYGON_API_KEY'] = "rwd4Vdja4BxDutJIoulw9K40r7Qf8xdE"
    os.environ['ALPHA_VANTAGE_API_KEY'] = "PITRBDQSWC2015J1"
    
    bot = EnhancedSniperBot(initial_capital=10000, max_daily_trades=10)
    
    # Run backtest with different confidence thresholds
    start_date = "2025-02-24"
    end_date = "2025-05-25"
    
    print(f"🗓️  BACKTEST PERIOD: {start_date} to {end_date}")
    print(f"💰 INITIAL CAPITAL: $10,000")
    print()
    
    # Test different confidence thresholds
    thresholds = [0.1, 0.3, 0.5, 0.8, 1.0]
    results_comparison = []
    
    for threshold in thresholds:
        print(f"🎯 TESTING CONFIDENCE THRESHOLD: {threshold}")
        print("-" * 50)
        
        results = bot.backtest_with_real_news(start_date, end_date, threshold)
        
        print(f"📈 RESULTS SUMMARY:")
        print(f"   Total Trades: {results['total_trades']}")
        print(f"   Wins: {results['wins']} | Losses: {results['losses']}")
        print(f"   Win Rate: {results['win_rate']*100:.1f}%")
        print(f"   Total Return: {results['total_return_pct']:.1f}%")
        print(f"   Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        print(f"   Max Drawdown: {results['max_drawdown_pct']:.1f}%")
        
        # Calculate final portfolio value
        final_value = 10000 * (1 + results['total_return_pct']/100)
        profit = final_value - 10000
        
        print(f"   Final Portfolio: ${final_value:,.2f}")
        print(f"   Profit/Loss: ${profit:,.2f}")
        
        results_comparison.append({
            'threshold': threshold,
            'trades': results['total_trades'],
            'win_rate': results['win_rate'],
            'total_return': results['total_return_pct'],
            'final_value': final_value,
            'profit': profit
        })
        
        # Show sample trades for this threshold
        if results['trades'] and len(results['trades']) > 0:
            print(f"\n📋 SAMPLE TRADES (First 5):")
            for i, trade in enumerate(results['trades'][:5], 1):
                outcome_emoji = "✅" if trade['outcome'] == 'WIN' else "❌"
                print(f"   {i}. {trade['date']} | {trade['ticker']} | {trade['return_pct']:+.1f}% | {outcome_emoji} {trade['outcome']}")
        
        print("\n" + "="*70 + "\n")
    
    # Comparison table
    print("📊 CONFIDENCE THRESHOLD COMPARISON")
    print("=" * 70)
    print(f"{'Threshold':<12} {'Trades':<8} {'Win Rate':<10} {'Return %':<10} {'Final Value':<12} {'Profit':<10}")
    print("-" * 70)
    
    for result in results_comparison:
        print(f"{result['threshold']:<12} {result['trades']:<8} {result['win_rate']*100:>7.1f}% {result['total_return']:>8.1f}% ${result['final_value']:>10,.0f} ${result['profit']:>8,.0f}")
    
    print("\n💡 KEY INSIGHTS:")
    print("=" * 70)
    
    # Find best performing threshold
    best_return = max(results_comparison, key=lambda x: x['total_return'])
    most_trades = max(results_comparison, key=lambda x: x['trades'])
    
    print(f"🏆 BEST RETURN: {best_return['threshold']} threshold with {best_return['total_return']:.1f}% return")
    print(f"📈 MOST ACTIVE: {most_trades['threshold']} threshold with {most_trades['trades']} trades")
    
    print(f"\n🔍 WHY LOWER THRESHOLDS GENERATE MORE SIGNALS:")
    print(f"   • Confidence 0.1: Accepts signals with low but positive sentiment")
    print(f"   • Confidence 1.0: Only accepts very strong sentiment + high-quality sources")
    print(f"   • More trades = more opportunities but also more risk")
    print(f"   • Sweet spot is usually 0.2-0.4 for balance of quality vs quantity")
    
    return results_comparison

def show_current_live_signals():
    """Show what signals are currently being generated."""
    print("\n🔴 LIVE SIGNAL GENERATION TEST")
    print("=" * 70)
    
    # Set API keys
    os.environ['POLYGON_API_KEY'] = "rwd4Vdja4BxDutJIoulw9K40r7Qf8xdE"
    os.environ['ALPHA_VANTAGE_API_KEY'] = "PITRBDQSWC2015J1"
    
    bot = EnhancedSniperBot(initial_capital=5000, max_daily_trades=10)
    
    # Test current signal generation with different thresholds
    thresholds = [0.1, 0.2, 0.3, 0.5]
    
    for threshold in thresholds:
        print(f"\n🎯 LIVE SIGNALS WITH {threshold} CONFIDENCE:")
        signals = bot.generate_daily_signals(confidence_threshold=threshold)
        
        if signals:
            print(f"   Found {len(signals)} signals:")
            for i, signal in enumerate(signals, 1):
                print(f"   {i}. {signal.ticker} {signal.signal_type} (conf: {signal.confidence_score:.3f})")
                print(f"      Entry: ${signal.entry_price:.2f} | Target: ${signal.target_price:.2f}")
                print(f"      News: {signal.headline[:60]}...")
                print()
        else:
            print(f"   No signals found with {threshold} threshold")

if __name__ == "__main__":
    # Run backtest analysis
    results = analyze_backtest_trades()
    
    # Show current live signals
    show_current_live_signals() 