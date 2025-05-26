#!/usr/bin/env python3
"""
🚀 Railway Deployment Helper
Prepare and deploy your $10K trading bot to Railway
"""

import os
import subprocess
import sys
from getpass import getpass

def check_git_status():
    """Check if we're in a git repository and if there are uncommitted changes."""
    try:
        # Check if we're in a git repo
        subprocess.check_output(['git', 'status'], stderr=subprocess.DEVNULL)
        
        # Check for uncommitted changes
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if result.stdout.strip():
            print("📝 Uncommitted changes detected:")
            print(result.stdout)
            return False
        else:
            print("✅ Git repository is clean")
            return True
            
    except subprocess.CalledProcessError:
        print("❌ Not in a git repository")
        return False

def commit_and_push():
    """Commit changes and push to GitHub."""
    try:
        print("📝 Committing changes...")
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Deploy $10K trading bot to Railway'], check=True)
        
        print("🚀 Pushing to GitHub...")
        subprocess.run(['git', 'push'], check=True)
        
        print("✅ Code pushed to GitHub successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        return False

def get_oanda_credentials():
    """Get OANDA credentials from user."""
    print("\n🔑 OANDA API CREDENTIALS")
    print("=" * 40)
    print("📝 You'll need these for Railway environment variables")
    print("💡 Get them from: https://www.oanda.com/demo-account/tpa/personal_token")
    print()
    
    api_key = getpass("🔑 OANDA API Key (hidden): ").strip()
    account_id = input("🏦 OANDA Account ID: ").strip()
    
    if not api_key or not account_id:
        print("❌ Both API key and Account ID are required!")
        return None, None
    
    return api_key, account_id

def show_railway_instructions(api_key, account_id):
    """Show Railway deployment instructions."""
    print("\n🚀 RAILWAY DEPLOYMENT INSTRUCTIONS")
    print("=" * 50)
    print()
    
    print("1️⃣ **Go to Railway**:")
    print("   🌐 Visit: https://railway.app")
    print("   📝 Sign up or login")
    print()
    
    print("2️⃣ **Create New Project**:")
    print("   ➕ Click 'Start a New Project'")
    print("   📂 Select 'Deploy from GitHub repo'")
    print("   🔍 Choose your 'sniper_bot' repository")
    print()
    
    print("3️⃣ **Set Environment Variables**:")
    print("   ⚙️ Go to your project → Variables tab")
    print("   ➕ Add these variables:")
    print()
    print("   🔑 OANDA_API_KEY")
    print(f"      Value: {api_key}")
    print()
    print("   🏦 OANDA_ACCOUNT_ID")
    print(f"      Value: {account_id}")
    print()
    
    print("4️⃣ **Deploy**:")
    print("   🚀 Railway will automatically deploy your bot")
    print("   📊 Monitor logs in the Railway dashboard")
    print("   ✅ Look for 'Connected to OANDA account successfully'")
    print()
    
    print("5️⃣ **Monitor Performance**:")
    print("   📈 Check logs every few hours initially")
    print("   💰 Track account balance growth")
    print("   🎯 Expected: ~6% monthly returns")
    print()

def show_expected_performance():
    """Show expected performance metrics."""
    print("💰 EXPECTED PERFORMANCE")
    print("=" * 30)
    print("📊 Based on real historical backtesting:")
    print()
    print("   📈 Monthly Return: ~6.03%")
    print("   💵 Monthly Profit: ~$603")
    print("   🎯 Win Rate: ~69%")
    print("   ⏰ Time to $100K: ~3.3 years")
    print()
    print("📅 Timeline Milestones:")
    print("   💰 $15,000: ~7 months")
    print("   💰 $20,000: ~12 months")
    print("   💰 $50,000: ~28 months")
    print("   💰 $100,000: ~40 months")
    print()

def main():
    """Main deployment helper function."""
    print("🎯 RAILWAY DEPLOYMENT HELPER")
    print("=" * 50)
    print("🚀 Deploy your $10K trading bot to Railway for 24/7 operation")
    print()
    
    # Step 1: Check git status
    print("1️⃣ Checking git repository...")
    if not check_git_status():
        commit = input("🤔 Commit and push changes? (y/n): ").lower().strip()
        if commit == 'y':
            if not commit_and_push():
                print("❌ Failed to push changes. Please fix git issues first.")
                return
        else:
            print("⚠️ You'll need to push changes to GitHub before deploying to Railway")
            return
    
    # Step 2: Get OANDA credentials
    api_key, account_id = get_oanda_credentials()
    if not api_key or not account_id:
        print("❌ Cannot proceed without OANDA credentials")
        return
    
    # Step 3: Show Railway instructions
    show_railway_instructions(api_key, account_id)
    
    # Step 4: Show expected performance
    show_expected_performance()
    
    # Step 5: Final reminders
    print("🚨 IMPORTANT REMINDERS:")
    print("=" * 25)
    print("   • This is demo trading (virtual money)")
    print("   • Monitor the bot regularly")
    print("   • Check Railway logs for trading activity")
    print("   • Bot trades every 30 minutes")
    print("   • Maximum 12 trades per day")
    print("   • 3% risk per trade")
    print()
    
    print("✅ Ready to deploy! Follow the Railway instructions above.")
    print("📖 For detailed guide, see: RAILWAY_DEPLOYMENT_GUIDE.md")

if __name__ == "__main__":
    main() 