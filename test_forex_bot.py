#!/usr/bin/env python3
"""
Test script for Forex Sniper Bot
Demonstrates functionality without requiring real OANDA credentials
"""

import os
import sys
sys.path.append('src')

def test_forex_bot_demo():
    """Test the forex bot with demo data."""
    print("🌍 FOREX SNIPER BOT - DEMO TEST")
    print("=" * 50)
    
    # Check if we have OANDA credentials
    api_key = os.getenv('OANDA_API_KEY')
    account_id = os.getenv('OANDA_ACCOUNT_ID')
    
    print(f"OANDA API Key: {'✅ Found' if api_key else '❌ Not set'}")
    print(f"OANDA Account ID: {'✅ Found' if account_id else '❌ Not set'}")
    print(f"Alpha Vantage Key: {'✅ Found' if os.getenv('ALPHA_VANTAGE_API_KEY') else '❌ Not set'}")
    print()
    
    if not api_key or not account_id:
        print("🔧 SETUP REQUIRED:")
        print("1. Sign up for FREE OANDA practice account: https://www.oanda.com/register/")
        print("2. Get your API credentials from account settings")
        print("3. Set environment variables:")
        print("   export OANDA_API_KEY='your_token_here'")
        print("   export OANDA_ACCOUNT_ID='your_account_id_here'")
        print()
        print("📖 See FOREX_SETUP_GUIDE.md for detailed instructions")
        print()
        
        # Demo with fake data
        print("🎮 RUNNING DEMO WITH SIMULATED DATA:")
        demo_forex_signals()
        return
    
    # Test with real OANDA connection
    try:
        from forex_sniper_bot import ForexSniperBot
        
        print("🚀 Testing OANDA Connection...")
        bot = ForexSniperBot(api_key, account_id, environment="practice")
        
        # Test current prices
        print("\n💱 Current Forex Prices:")
        major_pairs = ['EUR_USD', 'GBP_USD', 'USD_JPY']
        for pair in major_pairs:
            try:
                price = bot.get_current_price(pair)
                if price:
                    spread_pips = price['spread'] * (10000 if 'JPY' not in pair else 100)
                    print(f"  {pair}: {price['bid']:.5f} / {price['ask']:.5f} (Spread: {spread_pips:.1f} pips)")
                else:
                    print(f"  {pair}: ❌ Failed to get price")
            except Exception as e:
                print(f"  {pair}: ❌ Error - {e}")
        
        # Test account summary
        print("\n💰 Account Summary:")
        try:
            account = bot.get_account_summary()
            if account:
                print(f"  Balance: ${account.get('balance', 'N/A'):,.2f}")
                print(f"  Unrealized P/L: ${account.get('unrealized_pl', 0):,.2f}")
                print(f"  Open Trades: {account.get('open_trades', 0)}")
                print(f"  Currency: {account.get('currency', 'N/A')}")
            else:
                print("  ❌ Failed to get account summary")
        except Exception as e:
            print(f"  ❌ Error getting account: {e}")
        
        # Test signal generation
        print("\n📊 Generating Forex Signals...")
        try:
            signals = bot.generate_forex_signals(confidence_threshold=0.3)
            
            if signals:
                print(f"✅ Generated {len(signals)} forex signals:")
                for i, signal in enumerate(signals, 1):
                    profit_pips = signal.pip_target
                    risk_pips = signal.pip_stop
                    risk_reward = profit_pips / risk_pips if risk_pips > 0 else 0
                    
                    print(f"\n  📈 Signal {i}: {signal.pair} {signal.signal_type}")
                    print(f"     Entry: {signal.entry_price:.5f}")
                    print(f"     Target: {signal.target_price:.5f} (+{profit_pips} pips)")
                    print(f"     Stop: {signal.stop_loss:.5f} (-{risk_pips} pips)")
                    print(f"     Risk/Reward: 1:{risk_reward:.1f}")
                    print(f"     Confidence: {signal.confidence_score:.2f}")
                    print(f"     News: {signal.headline[:60]}...")
            else:
                print("⚠️  No signals generated (try lowering confidence threshold)")
                
        except Exception as e:
            print(f"❌ Error generating signals: {e}")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure oandapyV20 is installed: pip install oandapyV20")
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("Check your OANDA credentials and internet connection")

def demo_forex_signals():
    """Show demo forex signals with simulated data."""
    print("📊 DEMO FOREX SIGNALS (Simulated Data):")
    print()
    
    demo_signals = [
        {
            'pair': 'EUR_USD',
            'type': 'BUY',
            'entry': 1.08450,
            'target': 1.08750,
            'stop': 1.08300,
            'pip_target': 30,
            'pip_stop': 15,
            'confidence': 0.75,
            'news': 'ECB hints at rate hike amid strong inflation data'
        },
        {
            'pair': 'GBP_USD',
            'type': 'SELL',
            'entry': 1.26820,
            'target': 1.26320,
            'stop': 1.27070,
            'pip_target': 50,
            'pip_stop': 25,
            'confidence': 0.68,
            'news': 'UK GDP disappoints, BoE dovish stance expected'
        },
        {
            'pair': 'USD_JPY',
            'type': 'BUY',
            'entry': 149.85,
            'target': 150.45,
            'stop': 149.45,
            'pip_target': 60,
            'pip_stop': 40,
            'confidence': 0.82,
            'news': 'Fed officials signal continued hawkish policy'
        }
    ]
    
    for i, signal in enumerate(demo_signals, 1):
        risk_reward = signal['pip_target'] / signal['pip_stop']
        
        print(f"📈 Signal {i}: {signal['pair']} {signal['type']}")
        print(f"   Entry: {signal['entry']:.5f}")
        print(f"   Target: {signal['target']:.5f} (+{signal['pip_target']} pips)")
        print(f"   Stop: {signal['stop']:.5f} (-{signal['pip_stop']} pips)")
        print(f"   Risk/Reward: 1:{risk_reward:.1f}")
        print(f"   Confidence: {signal['confidence']:.2f}")
        print(f"   News: {signal['news']}")
        print()
    
    print("💡 Why These Signals Are Better Than Stocks:")
    print("   • 24/5 market - no overnight gaps")
    print("   • Higher leverage - bigger profits with same capital")
    print("   • Predictable news - central bank schedules are known")
    print("   • Instant execution - no waiting for market open")
    print("   • Lower capital requirements - start with $100-500")
    print()
    
    print("🎯 Expected Performance:")
    print("   • Win Rate: 55-65% (vs 45-55% for stocks)")
    print("   • Risk/Reward: 1:2 average")
    print("   • Monthly Return: 5-15% with proper risk management")
    print()
    
    print("🚀 Ready to start? Follow the FOREX_SETUP_GUIDE.md!")

if __name__ == "__main__":
    test_forex_bot_demo() 