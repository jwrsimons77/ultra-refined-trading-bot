#!/usr/bin/env python3
"""
🚀 Railway Trading Bot - $10,000 Virtual Account
24/7 cloud trading with OANDA using optimized signals
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

# Configure logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Railway captures stdout/stderr
    ]
)
logger = logging.getLogger(__name__)

class RailwayTradingBot:
    """24/7 Railway trading bot for $10,000 virtual account."""
    
    def __init__(self):
        """Initialize the Railway trading bot."""
        # Get credentials from Railway environment variables
        api_key = os.getenv('OANDA_API_KEY')
        account_id = os.getenv('OANDA_ACCOUNT_ID')
        
        if not api_key or not account_id:
            raise ValueError("OANDA_API_KEY and OANDA_ACCOUNT_ID environment variables required")
        
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
        self.total_trades = 0
        self.total_profit = 0.0
        
        logger.info("🚀 Railway Trading Bot initialized")
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
            account_info = self.trader.get_account_summary()
            balance = float(account_info.get('balance', 0))
            nav = float(account_info.get('nav', 0))
            margin_used = float(account_info.get('margin_used', 0))
            margin_available = float(account_info.get('margin_available', 0))
            
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
            positions = self.trader.get_open_positions()
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
            action = signal['signal_type']
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
            
            # Create TradeOrder object
            from src.oanda_trader import TradeOrder
            
            trade_order = TradeOrder(
                pair=pair,
                signal_type=action,
                entry_price=signal['entry_price'],
                target_price=signal['target_price'],
                stop_loss=signal['stop_loss'],
                confidence=confidence,
                units=position_size,
                risk_amount=account_balance * self.risk_per_trade
            )
            
            # Execute the trade
            order_id = self.trader.place_market_order(trade_order)
            
            if order_id:
                logger.info(f"✅ Trade executed successfully!")
                logger.info(f"📊 Trade ID: {order_id}")
                
                self.daily_trades += 1
                self.total_trades += 1
                return True
            else:
                logger.error(f"❌ Trade execution failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error executing trade: {e}")
            return False
    
    def scan_for_signals(self):
        """Scan all pairs for trading signals."""
        logger.info("🔍 Scanning for trading signals...")
        
        # Generate signals for all pairs at once
        try:
            all_signals = self.signal_generator.generate_forex_signals(
                max_signals=10, 
                min_confidence=self.min_confidence
            )
            
            # Filter signals for our trading pairs
            signals = []
            for signal in all_signals:
                if signal.pair in self.pairs and signal.confidence >= self.min_confidence:
                    # Convert ForexSignal object to dict for compatibility
                    signal_dict = {
                        'pair': signal.pair,
                        'signal_type': signal.signal_type,
                        'confidence': signal.confidence,
                        'entry_price': signal.entry_price,
                        'target_price': signal.target_price,
                        'stop_loss': signal.stop_loss,
                        'reason': signal.reason
                    }
                    signals.append(signal_dict)
                    logger.info(f"🎯 Signal found: {signal.pair} {signal.signal_type} ({signal.confidence:.1%})")
            
            logger.info(f"📊 Found {len(signals)} qualifying signals")
            return signals
            
        except Exception as e:
            logger.error(f"❌ Error generating signals: {e}")
            return []
    
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
        logger.info(f"📊 Total trades today: {self.daily_trades}/{self.max_daily_trades}")
        logger.info(f"📈 Total trades all time: {self.total_trades}")
    
    def health_check(self):
        """Perform health check and log status."""
        try:
            account_info = self.get_account_info()
            if account_info:
                logger.info(f"💚 Health check passed - Balance: ${account_info['balance']:,.2f}")
            else:
                logger.warning("⚠️ Health check warning - Could not get account info")
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
    
    def start_24_7_trading(self):
        """Start the 24/7 Railway trading bot."""
        logger.info("🚀 Starting 24/7 Railway trading bot...")
        
        # Schedule trading sessions every 30 minutes
        schedule.every(30).minutes.do(self.trading_session)
        
        # Schedule health checks every 2 hours
        schedule.every(2).hours.do(self.health_check)
        
        logger.info("⏰ Trading sessions scheduled every 30 minutes")
        logger.info("💚 Health checks scheduled every 2 hours")
        logger.info("🌐 Bot is now running 24/7 on Railway")
        
        # Initial health check
        self.health_check()
        
        # Main loop
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"❌ Unexpected error in main loop: {e}")
                logger.info("🔄 Continuing operation...")
                time.sleep(300)  # Wait 5 minutes before retrying

def main():
    """Main function for Railway deployment."""
    logger.info("🎯 RAILWAY TRADING BOT - $10,000 VIRTUAL ACCOUNT")
    logger.info("=" * 60)
    
    try:
        # Create and start the trading bot
        bot = RailwayTradingBot()
        
        # Show initial status
        account_info = bot.get_account_info()
        if account_info:
            logger.info(f"✅ Connected to OANDA account successfully")
            logger.info(f"💰 Account Balance: ${account_info['balance']:,.2f}")
            logger.info(f"📊 Available Margin: ${account_info['margin_available']:,.2f}")
            
            # Start 24/7 trading
            bot.start_24_7_trading()
        else:
            logger.error("❌ Failed to connect to OANDA account")
            
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        logger.error("💡 Make sure OANDA_API_KEY and OANDA_ACCOUNT_ID are set in Railway environment variables")
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")

if __name__ == "__main__":
    main() 