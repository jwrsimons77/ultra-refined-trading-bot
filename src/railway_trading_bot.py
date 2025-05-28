#!/usr/bin/env python3
"""
🚀 Railway Trading Bot - $10,000 Virtual Account
24/7 cloud trading with OANDA using optimized signals
Enhanced with comprehensive performance tracking and analytics
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
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional

# Configure logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Railway captures stdout/stderr
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TradeRecord:
    """Comprehensive trade record for performance tracking."""
    trade_id: str
    timestamp: datetime
    pair: str
    signal_type: str
    confidence: float
    entry_price: float
    target_price: float
    stop_loss: float
    units: int
    margin_used: float
    expected_profit: float
    expected_loss: float
    risk_reward_ratio: float
    status: str  # OPEN, CLOSED_WIN, CLOSED_LOSS, CLOSED_MANUAL
    exit_price: Optional[float] = None
    exit_timestamp: Optional[datetime] = None
    actual_profit: Optional[float] = None
    pips_gained: Optional[float] = None
    hold_time_hours: Optional[float] = None
    
class PerformanceTracker:
    """Track and analyze trading performance from Railway logs."""
    
    def __init__(self):
        self.trades: List[TradeRecord] = []
        self.daily_stats = {}
        self.pair_performance = {}
        
    def add_trade(self, trade: TradeRecord):
        """Add a new trade to tracking."""
        self.trades.append(trade)
        logger.info(f"📊 TRADE RECORDED: {trade.pair} {trade.signal_type} | ID: {trade.trade_id} | Confidence: {trade.confidence:.1%}")
        
    def update_trade_outcome(self, trade_id: str, exit_price: float, status: str):
        """Update trade outcome when closed."""
        for trade in self.trades:
            if trade.trade_id == trade_id:
                trade.exit_price = exit_price
                trade.exit_timestamp = datetime.now()
                trade.status = status
                
                # Calculate actual results
                if trade.signal_type == "BUY":
                    trade.pips_gained = (exit_price - trade.entry_price) / (0.01 if 'JPY' in trade.pair else 0.0001)
                else:
                    trade.pips_gained = (trade.entry_price - exit_price) / (0.01 if 'JPY' in trade.pair else 0.0001)
                
                # Calculate actual profit (simplified)
                pip_value = 0.10 / 1000  # Approximate pip value per unit
                trade.actual_profit = trade.pips_gained * pip_value * trade.units
                
                # Calculate hold time
                if trade.exit_timestamp and trade.timestamp:
                    trade.hold_time_hours = (trade.exit_timestamp - trade.timestamp).total_seconds() / 3600
                
                logger.info(f"🎯 TRADE CLOSED: {trade.pair} {trade.signal_type} | {status} | {trade.pips_gained:.1f} pips | ${trade.actual_profit:.2f}")
                break
                
    def get_performance_summary(self) -> Dict:
        """Generate comprehensive performance summary."""
        if not self.trades:
            return {}
            
        total_trades = len(self.trades)
        closed_trades = [t for t in self.trades if t.status in ['CLOSED_WIN', 'CLOSED_LOSS']]
        open_trades = [t for t in self.trades if t.status == 'OPEN']
        
        if not closed_trades:
            return {
                'total_trades': total_trades,
                'open_trades': len(open_trades),
                'closed_trades': 0,
                'win_rate': 0,
                'message': 'No closed trades yet for analysis'
            }
        
        winners = [t for t in closed_trades if t.status == 'CLOSED_WIN']
        losers = [t for t in closed_trades if t.status == 'CLOSED_LOSS']
        
        win_rate = len(winners) / len(closed_trades) if closed_trades else 0
        total_profit = sum([t.actual_profit for t in closed_trades if t.actual_profit])
        avg_win = sum([t.actual_profit for t in winners if t.actual_profit]) / len(winners) if winners else 0
        avg_loss = sum([t.actual_profit for t in losers if t.actual_profit]) / len(losers) if losers else 0
        
        profit_factor = abs(avg_win * len(winners) / (avg_loss * len(losers))) if losers and avg_loss != 0 else float('inf')
        
        return {
            'total_trades': total_trades,
            'open_trades': len(open_trades),
            'closed_trades': len(closed_trades),
            'winners': len(winners),
            'losers': len(losers),
            'win_rate': win_rate,
            'total_profit': total_profit,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'avg_confidence': sum([t.confidence for t in self.trades]) / total_trades,
            'avg_hold_time': sum([t.hold_time_hours for t in closed_trades if t.hold_time_hours]) / len(closed_trades) if closed_trades else 0
        }
        
    def log_performance_report(self):
        """Log detailed performance report to Railway logs."""
        stats = self.get_performance_summary()
        
        if not stats or stats.get('closed_trades', 0) == 0:
            logger.info("📊 PERFORMANCE REPORT: No completed trades yet")
            return
            
        logger.info("=" * 60)
        logger.info("📊 RAILWAY BOT PERFORMANCE REPORT")
        logger.info("=" * 60)
        logger.info(f"📈 Total Trades: {stats['total_trades']}")
        logger.info(f"🔄 Open Trades: {stats['open_trades']}")
        logger.info(f"✅ Closed Trades: {stats['closed_trades']}")
        logger.info(f"🎯 Win Rate: {stats['win_rate']:.1%}")
        logger.info(f"💰 Total Profit: ${stats['total_profit']:.2f}")
        logger.info(f"⚖️  Profit Factor: {stats['profit_factor']:.2f}")
        logger.info(f"📊 Average Win: ${stats['avg_win']:.2f}")
        logger.info(f"📉 Average Loss: ${stats['avg_loss']:.2f}")
        logger.info(f"🎲 Average Confidence: {stats['avg_confidence']:.1%}")
        logger.info(f"⏱️  Average Hold Time: {stats['avg_hold_time']:.1f} hours")
        logger.info("=" * 60)
        
        # Pair-specific performance
        pair_stats = {}
        for trade in self.trades:
            if trade.pair not in pair_stats:
                pair_stats[trade.pair] = {'total': 0, 'wins': 0, 'profit': 0}
            pair_stats[trade.pair]['total'] += 1
            if trade.status == 'CLOSED_WIN':
                pair_stats[trade.pair]['wins'] += 1
            if trade.actual_profit:
                pair_stats[trade.pair]['profit'] += trade.actual_profit
                
        logger.info("📊 PAIR PERFORMANCE:")
        for pair, data in pair_stats.items():
            win_rate = data['wins'] / data['total'] if data['total'] > 0 else 0
            logger.info(f"   {pair}: {data['total']} trades | {win_rate:.1%} win rate | ${data['profit']:.2f} profit")

class RailwayTradingBot:
    """24/7 Railway trading bot with enhanced performance tracking."""
    
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
        self.performance_tracker = PerformanceTracker()
        
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
        self.starting_balance = None
        
        logger.info("🚀 Railway Trading Bot initialized with Performance Tracking")
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
        
        # More accurate pip value calculation
        if 'JPY' in pair:
            pip_value = 0.01  # For JPY pairs
        else:
            pip_value = 0.0001  # For other pairs
        
        # Use standard pip value for 1000 units ($0.10 for major pairs)
        pip_value_per_1000_units = 0.10
        
        # Assume 20 pip stop loss (will be overridden by actual signal data)
        stop_loss_pips = 20
        
        # Calculate position size based on risk
        # Position size = Risk Amount / (Stop Loss Pips * Pip Value per 1000 units) * 1000
        position_size = int((risk_amount / (stop_loss_pips * pip_value_per_1000_units)) * 1000)
        
        # Conservative limits for $10k account - UPDATED for fixed position sizing
        min_size = 1000      # Minimum 1k units (0.001 lots)
        max_size = 5000      # Maximum 5k units (0.005 lots) - more conservative since sizing is fixed
        
        position_size = max(min_size, min(position_size, max_size))
        
        # Log the calculation for transparency
        logger.info(f"📊 Position sizing for {pair}:")
        logger.info(f"   Risk amount: ${risk_amount:.2f}")
        logger.info(f"   Stop loss: {stop_loss_pips} pips")
        logger.info(f"   Pip value per 1000 units: ${pip_value_per_1000_units:.2f}")
        logger.info(f"   Calculated size: {position_size:,} units")
        logger.info(f"   Lot size: {position_size/100000:.3f} lots")
        
        return position_size
    
    def execute_trade(self, signal: dict, account_balance: float):
        """Execute a trade based on signal with comprehensive tracking."""
        try:
            pair = signal['pair']
            action = signal['signal_type']
            confidence = signal['confidence']
            
            # Store starting balance on first trade
            if self.starting_balance is None:
                self.starting_balance = account_balance
                logger.info(f"📊 STARTING BALANCE RECORDED: ${self.starting_balance:,.2f}")
            
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
            from oanda_trader import TradeOrder
            
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
                # Calculate expected profit/loss
                pip_value = 0.10 / 1000  # Approximate pip value per unit
                
                if action == "BUY":
                    target_pips = (signal['target_price'] - signal['entry_price']) / (0.01 if 'JPY' in pair else 0.0001)
                    stop_pips = (signal['entry_price'] - signal['stop_loss']) / (0.01 if 'JPY' in pair else 0.0001)
                else:
                    target_pips = (signal['entry_price'] - signal['target_price']) / (0.01 if 'JPY' in pair else 0.0001)
                    stop_pips = (signal['stop_loss'] - signal['entry_price']) / (0.01 if 'JPY' in pair else 0.0001)
                
                expected_profit = target_pips * pip_value * position_size
                expected_loss = -stop_pips * pip_value * position_size
                risk_reward_ratio = abs(expected_profit / expected_loss) if expected_loss != 0 else 0
                
                # Create trade record
                trade_record = TradeRecord(
                    trade_id=str(order_id),
                    timestamp=datetime.now(),
                    pair=pair,
                    signal_type=action,
                    confidence=confidence,
                    entry_price=signal['entry_price'],
                    target_price=signal['target_price'],
                    stop_loss=signal['stop_loss'],
                    units=position_size,
                    margin_used=position_size * 0.03,  # Approximate margin
                    expected_profit=expected_profit,
                    expected_loss=expected_loss,
                    risk_reward_ratio=risk_reward_ratio,
                    status="OPEN"
                )
                
                # Add to performance tracker
                self.performance_tracker.add_trade(trade_record)
                
                logger.info(f"✅ Trade executed successfully!")
                logger.info(f"📊 Trade ID: {order_id}")
                logger.info(f"🎯 Expected Profit: ${expected_profit:.2f} ({target_pips:.1f} pips)")
                logger.info(f"🛡️ Expected Loss: ${expected_loss:.2f} ({stop_pips:.1f} pips)")
                logger.info(f"⚖️ Risk/Reward Ratio: {risk_reward_ratio:.2f}:1")
                
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
        """Execute one trading session with performance monitoring."""
        logger.info("🚀 Starting trading session...")
        
        # Monitor open positions first
        self.monitor_open_positions()
        
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
        
        # Log quick performance update
        if self.total_trades > 0:
            stats = self.performance_tracker.get_performance_summary()
            if stats and stats.get('closed_trades', 0) > 0:
                logger.info(f"📊 Current Performance: {stats['win_rate']:.1%} win rate | ${stats['total_profit']:.2f} profit | {stats['closed_trades']} closed trades")
    
    def health_check(self):
        """Perform health check with performance monitoring."""
        try:
            account_info = self.get_account_info()
            if account_info:
                # Basic health check
                balance = account_info['balance']
                logger.info(f"💚 Health check passed - Balance: ${balance:,.2f}")
                
                # Performance health check
                if self.starting_balance:
                    total_return = balance - self.starting_balance
                    return_pct = (total_return / self.starting_balance) * 100
                    logger.info(f"📈 Performance: ${total_return:+,.2f} ({return_pct:+.2f}%) since start")
                
                # Monitor open positions
                self.monitor_open_positions()
                
                # Log performance summary every 4th health check (every 8 hours)
                if hasattr(self, 'health_check_count'):
                    self.health_check_count += 1
                else:
                    self.health_check_count = 1
                
                if self.health_check_count % 4 == 0:
                    logger.info("🕐 8-HOUR PERFORMANCE CHECKPOINT")
                    self.performance_tracker.log_performance_report()
                    
            else:
                logger.warning("⚠️ Health check warning - Could not get account info")
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
    
    def start_24_7_trading(self):
        """Start the 24/7 Railway trading bot with enhanced monitoring."""
        logger.info("🚀 Starting 24/7 Railway trading bot...")
        
        # Schedule trading sessions every 30 minutes
        schedule.every(30).minutes.do(self.trading_session)
        
        # Schedule health checks every 2 hours
        schedule.every(2).hours.do(self.health_check)
        
        # Schedule daily performance summary at midnight UTC
        schedule.every().day.at("00:00").do(self.log_daily_performance_summary)
        
        # Schedule performance reports every 6 hours
        schedule.every(6).hours.do(self.performance_tracker.log_performance_report)
        
        logger.info("⏰ Trading sessions scheduled every 30 minutes")
        logger.info("💚 Health checks scheduled every 2 hours")
        logger.info("📊 Performance reports scheduled every 6 hours")
        logger.info("📈 Daily summaries scheduled at midnight UTC")
        logger.info("🌐 Bot is now running 24/7 on Railway")
        
        # Initial health check
        self.health_check()
        
        # Log initial status
        logger.info("🎯 RAILWAY BOT PERFORMANCE TRACKING ACTIVE")
        logger.info("📊 All trades will be tracked and analyzed in real-time")
        logger.info("📈 Performance reports will appear in Railway logs")
        
        # Main loop
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"❌ Unexpected error in main loop: {e}")
                logger.info("🔄 Continuing operation...")
                time.sleep(300)  # Wait 5 minutes before retrying
    
    def monitor_open_positions(self):
        """Monitor open positions and update trade outcomes."""
        try:
            open_positions = self.get_open_positions()
            
            # Check for closed trades
            for trade in self.performance_tracker.trades:
                if trade.status == "OPEN":
                    # Check if position is still open
                    position_still_open = False
                    for position in open_positions:
                        instrument = position.get('instrument', '').replace('_', '/')
                        if instrument == trade.pair:
                            position_still_open = True
                            break
                    
                    if not position_still_open:
                        # Position was closed, try to determine outcome
                        # This is simplified - in practice you'd query OANDA for trade history
                        logger.info(f"🔍 Detected closed position: {trade.pair} (Trade ID: {trade.trade_id})")
                        
                        # For now, we'll mark as closed and let manual analysis determine win/loss
                        # In a full implementation, you'd query OANDA's transaction history
                        
        except Exception as e:
            logger.error(f"❌ Error monitoring positions: {e}")
    
    def log_daily_performance_summary(self):
        """Log daily performance summary."""
        try:
            current_account = self.get_account_info()
            if current_account and self.starting_balance:
                current_balance = current_account['balance']
                total_return = current_balance - self.starting_balance
                return_pct = (total_return / self.starting_balance) * 100
                
                logger.info("=" * 50)
                logger.info("📊 DAILY PERFORMANCE SUMMARY")
                logger.info("=" * 50)
                logger.info(f"💰 Starting Balance: ${self.starting_balance:,.2f}")
                logger.info(f"💰 Current Balance: ${current_balance:,.2f}")
                logger.info(f"📈 Total Return: ${total_return:,.2f} ({return_pct:+.2f}%)")
                logger.info(f"📊 Total Trades Today: {self.daily_trades}")
                logger.info(f"📈 Total Trades All Time: {self.total_trades}")
                
                # Log performance tracker summary
                self.performance_tracker.log_performance_report()
                
        except Exception as e:
            logger.error(f"❌ Error logging daily summary: {e}")

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