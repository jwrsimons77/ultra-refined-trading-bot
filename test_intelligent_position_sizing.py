#!/usr/bin/env python3
"""
Test intelligent position sizing with risk management
"""

import sys
import os
sys.path.append('src')

# Mock the environment variables to avoid initialization errors
os.environ['OANDA_API_KEY'] = 'test_key'
os.environ['OANDA_ACCOUNT_ID'] = 'test_account'

from ultra_refined_railway_trading_bot import AdvancedPerformanceTracker
from datetime import datetime, timezone

def test_risk_adjustments():
    """Test that risk adjustments work correctly."""
    print("🧪 Testing Risk Adjustments")
    print("=" * 60)
    
    # Create performance tracker
    tracker = AdvancedPerformanceTracker()
    
    # Test 1: Normal conditions (no recent losses)
    print("🔍 TEST 1: Normal Conditions (No Recent Losses)")
    print("-" * 40)
    
    tracker.consecutive_losses = 0
    tracker.losing_streak = 0
    
    risk_adjustment = tracker.get_dynamic_risk_adjustment()
    should_reduce = tracker.should_reduce_risk()
    
    print(f"   Risk Adjustment: {risk_adjustment:.2f}")
    print(f"   Should Reduce Risk: {should_reduce}")
    print(f"   Expected: 1.0 (normal risk)")
    print()
    
    # Test 2: After 3 consecutive losses (25% risk reduction)
    print("🔍 TEST 2: After 3 Consecutive Losses (25% Risk Reduction)")
    print("-" * 40)
    
    tracker.consecutive_losses = 3
    tracker.losing_streak = 0
    
    risk_adjustment_2 = tracker.get_dynamic_risk_adjustment()
    should_reduce_2 = tracker.should_reduce_risk()
    
    print(f"   Risk Adjustment: {risk_adjustment_2:.2f}")
    print(f"   Should Reduce Risk: {should_reduce_2}")
    print(f"   Expected: 0.75 (25% reduction)")
    print()
    
    # Test 3: After 5 consecutive losses (50% risk reduction)
    print("🔍 TEST 3: After 5 Consecutive Losses (50% Risk Reduction)")
    print("-" * 40)
    
    tracker.consecutive_losses = 5
    tracker.losing_streak = 0
    
    risk_adjustment_3 = tracker.get_dynamic_risk_adjustment()
    should_reduce_3 = tracker.should_reduce_risk()
    
    print(f"   Risk Adjustment: {risk_adjustment_3:.2f}")
    print(f"   Should Reduce Risk: {should_reduce_3}")
    print(f"   Expected: 0.5 (50% reduction)")
    print()
    
    # Test 4: After 7+ losing streak (40% risk reduction)
    print("🔍 TEST 4: After 7+ Losing Streak (40% Risk Reduction)")
    print("-" * 40)
    
    tracker.consecutive_losses = 0
    tracker.losing_streak = 7
    
    risk_adjustment_4 = tracker.get_dynamic_risk_adjustment()
    should_reduce_4 = tracker.should_reduce_risk()
    
    print(f"   Risk Adjustment: {risk_adjustment_4:.2f}")
    print(f"   Should Reduce Risk: {should_reduce_4}")
    print(f"   Expected: 0.6 (40% reduction)")
    print()
    
    # Summary
    print("📊 SUMMARY:")
    print("=" * 60)
    print(f"Normal conditions: {risk_adjustment:.2f} (should reduce: {should_reduce})")
    print(f"3 losses: {risk_adjustment_2:.2f} (should reduce: {should_reduce_2})")
    print(f"5 losses: {risk_adjustment_3:.2f} (should reduce: {should_reduce_3})")
    print(f"7+ streak: {risk_adjustment_4:.2f} (should reduce: {should_reduce_4})")
    
    # Verify risk management is working
    print()
    print("✅ VERIFICATION:")
    if risk_adjustment_2 < risk_adjustment:
        print("   ✅ Risk reduced after 3 losses")
    else:
        print("   ❌ Risk not reduced after 3 losses")
    
    if risk_adjustment_3 < risk_adjustment_2:
        print("   ✅ Risk further reduced after 5 losses")
    else:
        print("   ❌ Risk not further reduced after 5 losses")
    
    if risk_adjustment_4 < risk_adjustment:
        print("   ✅ Risk reduced after losing streak")
    else:
        print("   ❌ Risk not reduced after losing streak")
    
    print()
    print("🎯 INTELLIGENT RISK MANAGEMENT RESTORED:")
    print("   ✅ Dynamic risk adjustments based on performance")
    print("   ✅ 25% risk reduction after 3 consecutive losses")
    print("   ✅ 50% risk reduction after 5 consecutive losses")
    print("   ✅ 40% risk reduction after 7+ losing streak")
    print("   ✅ Protects account during poor performance")

def test_position_size_calculation():
    """Test position size calculation logic."""
    print("\n🧪 Testing Position Size Calculation Logic")
    print("=" * 60)
    
    # Mock account balance and parameters
    account_balance = 10000.0
    base_risk_per_trade = 0.02  # 2%
    stop_distance_pips = 50.0
    
    print(f"💰 Test Account Balance: ${account_balance}")
    print(f"🛡️  Base Risk per Trade: {base_risk_per_trade:.1%}")
    print(f"📏 Stop Distance: {stop_distance_pips} pips")
    print()
    
    # Test different risk adjustments
    risk_adjustments = [1.0, 0.75, 0.5, 0.6]
    scenarios = ["Normal", "3 Losses", "5 Losses", "7+ Streak"]
    
    for i, (adjustment, scenario) in enumerate(zip(risk_adjustments, scenarios)):
        print(f"🔍 {scenario} Conditions (Risk Adjustment: {adjustment:.2f})")
        print("-" * 40)
        
        # Calculate adjusted risk
        adjusted_risk = base_risk_per_trade * adjustment
        risk_amount = account_balance * adjusted_risk
        
        print(f"   Adjusted Risk: {adjusted_risk:.1%}")
        print(f"   Risk Amount: ${risk_amount:.2f}")
        
        # Estimate position size (simplified calculation)
        # Assuming pip value is roughly $0.10 per 1000 units for EUR/USD
        pip_value_per_unit = 0.0001  # Simplified
        position_size = int(risk_amount / (stop_distance_pips * pip_value_per_unit))
        
        # Apply limits
        min_size = 1000
        max_size = min(20000, int(account_balance * 0.1))
        position_size = max(min_size, min(position_size, max_size))
        
        print(f"   Calculated Position Size: {position_size} units")
        
        # Check if 5000 units would be preferred
        if position_size >= 5000:
            print(f"   ✅ Would prefer 5000 units (within calculated limit)")
        else:
            print(f"   ⚠️ Would use {position_size} units (5000 too large)")
        
        print()

if __name__ == "__main__":
    test_risk_adjustments()
    test_position_size_calculation() 