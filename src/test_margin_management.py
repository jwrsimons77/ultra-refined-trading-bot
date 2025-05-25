#!/usr/bin/env python3
"""
Test script for margin management system
Verifies that the bot properly tracks margin and prevents overtrading
"""

import logging
from oanda_trader import OANDATrader
from forex_signal_generator import ForexSignalGenerator, ForexSignal
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_margin_management():
    """Test the margin management system."""
    print("🧪 Testing Margin Management System")
    print("=" * 50)
    
    # Initialize trader
    api_key = "fe92315bee29b117825fed529cf3fa99-173e927b8cdbb1fc244993e24e33fd93"
    account_id = "101-004-31788297-001"
    
    trader = OANDATrader(api_key, account_id, environment="practice")
    
    # Test 1: Get account summary
    print("\n📊 Test 1: Account Summary")
    print("-" * 30)
    
    account_summary = trader.get_account_summary()
    
    if account_summary:
        print(f"✅ Account summary retrieved successfully")
        print(f"   Balance: ${account_summary['balance']:.2f}")
        print(f"   Margin Used: ${account_summary['margin_used']:.2f}")
        print(f"   Margin Available: ${account_summary['margin_available']:.2f}")
        print(f"   Open Trades: {account_summary['open_trade_count']}")
        
        # Calculate utilization
        utilization = (account_summary['margin_used'] / account_summary['balance']) * 100 if account_summary['balance'] > 0 else 0
        print(f"   Margin Utilization: {utilization:.1f}%")
    else:
        print("❌ Failed to get account summary")
        return
    
    # Test 2: Margin calculation for different trade sizes
    print("\n💰 Test 2: Margin Calculations")
    print("-" * 30)
    
    test_pairs = ["EUR/USD", "GBP/USD", "USD/JPY"]
    test_units = [1000, 5000, 10000]
    
    for pair in test_pairs:
        print(f"\n{pair}:")
        for units in test_units:
            margin_required = trader.calculate_margin_required(pair, units)
            print(f"   {units:,} units = ${margin_required:.2f} margin")
    
    # Test 3: Margin availability checks
    print("\n🔍 Test 3: Margin Availability Checks")
    print("-" * 30)
    
    for pair in test_pairs:
        margin_check = trader.check_margin_availability(pair, 5000)
        status = "✅ APPROVED" if margin_check['available'] else "❌ REJECTED"
        print(f"{pair}: {status}")
        if margin_check['reason']:
            print(f"   Reason: {margin_check['reason']}")
    
    # Test 4: Safe position size calculation
    print("\n📏 Test 4: Safe Position Size Calculation")
    print("-" * 30)
    
    # Create a mock signal for testing
    mock_signal = ForexSignal(
        pair="EUR/USD",
        signal_type="BUY",
        entry_price=1.0800,
        target_price=1.0850,
        stop_loss=1.0750,
        confidence=0.75,
        pips_target=50,
        pips_risk=50,
        risk_reward_ratio="1:1",
        reason="Test signal for margin management",
        timestamp=datetime.now(),
        news_sentiment=0.7,
        technical_score=0.8
    )
    
    safe_size = trader.calculate_safe_position_size(mock_signal, account_summary)
    print(f"Safe position size for EUR/USD: {safe_size:,} units")
    
    if safe_size > 0:
        final_margin = trader.calculate_margin_required("EUR/USD", safe_size)
        print(f"Margin required: ${final_margin:.2f}")
        print(f"Remaining available: ${account_summary['margin_available'] - final_margin:.2f}")
    
    # Test 5: Signal validation
    print("\n✅ Test 5: Signal Validation")
    print("-" * 30)
    
    should_trade = trader.should_trade_signal(mock_signal)
    print(f"Should trade signal: {'✅ YES' if should_trade else '❌ NO'}")
    
    # Test 6: Multiple position simulation
    print("\n🔄 Test 6: Multiple Position Simulation")
    print("-" * 30)
    
    print("Simulating multiple trades to test margin limits...")
    
    test_signals = [
        ForexSignal("EUR/USD", "BUY", 1.0800, 1.0850, 1.0750, 0.75, 50, 50, "1:1", "Test 1", datetime.now(), 0.7, 0.8),
        ForexSignal("GBP/USD", "SELL", 1.2600, 1.2550, 1.2650, 0.70, 50, 50, "1:1", "Test 2", datetime.now(), 0.6, 0.7),
        ForexSignal("USD/JPY", "BUY", 149.50, 150.00, 149.00, 0.80, 50, 50, "1:1", "Test 3", datetime.now(), 0.8, 0.9),
        ForexSignal("AUD/USD", "SELL", 0.6600, 0.6550, 0.6650, 0.65, 50, 50, "1:1", "Test 4", datetime.now(), 0.5, 0.6),
    ]
    
    approved_count = 0
    total_margin_needed = 0
    
    for i, signal in enumerate(test_signals, 1):
        print(f"\nSignal {i}: {signal.signal_type} {signal.pair}")
        
        # Check if this signal would be approved
        would_approve = trader.should_trade_signal(signal)
        
        if would_approve:
            safe_size = trader.calculate_safe_position_size(signal, account_summary)
            if safe_size > 0:
                margin_needed = trader.calculate_margin_required(signal.pair, safe_size)
                total_margin_needed += margin_needed
                approved_count += 1
                print(f"   ✅ APPROVED - Size: {safe_size:,} units, Margin: ${margin_needed:.2f}")
            else:
                print(f"   ❌ REJECTED - Cannot calculate safe size")
        else:
            print(f"   ❌ REJECTED - Failed validation")
    
    print(f"\nSummary:")
    print(f"   Signals approved: {approved_count}/{len(test_signals)}")
    print(f"   Total margin needed: ${total_margin_needed:.2f}")
    print(f"   Available margin: ${account_summary['margin_available']:.2f}")
    print(f"   Remaining after trades: ${account_summary['margin_available'] - total_margin_needed:.2f}")
    
    # Final safety check
    if total_margin_needed <= account_summary['margin_available']:
        print("   ✅ All approved trades fit within available margin")
    else:
        print("   ⚠️ Approved trades exceed available margin (system should prevent this)")
    
    print("\n🎯 Margin Management Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    test_margin_management() 