#!/usr/bin/env python3
"""
🚀 Live Trading Setup Script
Configure OANDA credentials and start live trading
"""

import os
import sys
import subprocess
from getpass import getpass

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = ['schedule', 'requests', 'yfinance', 'pandas', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - MISSING")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ All dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies. Please install manually:")
            print(f"   pip install {' '.join(missing_packages)}")
            return False
    
    return True

def setup_oanda_credentials():
    """Setup OANDA API credentials."""
    print("\n🔑 OANDA API CREDENTIALS SETUP")
    print("=" * 50)
    print("📝 You need your OANDA API key and account ID")
    print("💡 Get them from: https://www.oanda.com/demo-account/tpa/personal_token")
    print()
    
    # Check if credentials already exist
    existing_api_key = os.getenv('OANDA_API_KEY')
    existing_account_id = os.getenv('OANDA_ACCOUNT_ID')
    
    if existing_api_key and existing_account_id:
        print(f"✅ Found existing credentials:")
        print(f"   API Key: {existing_api_key[:10]}...")
        print(f"   Account ID: {existing_account_id}")
        
        use_existing = input("\n🤔 Use existing credentials? (y/n): ").lower().strip()
        if use_existing == 'y':
            return existing_api_key, existing_account_id
    
    # Get new credentials
    print("\n📝 Enter your OANDA credentials:")
    api_key = getpass("🔑 API Key (hidden): ").strip()
    account_id = input("🏦 Account ID: ").strip()
    
    if not api_key or not account_id:
        print("❌ Both API key and Account ID are required!")
        return None, None
    
    # Set environment variables for current session
    os.environ['OANDA_API_KEY'] = api_key
    os.environ['OANDA_ACCOUNT_ID'] = account_id
    
    # Create .env file for persistence
    env_content = f"""# OANDA API Credentials
OANDA_API_KEY={api_key}
OANDA_ACCOUNT_ID={account_id}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Credentials saved to .env file")
    print("💡 Add this to your shell profile for persistence:")
    print(f"   export OANDA_API_KEY='{api_key}'")
    print(f"   export OANDA_ACCOUNT_ID='{account_id}'")
    
    return api_key, account_id

def test_connection(api_key: str, account_id: str):
    """Test connection to OANDA API."""
    print("\n🔗 Testing OANDA connection...")
    
    try:
        sys.path.append('src')
        from oanda_trader import OANDATrader
        
        trader = OANDATrader(api_key, account_id)
        account_info = trader.get_account_info()
        
        if account_info:
            balance = float(account_info.get('balance', 0))
            currency = account_info.get('currency', 'USD')
            
            print(f"✅ Connection successful!")
            print(f"💰 Account Balance: {balance:,.2f} {currency}")
            print(f"🏦 Account ID: {account_id}")
            return True
        else:
            print("❌ Connection failed - Invalid response")
            return False
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def show_trading_parameters():
    """Show the trading parameters that will be used."""
    print("\n📊 TRADING PARAMETERS")
    print("=" * 30)
    print("🎯 Minimum Confidence: 45%")
    print("💰 Risk per Trade: 3%")
    print("📈 Max Concurrent Trades: 8")
    print("📅 Max Daily Trades: 12")
    print("⏰ Trading Frequency: Every 30 minutes")
    print("💱 Currency Pairs: EUR/USD, GBP/USD, USD/JPY, USD/CHF, AUD/USD, USD/CAD, NZD/USD")
    print()

def start_live_trading():
    """Start the live trading bot."""
    print("🚀 STARTING LIVE TRADING BOT")
    print("=" * 40)
    print("⚠️  IMPORTANT REMINDERS:")
    print("   • This is live trading with real money")
    print("   • Monitor the bot regularly")
    print("   • Check live_trading.log for detailed logs")
    print("   • Press Ctrl+C to stop the bot")
    print()
    
    confirm = input("🤔 Are you ready to start live trading? (yes/no): ").lower().strip()
    
    if confirm != 'yes':
        print("⏸️ Live trading cancelled")
        return False
    
    print("\n🚀 Starting live trading bot...")
    print("📊 Monitor progress in live_trading.log")
    print("🛑 Press Ctrl+C to stop")
    print()
    
    try:
        # Import and run the live trading bot
        sys.path.append('src')
        from live_trading_bot import main as run_live_bot
        run_live_bot()
        
    except KeyboardInterrupt:
        print("\n🛑 Live trading stopped by user")
        return True
    except Exception as e:
        print(f"\n❌ Error starting live trading: {e}")
        return False

def main():
    """Main setup function."""
    print("🎯 LIVE TRADING BOT SETUP")
    print("=" * 50)
    print("🚀 Setting up your $10,000 virtual trading account")
    print()
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("❌ Setup failed - missing dependencies")
        return
    
    # Step 2: Setup credentials
    api_key, account_id = setup_oanda_credentials()
    if not api_key or not account_id:
        print("❌ Setup failed - invalid credentials")
        return
    
    # Step 3: Test connection
    if not test_connection(api_key, account_id):
        print("❌ Setup failed - connection test failed")
        return
    
    # Step 4: Show trading parameters
    show_trading_parameters()
    
    # Step 5: Start live trading
    start_live_trading()

if __name__ == "__main__":
    main() 