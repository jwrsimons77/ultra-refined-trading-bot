#!/usr/bin/env python3
"""
Quick test for OANDA connection
"""

import os
import sys
sys.path.append('src')

def test_oanda_connection():
    """Test OANDA connection with provided credentials."""
    print("🌍 Testing OANDA Connection...")
    print("=" * 40)
    
    # Set credentials
    api_key = "fe92315bee29b117825fed529cf3fa99-173e927b8cdbb1fc244993e24e33fd93"
    account_id = "101-004-29067-001"  # Standard OANDA practice account format
    
    print(f"API Key: {api_key[:20]}...")
    print(f"Account ID: {account_id}")
    print()
    
    try:
        from forex_sniper_bot import ForexSniperBot
        
        print("✅ Forex bot imported successfully")
        
        # Initialize bot
        bot = ForexSniperBot(api_key, account_id, environment="practice")
        print("✅ Bot initialized")
        
        # Test account summary
        print("\n💰 Testing Account Summary...")
        account = bot.get_account_summary()
        if account:
            print(f"  Balance: ${account.get('balance', 'N/A'):,.2f}")
            print(f"  Currency: {account.get('currency', 'N/A')}")
            print(f"  Open Trades: {account.get('open_trades', 0)}")
            print("✅ Account summary retrieved")
        else:
            print("❌ Failed to get account summary")
        
        # Test price data
        print("\n💱 Testing Price Data...")
        price = bot.get_current_price('EUR_USD')
        if price:
            print(f"  EUR/USD: {price['bid']:.5f} / {price['ask']:.5f}")
            print(f"  Spread: {price['spread']:.5f}")
            print("✅ Price data retrieved")
        else:
            print("❌ Failed to get price data")
        
        # Test signal generation
        print("\n📊 Testing Signal Generation...")
        signals = bot.generate_forex_signals(confidence_threshold=0.3)
        print(f"✅ Generated {len(signals)} forex signals")
        
        for signal in signals[:2]:  # Show first 2 signals
            print(f"  📈 {signal.pair} {signal.signal_type} @ {signal.entry_price:.5f}")
            print(f"     Target: +{signal.pip_target} pips | Stop: -{signal.pip_stop} pips")
            print(f"     Confidence: {signal.confidence_score:.1%}")
        
        print("\n🎉 All tests passed! OANDA connection is working.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Run: pip install oandapyV20")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    test_oanda_connection() 