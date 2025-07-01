#!/usr/bin/env python3
"""
Export and analyze Railway logs for the past 24 hours
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
import re
from collections import defaultdict

def get_railway_logs(service_id, token, hours=24):
    """Fetch Railway logs using Railway CLI or API."""
    
    # Try using Railway CLI first
    try:
        import subprocess
        print("🔍 Attempting to fetch logs via Railway CLI...")
        
        # Get logs for the specified hours
        cmd = f"railway logs --service {service_id} --hours {hours}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Successfully fetched logs via Railway CLI")
            return result.stdout
        else:
            print(f"❌ Railway CLI failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Railway CLI not available: {e}")
    
    # Fallback: Try Railway API
    try:
        print("🔍 Attempting to fetch logs via Railway API...")
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Railway API endpoint for logs
        url = f"https://backboard.railway.app/graphql/v2"
        
        # GraphQL query for logs
        query = """
        query getLogs($serviceId: String!, $limit: Int!) {
            logs(serviceId: $serviceId, limit: $limit) {
                id
                message
                timestamp
                level
            }
        }
        """
        
        variables = {
            "serviceId": service_id,
            "limit": 1000  # Get last 1000 log entries
        }
        
        response = requests.post(url, headers=headers, json={
            'query': query,
            'variables': variables
        })
        
        if response.status_code == 200:
            data = response.json()
            logs = data.get('data', {}).get('logs', [])
            
            # Convert to readable format
            log_text = ""
            for log in logs:
                timestamp = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
                log_text += f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {log['level']} - {log['message']}\n"
            
            print("✅ Successfully fetched logs via Railway API")
            return log_text
        else:
            print(f"❌ Railway API failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Railway API failed: {e}")
    
    return None

def analyze_logs(log_text):
    """Analyze the logs for key patterns and issues."""
    
    if not log_text:
        print("❌ No logs to analyze")
        return
    
    print("\n" + "="*80)
    print("📊 RAILWAY LOGS ANALYSIS - PAST 24 HOURS")
    print("="*80)
    
    # Parse logs into structured data
    log_entries = []
    for line in log_text.split('\n'):
        if line.strip():
            # Parse timestamp and message
            match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (\w+) - (.+)', line)
            if match:
                timestamp, level, message = match.groups()
                log_entries.append({
                    'timestamp': timestamp,
                    'level': level,
                    'message': message
                })
    
    print(f"📋 Total log entries: {len(log_entries)}")
    
    # Key patterns to look for
    patterns = {
        'bot_startup': r'🚀 ULTRA REFINED RAILWAY TRADING BOT',
        'version_check': r'📌 OandaTrader Version: v2\.1',
        'market_prices': r'📊 Current market prices for',
        'trade_attempts': r'🔄 Placing order:',
        'trade_success': r'✅ Order placed successfully',
        'trade_failure': r'❌ Order was cancelled immediately',
        'take_profit_error': r'TAKE_PROFIT_ON_FILL_LOSS',
        'signal_generation': r'📡 Signal found for',
        'sync_debug': r'🔄 SYNC DEBUG INFO',
        'error_patterns': r'❌|ERROR|Exception|Traceback',
        'warning_patterns': r'⚠️|WARNING',
        'margin_issues': r'margin|Margin',
        'connection_issues': r'connection|Connection|timeout|Timeout'
    }
    
    # Analyze patterns
    analysis = defaultdict(list)
    
    for entry in log_entries:
        for pattern_name, pattern in patterns.items():
            if re.search(pattern, entry['message']):
                analysis[pattern_name].append(entry)
    
    # Print analysis
    print(f"\n🔍 PATTERN ANALYSIS:")
    for pattern_name, entries in analysis.items():
        print(f"   {pattern_name}: {len(entries)} occurrences")
        if entries:
            # Show first few examples
            for entry in entries[:3]:
                print(f"     {entry['timestamp']} - {entry['message'][:80]}...")
            if len(entries) > 3:
                print(f"     ... and {len(entries) - 3} more")
    
    # Check for critical issues
    print(f"\n🚨 CRITICAL ISSUES:")
    critical_issues = []
    
    # Check if bot started properly
    if not analysis['bot_startup']:
        critical_issues.append("❌ Bot startup message not found - bot may not be running")
    
    # Check if new version is running
    if not analysis['version_check']:
        critical_issues.append("❌ Version v2.1 not found - old code may still be running")
    
    # Check for TAKE_PROFIT_ON_FILL_LOSS errors
    if analysis['take_profit_error']:
        critical_issues.append(f"⚠️ {len(analysis['take_profit_error'])} TAKE_PROFIT_ON_FILL_LOSS errors found")
    
    # Check for connection issues
    if analysis['connection_issues']:
        critical_issues.append(f"⚠️ {len(analysis['connection_issues'])} connection issues found")
    
    # Check for margin issues
    if analysis['margin_issues']:
        critical_issues.append(f"⚠️ {len(analysis['margin_issues'])} margin-related issues found")
    
    if critical_issues:
        for issue in critical_issues:
            print(f"   {issue}")
    else:
        print("   ✅ No critical issues detected")
    
    # Trading activity summary
    print(f"\n📈 TRADING ACTIVITY SUMMARY:")
    print(f"   Trade attempts: {len(analysis['trade_attempts'])}")
    print(f"   Successful trades: {len(analysis['trade_success'])}")
    print(f"   Failed trades: {len(analysis['trade_failure'])}")
    print(f"   Signals generated: {len(analysis['signal_generation'])}")
    
    # Calculate success rate
    total_trades = len(analysis['trade_attempts'])
    successful_trades = len(analysis['trade_success'])
    if total_trades > 0:
        success_rate = (successful_trades / total_trades) * 100
        print(f"   Success rate: {success_rate:.1f}%")
    
    # Recent activity (last 10 entries)
    print(f"\n🕒 RECENT ACTIVITY (Last 10 entries):")
    for entry in log_entries[-10:]:
        print(f"   {entry['timestamp']} - {entry['message']}")
    
    # Save logs to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"railway_logs_analysis_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write("RAILWAY LOGS ANALYSIS\n")
        f.write("="*50 + "\n\n")
        f.write(f"Analysis timestamp: {datetime.now()}\n")
        f.write(f"Total log entries: {len(log_entries)}\n\n")
        
        f.write("PATTERN ANALYSIS:\n")
        for pattern_name, entries in analysis.items():
            f.write(f"{pattern_name}: {len(entries)} occurrences\n")
        
        f.write("\nCRITICAL ISSUES:\n")
        for issue in critical_issues:
            f.write(f"{issue}\n")
        
        f.write("\nFULL LOGS:\n")
        f.write("="*50 + "\n")
        f.write(log_text)
    
    print(f"\n💾 Analysis saved to: {filename}")
    
    return analysis

def main():
    """Main function to export and analyze Railway logs."""
    
    # You'll need to provide these values
    print("🔧 RAILWAY LOGS EXPORTER")
    print("="*50)
    
    # Get Railway service ID
    service_id = input("Enter Railway service ID (or press Enter to skip): ").strip()
    
    # Get Railway token
    token = input("Enter Railway token (or press Enter to skip): ").strip()
    
    if not service_id or not token:
        print("\n📋 MANUAL LOG EXPORT INSTRUCTIONS:")
        print("1. Go to your Railway dashboard")
        print("2. Select your trading bot service")
        print("3. Click on 'Logs' tab")
        print("4. Set time range to 'Last 24 hours'")
        print("5. Copy all logs and save to a file")
        print("6. Run this script with the log file")
        
        # Alternative: Read from file
        log_file = input("\nEnter path to log file (or press Enter to exit): ").strip()
        if log_file and os.path.exists(log_file):
            with open(log_file, 'r') as f:
                log_text = f.read()
            analyze_logs(log_text)
        return
    
    # Fetch logs
    print(f"\n🔍 Fetching logs for service {service_id}...")
    log_text = get_railway_logs(service_id, token, hours=24)
    
    if log_text:
        analyze_logs(log_text)
    else:
        print("❌ Failed to fetch logs. Please check your credentials and try again.")

if __name__ == "__main__":
    main() 