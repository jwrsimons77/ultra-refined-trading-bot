#!/usr/bin/env python3
"""
Test script to generate forex signals for testing pip calculations
"""

import sys
import os
sys.path.append('src')

from forex_signal_generator import ForexSignalGenerator, ForexSignal
from datetime import datetime
import random

def create_test_signals():
    """Create test signals with known values to test pip calculations."""
    
    # Create test signals with realistic forex prices
    test_signals = [
        ForexSignal(
            pair="EUR/USD",
            signal_type="BUY",
            entry_price=1.0850,
            target_price=1.0880,  # 30 pips target
            stop_loss=1.0830,     # 20 pips stop
            confidence=0.75,      # High confidence for auto-execute
            pips_target=30,
            pips_risk=20,
            risk_reward_ratio="1:1.5",
            reason="Test signal - Strong bullish sentiment + Technical breakout",
            timestamp=datetime.now(),
            news_sentiment=0.4,
            technical_score=0.3
        ),
        ForexSignal(
            pair="GBP/USD",
            signal_type="SELL",
            entry_price=1.2650,
            target_price=1.2600,  # 50 pips target
            stop_loss=1.2680,     # 30 pips stop
            confidence=0.65,      # Medium-high confidence
            pips_target=50,
            pips_risk=30,
            risk_reward_ratio="1:1.7",
            reason="Test signal - Bearish news sentiment + Technical resistance",
            timestamp=datetime.now(),
            news_sentiment=-0.3,
            technical_score=-0.2
        ),
        ForexSignal(
            pair="USD/JPY",
            signal_type="BUY",
            entry_price=149.50,
            target_price=150.00,  # 50 pips target (JPY pair)
            stop_loss=149.20,     # 30 pips stop (JPY pair)
            confidence=0.80,      # Very high confidence for auto-execute
            pips_target=50,
            pips_risk=30,
            risk_reward_ratio="1:1.7",
            reason="Test signal - USD strength + BoJ dovish stance",
            timestamp=datetime.now(),
            news_sentiment=0.5,
            technical_score=0.4
        ),
        ForexSignal(
            pair="AUD/USD",
            signal_type="SELL",
            entry_price=0.6590,
            target_price=0.6560,  # 30 pips target
            stop_loss=0.6610,     # 20 pips stop
            confidence=0.45,      # Lower confidence for manual review
            pips_target=30,
            pips_risk=20,
            risk_reward_ratio="1:1.5",
            reason="Test signal - Weak commodity prices + RBA concerns",
            timestamp=datetime.now(),
            news_sentiment=-0.2,
            technical_score=-0.1
        )
    ]
    
    return test_signals

def test_pip_calculations():
    """Test the pip calculation functions."""
    from forex_trading_app import calculate_trade_pnl
    
    print("🧪 Testing Pip Calculations")
    print("=" * 50)
    
    test_signals = create_test_signals()
    
    for signal in test_signals:
        print(f"\n📊 Testing {signal.pair} - {signal.signal_type}")
        print(f"Entry: {signal.entry_price:.5f}")
        print(f"Target: {signal.target_price:.5f}")
        print(f"Stop: {signal.stop_loss:.5f}")
        print(f"Expected pips to target: {signal.pips_target}")
        print(f"Expected pips to stop: {signal.pips_risk}")
        
        # Test with 1000 units
        pnl_data = calculate_trade_pnl(signal, 1000)
        
        print(f"\n💰 Calculated Results (1000 units):")
        print(f"Pips to target: {pnl_data['pips_to_target']:.1f}")
        print(f"Pips to stop: {pnl_data['pips_to_stop']:.1f}")
        print(f"Potential profit: £{pnl_data['potential_profit']:.2f}")
        print(f"Potential loss: £{pnl_data['potential_loss']:.2f}")
        print(f"Risk:Reward: 1:{pnl_data['risk_reward_ratio']:.1f}")
        
        # Check if calculations are reasonable
        if pnl_data['pips_to_target'] > 100:
            print("⚠️  WARNING: Pips to target seems too high!")
        elif pnl_data['pips_to_target'] < 10:
            print("⚠️  WARNING: Pips to target seems too low!")
        else:
            print("✅ Pip calculations look reasonable")
        
        print("-" * 40)

if __name__ == "__main__":
    test_pip_calculations() 