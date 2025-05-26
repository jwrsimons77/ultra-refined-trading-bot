#!/usr/bin/env python3
"""
🚀 Start Background Forex Trading Bot
Simple script to launch the automated trading system
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

def main():
    """Start the background trading bot."""
    print("🚀 Starting James's Background Trading Bot...")
    print("=" * 50)
    
    # Change to the src directory
    src_dir = Path(__file__).parent / "src"
    if not src_dir.exists():
        print("❌ Error: src directory not found!")
        return
    
    os.chdir(src_dir)
    
    # Check if required files exist
    required_files = [
        "background_trader.py",
        "forex_signal_generator.py", 
        "oanda_trader.py",
        "simple_technical_analyzer.py"
    ]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Error: Required file {file} not found!")
            return
    
    print("✅ All required files found")
    print("🤖 Launching background trader...")
    print()
    print("📊 Trading Settings:")
    print("   • Minimum Confidence: 45%")
    print("   • Max Daily Trades: 8")
    print("   • Risk Per Trade: 3%")
    print("   • Scan Interval: 5 minutes")
    print("   • Max Concurrent Positions: 6")
    print()
    print("🔄 The bot will:")
    print("   • Scan for signals every 5 minutes")
    print("   • Auto-execute trades with 45%+ confidence")
    print("   • Trade during London, New York, and Tokyo sessions")
    print("   • Log all activity to background_trader.log")
    print()
    print("⚠️  Press Ctrl+C to stop the bot")
    print("=" * 50)
    
    try:
        # Start the background trader
        process = subprocess.Popen([
            sys.executable, "background_trader.py"
        ], cwd=src_dir)
        
        # Wait for the process
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping background trader...")
        if 'process' in locals():
            process.terminate()
            process.wait()
        print("✅ Background trader stopped successfully")
    except Exception as e:
        print(f"❌ Error starting background trader: {e}")

if __name__ == "__main__":
    main() 