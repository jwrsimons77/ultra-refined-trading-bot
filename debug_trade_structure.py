#!/usr/bin/env python3
"""
Debug script to see the structure of trade data.
"""

import os
import sys
sys.path.append('src')

from enhanced_sniper_bot import EnhancedSniperBot
import json

def debug_trade_structure():
    """Debug the structure of trade data."""
    print("🔍 DEBUGGING TRADE STRUCTURE")
    print("=" * 50)
    
    # Set API keys
    os.environ['POLYGON_API_KEY'] = "rwd4Vdja4BxDutJIoulw9K40r7Qf8xdE"
    os.environ['ALPHA_VANTAGE_API_KEY'] = "PITRBDQSWC2015J1"
    
    bot = EnhancedSniperBot(initial_capital=10000, max_daily_trades=10)
    
    # Run a small backtest
    results = bot.backtest_with_real_news("2025-02-24", "2025-05-25", 0.2)
    
    print(f"Results keys: {list(results.keys())}")
    print(f"Number of trades: {len(results.get('trades', []))}")
    
    if results.get('trades'):
        print("\nFirst trade structure:")
        first_trade = results['trades'][0]
        print(json.dumps(first_trade, indent=2, default=str))
        
        print(f"\nTrade keys: {list(first_trade.keys())}")

if __name__ == "__main__":
    debug_trade_structure() 