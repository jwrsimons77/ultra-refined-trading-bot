#!/usr/bin/env python3
"""
🎯 YFinance Historical Backtesting System
Tests your exact trading bot logic against historical Yahoo Finance data
More reliable than OANDA API for backtesting
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional
import yfinance as yf
from dataclasses import dataclass
import matplotlib.pyplot as plt
import seaborn as sns

# Import your trading components
from forex_signal_generator import ForexSignalGenerator
from simple_technical_analyzer import SimpleTechnicalAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BacktestTrade:
    """Represents a completed backtest trade."""
    pair: str
    signal_type: str
    entry_time: datetime
    entry_price: float
    exit_time: datetime
    exit_price: float
    target_price: float
    stop_loss: float
    confidence: float
    pips_gained: float
    profit_loss: float
    outcome: str  # 'WIN', 'LOSS', 'TIMEOUT'
    hold_time_hours: float
    reason: str

class YFinanceBacktester:
    """
    Comprehensive backtesting system using Yahoo Finance data
    Tests your exact trading bot logic
    """
    
    def __init__(self):
        """Initialize the backtester."""
        self.signal_generator = ForexSignalGenerator()
        self.technical_analyzer = SimpleTechnicalAnalyzer()
        
        # Backtesting parameters - MATCH YOUR BOT EXACTLY
        self.min_confidence = 0.45  # Same as background trader
        self.max_hold_hours = 168   # 1 week maximum hold time
        
        # Yahoo Finance forex symbols
        self.pairs_to_test = {
            'EUR/USD': 'EURUSD=X',
            'GBP/USD': 'GBPUSD=X', 
            'USD/JPY': 'USDJPY=X',
            'USD/CHF': 'USDCHF=X',
            'AUD/USD': 'AUDUSD=X',
            'USD/CAD': 'USDCAD=X',
            'NZD/USD': 'NZDUSD=X'
        }
        
        # Results storage
        self.completed_trades = []
        self.daily_results = []
        
        logger.info("🎯 YFinance Historical Backtester initialized")
        logger.info(f"📊 Testing pairs: {', '.join(self.pairs_to_test.keys())}")
        logger.info(f"📊 Min confidence: {self.min_confidence:.1%}")
    
    def get_historical_data(self, pair: str, start_date: datetime, end_date: datetime) -> Optional[pd.DataFrame]:
        """Get historical Yahoo Finance data for backtesting."""
        try:
            yf_symbol = self.pairs_to_test.get(pair)
            if not yf_symbol:
                logger.warning(f"No Yahoo Finance symbol for {pair}")
                return None
            
            # Download data with 1-hour intervals
            ticker = yf.Ticker(yf_symbol)
            
            # Try different intervals based on date range
            days_diff = (end_date - start_date).days
            
            if days_diff <= 7:
                interval = "1h"
            elif days_diff <= 30:
                interval = "1h"
            else:
                interval = "1d"
            
            logger.info(f"📊 Downloading {pair} data ({interval} interval)...")
            
            data = ticker.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval=interval,
                auto_adjust=True,
                prepost=False
            )
            
            if data.empty:
                logger.warning(f"No data available for {pair}")
                return None
            
            # Rename columns to match our format
            data = data.rename(columns={
                'Open': 'open',
                'High': 'high', 
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            # Ensure we have the required columns
            required_cols = ['open', 'high', 'low', 'close']
            if not all(col in data.columns for col in required_cols):
                logger.error(f"Missing required columns for {pair}")
                return None
            
            # Add volume if missing
            if 'volume' not in data.columns:
                data['volume'] = 1000  # Default volume
            
            # Remove timezone info for consistency
            if data.index.tz is not None:
                data.index = data.index.tz_localize(None)
            
            logger.info(f"📊 Retrieved {len(data)} candles for {pair} ({start_date.date()} to {end_date.date()})")
            return data
                
        except Exception as e:
            logger.error(f"Error getting historical data for {pair}: {e}")
            return None
    
    def simulate_signal_generation(self, pair: str, timestamp: datetime, historical_data: pd.DataFrame) -> Optional[Dict]:
        """
        Simulate signal generation at a specific point in time
        Uses only data available up to that timestamp
        """
        try:
            # Get data up to the current timestamp
            available_data = historical_data[historical_data.index <= timestamp]
            
            if len(available_data) < 50:  # Need enough data for analysis
                return None
            
            current_price = available_data['close'].iloc[-1]
            
            # Simulate news sentiment (simplified for backtesting)
            # Use a more realistic sentiment based on price action
            recent_change = (current_price - available_data['close'].iloc[-10]) / available_data['close'].iloc[-10]
            sentiment = np.clip(recent_change * 2, -0.4, 0.4)  # Scale to sentiment range
            
            # Get technical analysis using available data
            technical_analysis = self.simulate_technical_analysis(pair, available_data)
            
            if not technical_analysis:
                return None
            
            # Generate signal using same logic as live bot
            signal = self.signal_generator.generate_signal_from_analysis(
                pair, sentiment, technical_analysis
            )
            
            if signal and signal.confidence >= self.min_confidence:
                return {
                    'signal': signal,
                    'timestamp': timestamp,
                    'current_price': current_price
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error simulating signal for {pair} at {timestamp}: {e}")
            return None
    
    def simulate_technical_analysis(self, pair: str, data: pd.DataFrame) -> Optional[Dict]:
        """Simulate technical analysis using historical data."""
        try:
            if len(data) < 50:
                return None
            
            # Use the same technical analysis as your live bot
            # Calculate RSI
            delta = data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            # Calculate MACD
            ema_12 = data['close'].ewm(span=12).mean()
            ema_26 = data['close'].ewm(span=26).mean()
            macd_line = ema_12 - ema_26
            signal_line = macd_line.ewm(span=9).mean()
            macd_histogram = macd_line - signal_line
            
            # Calculate ATR
            high_low = data['high'] - data['low']
            high_close = np.abs(data['high'] - data['close'].shift())
            low_close = np.abs(data['low'] - data['close'].shift())
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(window=14).mean().iloc[-1]
            
            # Calculate Bollinger Bands
            bb_period = 20
            bb_std = 2
            bb_middle = data['close'].rolling(window=bb_period).mean()
            bb_std_dev = data['close'].rolling(window=bb_period).std()
            bb_upper = bb_middle + (bb_std_dev * bb_std)
            bb_lower = bb_middle - (bb_std_dev * bb_std)
            
            current_price = data['close'].iloc[-1]
            bb_position = (current_price - bb_lower.iloc[-1]) / (bb_upper.iloc[-1] - bb_lower.iloc[-1])
            
            # Generate technical score using multiple indicators
            rsi_score = 0.0
            if current_rsi > 75:  # More sensitive thresholds
                rsi_score = -0.6
            elif current_rsi < 25:
                rsi_score = 0.6
            elif current_rsi > 60:
                rsi_score = -0.3
            elif current_rsi < 40:
                rsi_score = 0.3
            
            macd_score = 0.0
            if macd_line.iloc[-1] > signal_line.iloc[-1]:
                if macd_line.iloc[-2] <= signal_line.iloc[-2]:  # Bullish crossover
                    macd_score = 0.7
                else:
                    macd_score = 0.4
            elif macd_line.iloc[-1] < signal_line.iloc[-1]:
                if macd_line.iloc[-2] >= signal_line.iloc[-2]:  # Bearish crossover
                    macd_score = -0.7
                else:
                    macd_score = -0.4
            
            # Bollinger Bands score
            bb_score = 0.0
            if bb_position > 0.8:  # Near upper band
                bb_score = -0.4
            elif bb_position < 0.2:  # Near lower band
                bb_score = 0.4
            
            # Moving average trend
            ma_20 = data['close'].rolling(window=20).mean().iloc[-1]
            ma_50 = data['close'].rolling(window=50).mean().iloc[-1]
            trend_score = 0.0
            if ma_20 > ma_50:
                trend_score = 0.3
            else:
                trend_score = -0.3
            
            # Combine scores
            technical_score = (rsi_score * 0.3 + macd_score * 0.4 + bb_score * 0.2 + trend_score * 0.1)
            
            # Calculate confidence based on signal strength
            confidence = min(0.9, 0.6 + abs(technical_score) * 0.5)
            
            return {
                'score': technical_score,
                'confidence': confidence,
                'atr': atr,
                'timeframe_breakdown': {'H1': technical_score},
                'source': 'Historical Technical Analysis',
                'indicators': {
                    'rsi': current_rsi,
                    'macd_signal': 'bullish' if macd_score > 0 else 'bearish',
                    'bb_position': bb_position,
                    'trend': 'bullish' if trend_score > 0 else 'bearish'
                }
            }
            
        except Exception as e:
            logger.error(f"Error in technical analysis simulation: {e}")
            return None
    
    def simulate_trade_execution(self, signal_data: Dict, historical_data: pd.DataFrame) -> Optional[BacktestTrade]:
        """
        Simulate trade execution and track to completion
        """
        try:
            signal = signal_data['signal']
            entry_time = signal_data['timestamp']
            entry_price = signal_data['current_price']
            
            # Get future data for trade simulation
            future_data = historical_data[historical_data.index > entry_time]
            
            if len(future_data) == 0:
                return None
            
            # Track the trade
            for i, (timestamp, row) in enumerate(future_data.iterrows()):
                current_price = row['close']
                hours_elapsed = (timestamp - entry_time).total_seconds() / 3600
                
                # Check for target hit
                if signal.signal_type == "BUY":
                    if current_price >= signal.target_price:
                        # Target hit - WIN (use signal's target pips, not calculated)
                        pips_gained = signal.pips_target  # Use the actual target pips from signal
                        return BacktestTrade(
                            pair=signal.pair,
                            signal_type=signal.signal_type,
                            entry_time=entry_time,
                            entry_price=entry_price,
                            exit_time=timestamp,
                            exit_price=signal.target_price,  # Exit at target, not current price
                            target_price=signal.target_price,
                            stop_loss=signal.stop_loss,
                            confidence=signal.confidence,
                            pips_gained=pips_gained,
                            profit_loss=pips_gained * 0.10,  # $0.10 per pip for 1000 units
                            outcome='WIN',
                            hold_time_hours=hours_elapsed,
                            reason=signal.reason
                        )
                    elif current_price <= signal.stop_loss:
                        # Stop loss hit - LOSS (use signal's stop pips, not calculated)
                        pips_gained = -signal.pips_risk  # Negative because it's a loss
                        return BacktestTrade(
                            pair=signal.pair,
                            signal_type=signal.signal_type,
                            entry_time=entry_time,
                            entry_price=entry_price,
                            exit_time=timestamp,
                            exit_price=signal.stop_loss,  # Exit at stop loss, not current price
                            target_price=signal.target_price,
                            stop_loss=signal.stop_loss,
                            confidence=signal.confidence,
                            pips_gained=pips_gained,
                            profit_loss=pips_gained * 0.10,  # $0.10 per pip for 1000 units
                            outcome='LOSS',
                            hold_time_hours=hours_elapsed,
                            reason=signal.reason
                        )
                else:  # SELL
                    if current_price <= signal.target_price:
                        # Target hit - WIN (use signal's target pips, not calculated)
                        pips_gained = signal.pips_target  # Use the actual target pips from signal
                        return BacktestTrade(
                            pair=signal.pair,
                            signal_type=signal.signal_type,
                            entry_time=entry_time,
                            entry_price=entry_price,
                            exit_time=timestamp,
                            exit_price=signal.target_price,  # Exit at target, not current price
                            target_price=signal.target_price,
                            stop_loss=signal.stop_loss,
                            confidence=signal.confidence,
                            pips_gained=pips_gained,
                            profit_loss=pips_gained * 0.10,  # $0.10 per pip for 1000 units
                            outcome='WIN',
                            hold_time_hours=hours_elapsed,
                            reason=signal.reason
                        )
                    elif current_price >= signal.stop_loss:
                        # Stop loss hit - LOSS (use signal's stop pips, not calculated)
                        pips_gained = -signal.pips_risk  # Negative because it's a loss
                        return BacktestTrade(
                            pair=signal.pair,
                            signal_type=signal.signal_type,
                            entry_time=entry_time,
                            entry_price=entry_price,
                            exit_time=timestamp,
                            exit_price=signal.stop_loss,  # Exit at stop loss, not current price
                            target_price=signal.target_price,
                            stop_loss=signal.stop_loss,
                            confidence=signal.confidence,
                            pips_gained=pips_gained,
                            profit_loss=pips_gained * 0.10,  # $0.10 per pip for 1000 units
                            outcome='LOSS',
                            hold_time_hours=hours_elapsed,
                            reason=signal.reason
                        )
                
                # Check for timeout
                if hours_elapsed >= self.max_hold_hours:
                    # Timeout - close at current price
                    if signal.signal_type == "BUY":
                        pips_gained = (current_price - entry_price) / (0.01 if 'JPY' in signal.pair else 0.0001)
                    else:
                        pips_gained = (entry_price - current_price) / (0.01 if 'JPY' in signal.pair else 0.0001)
                    
                    outcome = 'WIN' if pips_gained > 0 else 'LOSS'
                    
                    return BacktestTrade(
                        pair=signal.pair,
                        signal_type=signal.signal_type,
                        entry_time=entry_time,
                        entry_price=entry_price,
                        exit_time=timestamp,
                        exit_price=current_price,
                        target_price=signal.target_price,
                        stop_loss=signal.stop_loss,
                        confidence=signal.confidence,
                        pips_gained=pips_gained,
                        profit_loss=pips_gained * 0.10,  # $0.10 per pip for 1000 units (FIXED)
                        outcome='TIMEOUT',
                        hold_time_hours=hours_elapsed,
                        reason=signal.reason
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Error simulating trade execution: {e}")
            return None
    
    def run_backtest(self, start_date: datetime, end_date: datetime, scan_interval_hours: int = 4) -> Dict:
        """
        Run comprehensive backtest over specified period
        """
        logger.info(f"🎯 Starting backtest from {start_date.date()} to {end_date.date()}")
        logger.info(f"📊 Scan interval: {scan_interval_hours} hours")
        
        total_signals_generated = 0
        total_trades_executed = 0
        
        for pair in self.pairs_to_test.keys():
            logger.info(f"📈 Testing {pair}...")
            
            # Get historical data for this pair
            historical_data = self.get_historical_data(pair, start_date, end_date)
            
            if historical_data is None:
                logger.warning(f"⚠️ No data available for {pair}")
                continue
            
            # Simulate signal generation at regular intervals
            data_timestamps = historical_data.index
            
            for timestamp in data_timestamps[::scan_interval_hours]:  # Sample every N hours
                if timestamp < start_date or timestamp >= end_date:
                    continue
                    
                signal_data = self.simulate_signal_generation(pair, timestamp, historical_data)
                
                if signal_data:
                    total_signals_generated += 1
                    logger.info(f"📊 Generated signal: {pair} {signal_data['signal'].signal_type} at {timestamp} (confidence: {signal_data['signal'].confidence:.1%})")
                    
                    # Simulate trade execution
                    trade = self.simulate_trade_execution(signal_data, historical_data)
                    
                    if trade:
                        total_trades_executed += 1
                        self.completed_trades.append(trade)
                        logger.info(f"✅ Trade completed: {trade.outcome} - {trade.pips_gained:.1f} pips in {trade.hold_time_hours:.1f} hours")
        
        # Calculate results
        results = self.calculate_results()
        
        logger.info(f"🎯 Backtest completed!")
        logger.info(f"📊 Signals generated: {total_signals_generated}")
        logger.info(f"📊 Trades executed: {total_trades_executed}")
        
        if 'error' not in results:
            logger.info(f"📊 Win rate: {results['win_rate']:.1%}")
            logger.info(f"📊 Total profit: ${results['total_profit']:.2f}")
        
        return results
    
    def calculate_results(self) -> Dict:
        """Calculate comprehensive backtest results."""
        if not self.completed_trades:
            return {'error': 'No completed trades'}
        
        df = pd.DataFrame([
            {
                'pair': trade.pair,
                'signal_type': trade.signal_type,
                'outcome': trade.outcome,
                'pips_gained': trade.pips_gained,
                'profit_loss': trade.profit_loss,
                'confidence': trade.confidence,
                'hold_time_hours': trade.hold_time_hours,
                'entry_time': trade.entry_time
            }
            for trade in self.completed_trades
        ])
        
        # Calculate key metrics
        total_trades = len(df)
        winning_trades = len(df[df['outcome'] == 'WIN'])
        losing_trades = len(df[df['outcome'] == 'LOSS'])
        timeout_trades = len(df[df['outcome'] == 'TIMEOUT'])
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        total_profit = df['profit_loss'].sum()
        avg_win = df[df['outcome'] == 'WIN']['profit_loss'].mean() if winning_trades > 0 else 0
        avg_loss = df[df['outcome'] == 'LOSS']['profit_loss'].mean() if losing_trades > 0 else 0
        
        profit_factor = abs(df[df['profit_loss'] > 0]['profit_loss'].sum() / df[df['profit_loss'] < 0]['profit_loss'].sum()) if df[df['profit_loss'] < 0]['profit_loss'].sum() != 0 else float('inf')
        
        avg_hold_time = df['hold_time_hours'].mean()
        
        # Calculate by pair
        pair_results = df.groupby('pair').agg({
            'outcome': lambda x: (x == 'WIN').sum() / len(x),
            'profit_loss': 'sum',
            'pips_gained': 'sum'
        }).round(3)
        
        # Calculate by confidence level
        confidence_bins = pd.cut(df['confidence'], bins=[0, 0.5, 0.6, 0.7, 0.8, 1.0], labels=['45-50%', '50-60%', '60-70%', '70-80%', '80%+'])
        confidence_results = df.groupby(confidence_bins).agg({
            'outcome': lambda x: (x == 'WIN').sum() / len(x),
            'profit_loss': 'sum'
        }).round(3)
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'timeout_trades': timeout_trades,
            'win_rate': win_rate,
            'total_profit': total_profit,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'avg_hold_time_hours': avg_hold_time,
            'pair_results': pair_results.to_dict(),
            'confidence_results': confidence_results.to_dict(),
            'trades_df': df
        }
    
    def generate_report(self, results: Dict, save_path: str = 'backtest_report.html'):
        """Generate comprehensive HTML report."""
        if 'error' in results:
            logger.error(f"Cannot generate report: {results['error']}")
            return
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>🎯 Trading Bot Backtest Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; color: #2c3e50; margin-bottom: 30px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 15px; background: #ecf0f1; border-radius: 8px; text-align: center; }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #27ae60; }}
                .metric-label {{ font-size: 14px; color: #7f8c8d; }}
                .section {{ margin: 30px 0; }}
                .positive {{ color: #27ae60; }}
                .negative {{ color: #e74c3c; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #34495e; color: white; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 Trading Bot Backtest Report</h1>
                    <p>Historical Performance Analysis (Yahoo Finance Data)</p>
                </div>
                
                <div class="section">
                    <h2>📊 Key Performance Metrics</h2>
                    <div class="metric">
                        <div class="metric-value {'positive' if results['win_rate'] > 0.5 else 'negative'}">{results['win_rate']:.1%}</div>
                        <div class="metric-label">Win Rate</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{results['total_trades']}</div>
                        <div class="metric-label">Total Trades</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value {'positive' if results['total_profit'] > 0 else 'negative'}">${results['total_profit']:.2f}</div>
                        <div class="metric-label">Total Profit</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{results['profit_factor']:.2f}</div>
                        <div class="metric-label">Profit Factor</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{results['avg_hold_time_hours']:.1f}h</div>
                        <div class="metric-label">Avg Hold Time</div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>📈 Trade Breakdown</h2>
                    <p><strong>Winning Trades:</strong> {results['winning_trades']} (${results['avg_win']:.2f} average)</p>
                    <p><strong>Losing Trades:</strong> {results['losing_trades']} (${results['avg_loss']:.2f} average)</p>
                    <p><strong>Timeout Trades:</strong> {results['timeout_trades']}</p>
                </div>
                
                <div class="section">
                    <h2>💱 Performance by Currency Pair</h2>
                    <table>
                        <tr><th>Pair</th><th>Win Rate</th><th>Total Profit</th><th>Total Pips</th></tr>
        """
        
        for pair, data in results['pair_results']['outcome'].items():
            profit = results['pair_results']['profit_loss'][pair]
            pips = results['pair_results']['pips_gained'][pair]
            html_content += f"<tr><td>{pair}</td><td>{data:.1%}</td><td>${profit:.2f}</td><td>{pips:.1f}</td></tr>"
        
        html_content += """
                    </table>
                </div>
                
                <div class="section">
                    <h2>🎯 Performance by Confidence Level</h2>
                    <table>
                        <tr><th>Confidence Range</th><th>Win Rate</th><th>Total Profit</th></tr>
        """
        
        for conf_range, data in results['confidence_results']['outcome'].items():
            profit = results['confidence_results']['profit_loss'][conf_range]
            html_content += f"<tr><td>{conf_range}</td><td>{data:.1%}</td><td>${profit:.2f}</td></tr>"
        
        html_content += """
                    </table>
                </div>
                
                <div class="section">
                    <h2>💡 Key Insights</h2>
        """
        
        # Add insights based on results
        if results['win_rate'] > 0.6:
            html_content += "<p>✅ <strong>Excellent win rate!</strong> Your bot shows strong predictive capability.</p>"
        elif results['win_rate'] > 0.5:
            html_content += "<p>✅ <strong>Good win rate.</strong> Your bot is profitable with room for optimization.</p>"
        else:
            html_content += "<p>⚠️ <strong>Win rate needs improvement.</strong> Consider adjusting confidence thresholds.</p>"
        
        if results['profit_factor'] > 1.5:
            html_content += "<p>✅ <strong>Strong profit factor!</strong> Your wins significantly outweigh losses.</p>"
        elif results['profit_factor'] > 1.0:
            html_content += "<p>✅ <strong>Profitable system.</strong> Positive expectancy confirmed.</p>"
        else:
            html_content += "<p>⚠️ <strong>Profit factor below 1.0.</strong> System needs optimization.</p>"
        
        html_content += """
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(save_path, 'w') as f:
            f.write(html_content)
        
        logger.info(f"📊 Report saved to {save_path}")

def main():
    """Run historical backtest."""
    backtester = YFinanceBacktester()
    
    # Test over the last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    print("🎯 Starting Historical Backtest...")
    print(f"📅 Period: {start_date.date()} to {end_date.date()}")
    print(f"📊 Testing {len(backtester.pairs_to_test)} currency pairs")
    print(f"📊 Minimum confidence: {backtester.min_confidence:.1%}")
    print("=" * 60)
    
    # Run backtest
    results = backtester.run_backtest(start_date, end_date, scan_interval_hours=6)
    
    if 'error' not in results:
        # Generate report
        backtester.generate_report(results)
        
        print("\n🎯 BACKTEST RESULTS SUMMARY:")
        print("=" * 60)
        print(f"📊 Total Trades: {results['total_trades']}")
        print(f"📊 Win Rate: {results['win_rate']:.1%}")
        print(f"📊 Total Profit: ${results['total_profit']:.2f}")
        print(f"📊 Profit Factor: {results['profit_factor']:.2f}")
        print(f"📊 Average Hold Time: {results['avg_hold_time_hours']:.1f} hours")
        print("\n📈 Report saved to 'backtest_report.html'")
        print("🌐 Open the HTML file in your browser to view detailed results!")
    else:
        print(f"❌ Backtest failed: {results['error']}")

if __name__ == "__main__":
    main() 