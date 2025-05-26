#!/usr/bin/env python3
"""
🤖 Background Forex Trading Bot
Runs continuously and auto-executes high-confidence signals
"""

import time
import logging
from datetime import datetime, time as dt_time
import pytz
from typing import List
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from forex_signal_generator import ForexSignalGenerator
from oanda_trader import OANDATrader
from simple_technical_analyzer import SimpleTechnicalAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('background_trader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BackgroundTrader:
    """Automated background trading system."""
    
    def __init__(self):
        """Initialize the background trader."""
        self.signal_generator = ForexSignalGenerator()
        
        # Initialize OANDA trader with credentials
        api_key = "fe92315bee29b117825fed529cf3fa99-173e927b8cdbb1fc244993e24e33fd93"
        account_id = "101-004-31788297-001"
        self.trader = OANDATrader(api_key, account_id)
        
        self.running = False
        
        # Trading parameters - OPTIMIZED FOR PROFITABILITY
        self.min_confidence = 0.45  # Lowered from 0.75 to catch more opportunities
        self.max_daily_trades = 8   # Increased from 3 to allow more trading
        self.risk_per_trade = 3     # 3% risk per trade (more aggressive)
        self.max_concurrent_positions = 6  # Allow more positions
        
        # Tracking
        self.daily_trades = 0
        self.last_trade_date = None
        self.executed_signals = []
        
        logger.info("🤖 Background Trader initialized")
        logger.info(f"📊 Settings: Min Confidence={self.min_confidence:.1%}, Max Daily Trades={self.max_daily_trades}, Risk={self.risk_per_trade}%")
    
    def is_market_open(self) -> bool:
        """Check if forex market is open."""
        utc_now = datetime.now(pytz.UTC)
        current_time = utc_now.time()
        current_day = utc_now.weekday()  # 0=Monday, 6=Sunday
        
        # Forex market is closed on weekends
        if current_day >= 5:  # Saturday (5) or Sunday (6)
            return False
        
        # Major forex market hours (UTC) - EXTENDED HOURS
        # London: 08:00-17:00, New York: 13:00-22:00, Tokyo: 00:00-09:00
        london_session = dt_time(8, 0) <= current_time <= dt_time(17, 0)
        ny_session = dt_time(13, 0) <= current_time <= dt_time(22, 0)
        tokyo_session = dt_time(0, 0) <= current_time <= dt_time(9, 0)
        
        # Market is open during any major session
        market_open = london_session or ny_session or tokyo_session
        
        if market_open:
            session = "London" if london_session else ("New York" if ny_session else "Tokyo")
            logger.info(f"🌍 Market OPEN - {session} session active")
        
        return market_open
    
    def reset_daily_counters(self):
        """Reset daily trading counters."""
        today = datetime.now().date()
        if self.last_trade_date != today:
            self.daily_trades = 0
            self.last_trade_date = today
            logger.info(f"📅 New trading day: {today} - Counters reset")
    
    def can_trade(self) -> bool:
        """Check if we can execute more trades today."""
        self.reset_daily_counters()
        
        # Check daily limits
        if self.daily_trades >= self.max_daily_trades:
            logger.info(f"🛑 Daily trade limit reached ({self.daily_trades}/{self.max_daily_trades})")
            return False
        
        # Check concurrent positions
        try:
            positions = self.trader.get_open_positions()
            if len(positions) >= self.max_concurrent_positions:
                logger.info(f"🛑 Max concurrent positions reached ({len(positions)}/{self.max_concurrent_positions})")
                return False
        except Exception as e:
            logger.error(f"Error checking positions: {e}")
            return False
        
        return True
    
    def calculate_position_size(self, signal, account_balance: float) -> int:
        """Calculate optimal position size based on risk management."""
        try:
            # Calculate stop loss in pips
            if 'JPY' in signal.pair:
                stop_pips = abs(signal.entry_price - signal.stop_loss) / 0.01
            else:
                stop_pips = abs(signal.entry_price - signal.stop_loss) / 0.0001
            
            # Risk amount in account currency
            risk_amount = account_balance * (self.risk_per_trade / 100)
            
            # Calculate position size
            # For 1000 units, pip value is roughly $0.10 for most pairs
            pip_value = 0.10 if 'JPY' not in signal.pair else 1.0
            
            # Position size = Risk Amount / (Stop Loss Pips * Pip Value)
            position_size = int(risk_amount / (stop_pips * pip_value))
            
            # Ensure minimum position size
            position_size = max(1000, position_size)
            
            # Cap maximum position size for safety
            max_position = int(account_balance * 0.1)  # Max 10% of account as position size
            position_size = min(position_size, max_position)
            
            logger.info(f"💰 Position sizing: Risk=${risk_amount:.2f}, Stop={stop_pips:.1f} pips, Size={position_size:,} units")
            
            return position_size
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 1000  # Default fallback
    
    def execute_signal(self, signal) -> bool:
        """Execute a trading signal."""
        try:
            # Get account info
            account_summary = self.trader.get_account_summary()
            if not account_summary:
                logger.error("Could not get account summary")
                return False
            
            account_balance = account_summary['balance']
            
            # Calculate position size
            position_size = self.calculate_position_size(signal, account_balance)
            
            # Execute the trade
            order_id = self.trader.execute_signal(signal, position_size)
            
            if order_id:
                self.daily_trades += 1
                self.executed_signals.append({
                    'timestamp': datetime.now(),
                    'pair': signal.pair,
                    'type': signal.signal_type,
                    'confidence': signal.confidence,
                    'entry_price': signal.entry_price,
                    'target_price': signal.target_price,
                    'stop_loss': signal.stop_loss,
                    'position_size': position_size,
                    'order_id': order_id
                })
                
                logger.info(f"""
🎯 TRADE EXECUTED SUCCESSFULLY! 🎯

Pair: {signal.pair}
Type: {signal.signal_type}
Confidence: {signal.confidence:.1%}
Entry: {signal.entry_price:.5f}
Target: {signal.target_price:.5f} ({signal.pips_target} pips)
Stop: {signal.stop_loss:.5f} ({signal.pips_risk} pips)
Position Size: {position_size:,} units
Order ID: {order_id}
Daily Trades: {self.daily_trades}/{self.max_daily_trades}
                """)
                
                return True
            else:
                logger.error(f"Failed to execute trade for {signal.pair}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing signal: {e}")
            return False
    
    def scan_and_trade(self):
        """Scan for signals and execute high-confidence trades."""
        try:
            logger.info("🔍 Scanning for trading opportunities...")
            
            # Generate signals with lower confidence threshold
            signals = self.signal_generator.generate_forex_signals(
                max_signals=10,  # Check more signals
                min_confidence=self.min_confidence
            )
            
            if not signals:
                logger.info("📊 No signals found meeting criteria")
                return
            
            logger.info(f"📊 Found {len(signals)} potential signals")
            
            # Filter for high-confidence signals
            high_confidence_signals = [s for s in signals if s.confidence >= self.min_confidence]
            
            if not high_confidence_signals:
                logger.info(f"📊 No signals above {self.min_confidence:.1%} confidence threshold")
                return
            
            logger.info(f"🎯 {len(high_confidence_signals)} signals above confidence threshold")
            
            # Execute signals in order of confidence
            executed_count = 0
            for signal in high_confidence_signals:
                if not self.can_trade():
                    logger.info("🛑 Cannot execute more trades (limits reached)")
                    break
                
                logger.info(f"🎯 Attempting to execute: {signal.pair} {signal.signal_type} ({signal.confidence:.1%})")
                
                if self.execute_signal(signal):
                    executed_count += 1
                    # Wait a bit between executions
                    time.sleep(2)
                else:
                    logger.warning(f"⚠️ Failed to execute {signal.pair} {signal.signal_type}")
            
            if executed_count > 0:
                logger.info(f"✅ Successfully executed {executed_count} trades this scan")
            else:
                logger.info("📊 No trades executed this scan")
                
        except Exception as e:
            logger.error(f"Error in scan_and_trade: {e}")
    
    def run(self, scan_interval: int = 300):  # 5 minutes default
        """Run the background trader continuously."""
        logger.info(f"🚀 Starting background trader (scan every {scan_interval} seconds)")
        self.running = True
        
        while self.running:
            try:
                # Check if market is open
                if not self.is_market_open():
                    logger.info("💤 Market closed - sleeping for 30 minutes")
                    time.sleep(1800)  # Sleep for 30 minutes when market is closed
                    continue
                
                # Check if we can trade
                if not self.can_trade():
                    logger.info("🛑 Trading limits reached - sleeping for 1 hour")
                    time.sleep(3600)  # Sleep for 1 hour if limits reached
                    continue
                
                # Scan and trade
                self.scan_and_trade()
                
                # Wait for next scan
                logger.info(f"⏰ Waiting {scan_interval} seconds until next scan...")
                time.sleep(scan_interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 Received stop signal - shutting down gracefully")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                logger.info("⏰ Sleeping 60 seconds before retry...")
                time.sleep(60)
        
        logger.info("🏁 Background trader stopped")
    
    def stop(self):
        """Stop the background trader."""
        self.running = False
        logger.info("🛑 Stop signal sent to background trader")
    
    def get_status(self) -> dict:
        """Get current status of the background trader."""
        return {
            'running': self.running,
            'daily_trades': self.daily_trades,
            'max_daily_trades': self.max_daily_trades,
            'executed_signals': len(self.executed_signals),
            'last_trade_date': self.last_trade_date,
            'market_open': self.is_market_open(),
            'can_trade': self.can_trade()
        }

def main():
    """Main function to run the background trader."""
    trader = BackgroundTrader()
    
    try:
        # Run with 5-minute scan intervals
        trader.run(scan_interval=300)
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down background trader...")
        trader.stop()

if __name__ == "__main__":
    main() 