#!/usr/bin/env python3
"""
Test that the app fix works - should generate signals with lower threshold.
"""

import os
import sys
sys.path.append('src')

from enhanced_sniper_bot import EnhancedSniperBot

def test_app_thresholds():
    """Test different confidence thresholds like the app would use."""
    print("🧪 TESTING: App Confidence Thresholds")
    print("=" * 50)
    
    # Set API keys
    os.environ['POLYGON_API_KEY'] = "rwd4Vdja4BxDutJIoulw9K40r7Qf8xdE"
    os.environ['ALPHA_VANTAGE_API_KEY'] = "PITRBDQSWC2015J1"
    
    bot = EnhancedSniperBot(initial_capital=5000, max_daily_trades=5)
    
    # Test old app threshold (0.8) - should fail
    print("1. Testing OLD app threshold (0.8)...")
    signals_old = bot.generate_daily_signals(confidence_threshold=0.8)
    print(f"   Signals with 0.8 threshold: {len(signals_old)}")
    
    # Test new app threshold (0.2) - should work
    print("\n2. Testing NEW app threshold (0.2)...")
    signals_new = bot.generate_daily_signals(confidence_threshold=0.2)
    print(f"   Signals with 0.2 threshold: {len(signals_new)}")
    
    if signals_new:
        print("   ✅ SUCCESS! App should now show signals:")
        for i, signal in enumerate(signals_new[:3], 1):
            print(f"   {i}. {signal.ticker} {signal.signal_type} (confidence: {signal.confidence_score:.3f})")
            print(f"      {signal.headline[:60]}...")
    else:
        print("   ❌ Still no signals - may need further adjustment")
    
    # Test even lower threshold (0.1) for comparison
    print("\n3. Testing VERY LOW threshold (0.1)...")
    signals_low = bot.generate_daily_signals(confidence_threshold=0.1)
    print(f"   Signals with 0.1 threshold: {len(signals_low)}")
    
    print(f"\n📊 SUMMARY:")
    print(f"   Threshold 0.8 (old): {len(signals_old)} signals")
    print(f"   Threshold 0.2 (new): {len(signals_new)} signals")
    print(f"   Threshold 0.1 (low): {len(signals_low)} signals")
    
    if len(signals_new) > 0:
        print("\n🎉 FIX SUCCESSFUL! App should now generate signals.")
    else:
        print("\n⚠️  May need to lower threshold further to 0.1")

if __name__ == "__main__":
    test_app_thresholds() 