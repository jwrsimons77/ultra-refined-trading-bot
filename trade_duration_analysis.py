#!/usr/bin/env python3
"""
Detailed trade duration analysis showing how long each trade took to hit targets.
"""

import os
import sys
sys.path.append('src')

from enhanced_sniper_bot import EnhancedSniperBot
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np

def analyze_trade_durations():
    """Analyze how long trades took to hit targets or stop losses."""
    print("⏱️  TRADE DURATION ANALYSIS")
    print("=" * 80)
    
    # Set API keys
    os.environ['POLYGON_API_KEY'] = "rwd4Vdja4BxDutJIoulw9K40r7Qf8xdE"
    os.environ['ALPHA_VANTAGE_API_KEY'] = "PITRBDQSWC2015J1"
    
    bot = EnhancedSniperBot(initial_capital=10000, max_daily_trades=10)
    
    # Run backtest to get trades
    start_date = "2025-02-24"
    end_date = "2025-05-25"
    confidence_threshold = 0.2
    
    print(f"🗓️  PERIOD: {start_date} to {end_date}")
    print(f"🎯 CONFIDENCE: {confidence_threshold}")
    print(f"💰 CAPITAL: $10,000")
    print()
    
    results = bot.backtest_with_real_news(start_date, end_date, confidence_threshold)
    
    if not results['trades']:
        print("❌ No trades found in backtest")
        return
    
    print(f"📊 ANALYZING {len(results['trades'])} TRADES")
    print("=" * 80)
    
    # Analyze each trade duration
    trade_durations = []
    
    for i, trade in enumerate(results['trades'][:20], 1):  # Show first 20 trades
        ticker = trade['ticker']
        entry_date = datetime.strptime(trade['date'], '%Y-%m-%d')
        entry_price = trade['entry_price']
        target_price = trade['target_price']
        signal_type = trade['signal_type']
        
        # Calculate how long it took to hit target/stop
        duration_days = analyze_single_trade_duration(
            ticker, entry_date, entry_price, target_price, signal_type
        )
        
        trade_durations.append(duration_days)
        
        # Display trade details
        outcome_emoji = "✅" if trade['outcome'] == 'WIN' else "❌"
        duration_text = f"{duration_days} days" if duration_days > 0 else "Never hit"
        
        print(f"{i:2d}. {trade['date']} | {ticker:4s} {signal_type:4s} | "
              f"${entry_price:6.2f} → ${target_price:6.2f} | "
              f"{trade['return_pct']:+5.1f}% | {duration_text:10s} | {outcome_emoji}")
    
    # Summary statistics
    valid_durations = [d for d in trade_durations if d > 0]
    
    print("\n" + "=" * 80)
    print("📈 DURATION STATISTICS")
    print("=" * 80)
    
    if valid_durations:
        print(f"Average time to target: {np.mean(valid_durations):.1f} days")
        print(f"Median time to target: {np.median(valid_durations):.1f} days")
        print(f"Fastest trade: {min(valid_durations)} days")
        print(f"Slowest trade: {max(valid_durations)} days")
        print(f"Trades that hit target: {len(valid_durations)}/{len(trade_durations)} ({len(valid_durations)/len(trade_durations)*100:.1f}%)")
    
    # Duration distribution
    print(f"\n⏰ DURATION BREAKDOWN:")
    duration_ranges = [
        (1, 1, "Same day"),
        (2, 3, "2-3 days"),
        (4, 7, "4-7 days"),
        (8, 14, "1-2 weeks"),
        (15, 30, "2-4 weeks"),
        (31, 999, "1+ month")
    ]
    
    for min_days, max_days, label in duration_ranges:
        count = sum(1 for d in valid_durations if min_days <= d <= max_days)
        percentage = count / len(valid_durations) * 100 if valid_durations else 0
        print(f"   {label:12s}: {count:2d} trades ({percentage:4.1f}%)")

def analyze_single_trade_duration(ticker, entry_date, entry_price, target_price, signal_type):
    """Analyze how long a single trade took to hit its target."""
    try:
        # Get historical data for the period after entry
        end_date = entry_date + timedelta(days=60)  # Look 60 days ahead
        
        stock = yf.Ticker(ticker)
        hist = stock.history(start=entry_date, end=end_date)
        
        if hist.empty:
            return -1
        
        # Check each day to see if target was hit
        for i, (date, row) in enumerate(hist.iterrows()):
            if signal_type == 'BUY':
                # For BUY signals, check if high price reached target
                if row['High'] >= target_price:
                    return i + 1  # Days to hit target
            else:  # SELL signal
                # For SELL signals, check if low price reached target
                if row['Low'] <= target_price:
                    return i + 1  # Days to hit target
        
        return -1  # Never hit target in 60 days
        
    except Exception as e:
        print(f"Error analyzing {ticker}: {e}")
        return -1

def show_current_signals_with_projections():
    """Show current signals with projected timeframes."""
    print("\n🔮 CURRENT SIGNALS WITH TIME PROJECTIONS")
    print("=" * 80)
    
    # Set API keys
    os.environ['POLYGON_API_KEY'] = "rwd4Vdja4BxDutJIoulw9K40r7Qf8xdE"
    os.environ['ALPHA_VANTAGE_API_KEY'] = "PITRBDQSWC2015J1"
    
    bot = EnhancedSniperBot(initial_capital=5000, max_daily_trades=10)
    
    # Get current signals
    signals = bot.generate_daily_signals(confidence_threshold=0.2)
    
    if not signals:
        print("❌ No current signals found")
        return
    
    print(f"📊 FOUND {len(signals)} CURRENT SIGNALS:")
    print()
    
    for i, signal in enumerate(signals, 1):
        # Calculate expected timeframe based on price movement needed
        price_change_pct = abs((signal.target_price - signal.entry_price) / signal.entry_price * 100)
        
        # Estimate timeframe based on typical volatility
        if price_change_pct < 3:
            timeframe = "1-3 days"
        elif price_change_pct < 7:
            timeframe = "3-7 days"
        elif price_change_pct < 15:
            timeframe = "1-2 weeks"
        else:
            timeframe = "2-4 weeks"
        
        print(f"{i}. {signal.ticker} {signal.signal_type}")
        print(f"   Entry: ${signal.entry_price:.2f} → Target: ${signal.target_price:.2f}")
        print(f"   Move needed: {price_change_pct:.1f}%")
        print(f"   Confidence: {signal.confidence_score:.3f}")
        print(f"   Expected timeframe: {timeframe}")
        print(f"   News: {signal.headline[:60]}...")
        print()

if __name__ == "__main__":
    analyze_trade_durations()
    show_current_signals_with_projections() 