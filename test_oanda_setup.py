#!/usr/bin/env python3
"""
OANDA API Setup and Test Script
This script helps you get your correct account ID and test the connection
"""

import requests
import json

def test_oanda_connection(api_key):
    """Test OANDA connection and get account information."""
    print("🔧 Testing OANDA API Connection...")
    print("=" * 50)
    
    # OANDA practice environment URLs
    base_url = "https://api-fxpractice.oanda.com"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        # Step 1: Get list of accounts
        print("📋 Step 1: Getting your account list...")
        accounts_url = f"{base_url}/v3/accounts"
        
        response = requests.get(accounts_url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            accounts_data = response.json()
            print("✅ Successfully connected to OANDA!")
            print(f"Response: {json.dumps(accounts_data, indent=2)}")
            
            if 'accounts' in accounts_data and accounts_data['accounts']:
                account_id = accounts_data['accounts'][0]['id']
                print(f"\n🎯 Your correct Account ID is: {account_id}")
                
                # Step 2: Test account summary
                print(f"\n📊 Step 2: Testing account summary for {account_id}...")
                summary_url = f"{base_url}/v3/accounts/{account_id}/summary"
                
                summary_response = requests.get(summary_url, headers=headers)
                print(f"Summary Status Code: {summary_response.status_code}")
                
                if summary_response.status_code == 200:
                    summary_data = summary_response.json()
                    account = summary_data.get('account', {})
                    
                    print("✅ Account Summary Retrieved Successfully!")
                    print(f"Account ID: {account.get('id')}")
                    print(f"Currency: {account.get('currency')}")
                    print(f"Balance: {account.get('balance')}")
                    print(f"NAV: {account.get('NAV')}")
                    print(f"Margin Available: {account.get('marginAvailable')}")
                    
                    return account_id
                else:
                    print(f"❌ Failed to get account summary: {summary_response.text}")
            else:
                print("❌ No accounts found in response")
        else:
            print(f"❌ Failed to connect: {response.status_code}")
            print(f"Error: {response.text}")
            
            if response.status_code == 401:
                print("\n💡 This looks like an authentication error.")
                print("Please check your API key is correct.")
            elif response.status_code == 403:
                print("\n💡 This looks like a permissions error.")
                print("Make sure your API key has the right permissions.")
                
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
    
    return None

def main():
    """Main function to test OANDA setup."""
    print("🌍 OANDA API Setup Helper")
    print("=" * 50)
    
    # Your API key
    api_key = "fe92315bee29b117825fed529cf3fa99-173e927b8cdbb1fc244993e24e33fd93"
    
    print(f"Using API Key: {api_key[:20]}...")
    print("Testing with PRACTICE environment")
    print()
    
    # Test the connection
    account_id = test_oanda_connection(api_key)
    
    if account_id:
        print("\n" + "=" * 50)
        print("🎉 SUCCESS! Your OANDA connection is working!")
        print("=" * 50)
        print(f"✅ API Key: {api_key}")
        print(f"✅ Account ID: {account_id}")
        print(f"✅ Environment: practice")
        print()
        print("📝 Use these credentials in your forex app:")
        print(f'OANDA_API_KEY = "{api_key}"')
        print(f'OANDA_ACCOUNT_ID = "{account_id}"')
        print('OANDA_ENVIRONMENT = "practice"')
    else:
        print("\n" + "=" * 50)
        print("❌ OANDA connection failed!")
        print("=" * 50)
        print("Please check:")
        print("1. Your API key is correct")
        print("2. You have a practice account set up")
        print("3. Your API key has the right permissions")
        print()
        print("To get your API key:")
        print("1. Log in to OANDA fxTrade")
        print("2. Go to 'Manage API Access'")
        print("3. Generate a new personal access token")

if __name__ == "__main__":
    main() 