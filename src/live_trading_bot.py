#!/usr/bin/env python3
"""
🚀 Live Trading Bot - $10,000 Virtual Account
Real-time trading with OANDA using optimized signals
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
import logging
from datetime import datetime, timedelta
from oanda_trader import OANDATrader
from forex_signal_generator import ForexSignalGenerator
from simple_technical_analyzer import SimpleTechnicalAnalyzer
import schedule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('live_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LiveTradingBot:
    """Live trading bot for $10,000 virtual account."""
    
    def __init__(self, api_key: str, account_id: str):
        """Initialize the live trading bot."""
        self.trader = OANDATrader(api_key, account_id)
        self.signal_generator = ForexSignalGenerator()
        self.technical_analyzer = SimpleTechnicalAnalyzer()
        
        # Trading parameters (optimized from backtests)
        self.pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD']
        self.min_confidence = 0.45  # 45% minimum confidence
        self.risk_per_trade = 0.03  # 3% risk per trade
        self.max_concurrent_trades = 8
        self.max_daily_trades = 12
        
        # Track daily trades
        self.daily_trades = 0
        self.last_trade_date = None
        
        logger.info("🚀 Live Trading Bot initialized")
        logger.info(f"📊 Trading pairs: {', '.join(self.pairs)}")
        logger.info(f"🎯 Min confidence: {self.min_confidence*100:.0f}%")
        logger.info(f"💰 Risk per trade: {self.risk_per_trade*100:.0f}%")
    
    def reset_daily_counters(self):
        """Reset daily trade counters if new day."""
        today = datetime.now().date()
        if self.last_trade_date != today:
            self.daily_trades = 0
            self.last_trade_date = today
            logger.info(f"📅 New trading day: {today}")
    
    def get_account_info(self):
        """Get current account information."""
        try:
            account_info = self.trader.get_account_info()
            balance = float(account_info.get('balance', 0))
            nav = float(account_info.get('NAV', 0))
            margin_used = float(account_info.get('marginUsed', 0))
            margin_available = float(account_info.get('marginAvailable', 0))
            
            logger.info(f"💰 Account Balance: ${balance:,.2f}")
            logger.info(f"📊 NAV: ${nav:,.2f}")
            logger.info(f"📈 Margin Used: ${margin_used:,.2f}")
            logger.info(f"📉 Margin Available: ${margin_available:,.2f}")
            
            return {
                'balance': balance,
                'nav': nav,
                'margin_used': margin_used,
                'margin_available': margin_available
            }
        except Exception as e:
            logger.error(f"❌ Error getting account info: {e}")
            return None
    
    def get_open_positions(self):
        """Get current open positions."""
        try:
            positions = self.trader.get_positions()
            open_positions = []
            
            for position in positions:
                if float(position.get('long', {}).get('units', 0)) != 0 or float(position.get('short', {}).get('units', 0)) != 0:
                    open_positions.append(position)
            
            logger.info(f"📊 Open positions: {len(open_positions)}")
            return open_positions
        except Exception as e:
            logger.error(f"❌ Error getting positions: {e}")
            return []
    
    def calculate_position_size(self, account_balance: float, pair: str):
        """Calculate position size based on risk management."""
        risk_amount = account_balance * self.risk_per_trade
        
        # Estimate pip value (simplified)
        if 'JPY' in pair:
            pip_value = 0.01  # For JPY pairs
        else:
            pip_value = 0.0001  # For other pairs
        
        # Assume 20 pip stop loss
        stop_loss_pips = 20
        position_size = int(risk_amount / (stop_loss_pips * pip_value))
        
        # Ensure minimum position size
        min_size = 1000
        max_size = 100000  # Maximum position size
        
        position_size = max(min_size, min(position_size, max_size))
        
        logger.info(f"📊 Position size for {pair}: {position_size:,} units")
        return position_size
    
    def execute_trade(self, signal: dict, account_balance: float):
        """Execute a trade based on signal."""
        try:
            pair = signal['pair']
            action = signal['action']
            confidence = signal['confidence']
            
            # Calculate position size
            position_size = self.calculate_position_size(account_balance, pair)
            
            # Set stop loss and take profit (simplified)
            if 'JPY' in pair:
                stop_loss_pips = 20
                take_profit_pips = 40
            else:
                stop_loss_pips = 20
                take_profit_pips = 40
            
            logger.info(f"🎯 Executing {action} trade for {pair}")
            logger.info(f"📊 Confidence: {confidence:.1%}")
            logger.info(f"💰 Position size: {position_size:,} units")
            
            # Execute the trade
            result = self.trader.place_order(
                pair=pair,
                units=position_size if action == 'BUY' else -position_size,
                order_type='MARKET',
                stop_loss_pips=stop_loss_pips,
                take_profit_pips=take_profit_pips
            )
            
            if result and 'orderFillTransaction' in result:
                trade_id = result['orderFillTransaction']['id']
                price = float(result['orderFillTransaction']['price'])
                
                logger.info(f"✅ Trade executed successfully!")
                logger.info(f"📊 Trade ID: {trade_id}")
                logger.info(f"💰 Entry price: {price}")
                
                self.daily_trades += 1
                return True
            else:
                logger.error(f"❌ Trade execution failed: {result}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error executing trade: {e}")
            return False
    
    def scan_for_signals(self):
        """Scan all pairs for trading signals."""
        logger.info("🔍 Scanning for trading signals...")
        
        signals = []
        for pair in self.pairs:
            try:
                # Generate signal for this pair
                signal = self.signal_generator.generate_signal(pair)
                
                if signal and signal.get('confidence', 0) >= self.min_confidence:
                    signals.append(signal)
                    logger.info(f"🎯 Signal found: {pair} {signal['action']} ({signal['confidence']:.1%})")
                
            except Exception as e:
                logger.error(f"❌ Error generating signal for {pair}: {e}")
        
        logger.info(f"📊 Found {len(signals)} qualifying signals")
        return signals
    
    def trading_session(self):
        """Execute one trading session."""
        logger.info("🚀 Starting trading session...")
        
        # Reset daily counters
        self.reset_daily_counters()
        
        # Check if we've hit daily trade limit
        if self.daily_trades >= self.max_daily_trades:
            logger.info(f"⏸️ Daily trade limit reached ({self.daily_trades}/{self.max_daily_trades})")
            return
        
        # Get account information
        account_info = self.get_account_info()
        if not account_info:
            logger.error("❌ Could not get account information")
            return
        
        # Get open positions
        open_positions = self.get_open_positions()
        if len(open_positions) >= self.max_concurrent_trades:
            logger.info(f"⏸️ Maximum concurrent trades reached ({len(open_positions)}/{self.max_concurrent_trades})")
            return
        
        # Scan for signals
        signals = self.scan_for_signals()
        
        if not signals:
            logger.info("📊 No qualifying signals found")
            return
        
        # Execute trades for top signals
        trades_to_execute = min(len(signals), self.max_daily_trades - self.daily_trades, self.max_concurrent_trades - len(open_positions))
        
        # Sort signals by confidence
        signals.sort(key=lambda x: x['confidence'], reverse=True)
        
        for i in range(trades_to_execute):
            signal = signals[i]
            success = self.execute_trade(signal, account_info['balance'])
            
            if success:
                logger.info(f"✅ Trade {i+1}/{trades_to_execute} executed successfully")
            else:
                logger.error(f"❌ Trade {i+1}/{trades_to_execute} failed")
            
            # Small delay between trades
            time.sleep(2)
        
        logger.info(f"🎯 Trading session completed. Executed {trades_to_execute} trades")
    
    def start_live_trading(self):
        """Start the live trading bot."""
        logger.info("🚀 Starting live trading bot...")
        
        # Schedule trading sessions
        schedule.every(30).minutes.do(self.trading_session)  # Every 30 minutes
        
        logger.info("⏰ Trading sessions scheduled every 30 minutes")
        logger.info("🔄 Bot is now running. Press Ctrl+C to stop.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("🛑 Live trading bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")

def main():
    """Main function to start live trading."""
    # Get API credentials from environment variables
    api_key = os.getenv('OANDA_API_KEY')
    account_id = os.getenv('OANDA_ACCOUNT_ID')
    
    if not api_key or not account_id:
        print("❌ Error: OANDA_API_KEY and OANDA_ACCOUNT_ID environment variables required")
        print("💡 Set them with:")
        print("   export OANDA_API_KEY='your_api_key'")
        print("   export OANDA_ACCOUNT_ID='your_account_id'")
        return
    
    # Create and start the trading bot
    bot = LiveTradingBot(api_key, account_id)
    
    # Show initial account status
    print("🎯 LIVE TRADING BOT - $10,000 VIRTUAL ACCOUNT")
    print("=" * 60)
    account_info = bot.get_account_info()
    
    if account_info:
        print(f"✅ Connected to OANDA account successfully")
        print(f"💰 Account Balance: ${account_info['balance']:,.2f}")
        print(f"📊 Available Margin: ${account_info['margin_available']:,.2f}")
        print()
        
        # Start live trading
        bot.start_live_trading()
    else:
        print("❌ Failed to connect to OANDA account")

if __name__ == "__main__":
    main() 