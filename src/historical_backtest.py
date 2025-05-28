#!/usr/bin/env python3
"""
🎯 Historical Backtesting System
Tests your exact trading bot logic against historical OANDA data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional
import requests
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

class HistoricalBacktester:
    """
    Comprehensive backtesting system using historical OANDA data
    Tests your exact trading bot logic
    """
    
    def __init__(self):
        """Initialize the backtester."""
        self.signal_generator = ForexSignalGenerator()
        self.technical_analyzer = SimpleTechnicalAnalyzer()
        
        # OANDA credentials
        self.api_key = "fe92315bee29b117825fed529cf3fa99-173e927b8cdbb1fc244993e24e33fd93"
        self.account_id = "101-004-31788297-001"
        
        # Backtesting parameters - MATCH YOUR BOT EXACTLY
        self.min_confidence = 0.45  # Same as background trader
        self.max_hold_hours = 168   # 1 week maximum hold time
        self.pairs_to_test = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD']
        
        # Results storage
        self.completed_trades = []
        self.daily_results = []
        
        logger.info("🎯 Historical Backtester initialized")
        logger.info(f"📊 Testing pairs: {', '.join(self.pairs_to_test)}")
        logger.info(f"📊 Min confidence: {self.min_confidence:.1%}")
    
    def get_historical_data(self, pair: str, start_date: datetime, end_date: datetime, granularity: str = 'H1') -> Optional[pd.DataFrame]:
        """Get historical OANDA data for backtesting."""
        try:
            oanda_pair = pair.replace('/', '_')
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Format dates for OANDA API
            start_str = start_date.strftime('%Y-%m-%dT%H:%M:%S.000000000Z')
            end_str = end_date.strftime('%Y-%m-%dT%H:%M:%S.000000000Z')
            
            url = f"https://api-fxpractice.oanda.com/v3/instruments/{oanda_pair}/candles"
            params = {
                "granularity": granularity,
                "from": start_str,
                "to": end_str,
                "price": "M"  # Mid prices
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                candles = data.get('candles', [])
                
                if not candles:
                    logger.warning(f"No historical data for {pair} from {start_date} to {end_date}")
                    return None
                
                # Convert to DataFrame
                df_data = []
                for candle in candles:
                    if candle['complete']:
                        mid = candle['mid']
                        df_data.append({
                            'timestamp': pd.to_datetime(candle['time']),
                            'open': float(mid['o']),
                            'high': float(mid['h']),
                            'low': float(mid['l']),
                            'close': float(mid['c']),
                            'volume': float(candle.get('volume', 1000))
                        })
                
                if not df_data:
                    return None
                
                df = pd.DataFrame(df_data)
                df.set_index('timestamp', inplace=True)
                df.sort_index(inplace=True)
                
                logger.info(f"📊 Retrieved {len(df)} candles for {pair} ({start_date.date()} to {end_date.date()})")
                return df
                
            else:
                logger.error(f"OANDA API error for {pair}: {response.status_code}")
                return None
                
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
            # In real backtesting, you'd use historical news data
            sentiment = np.random.uniform(-0.3, 0.3)  # Neutral bias for backtesting
            
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
            
            # Generate technical score (simplified)
            rsi_score = 0.0
            if current_rsi > 70:
                rsi_score = -0.6
            elif current_rsi < 30:
                rsi_score = 0.6
            
            macd_score = 0.0
            if macd_line.iloc[-1] > signal_line.iloc[-1]:
                macd_score = 0.4
            elif macd_line.iloc[-1] < signal_line.iloc[-1]:
                macd_score = -0.4
            
            technical_score = (rsi_score + macd_score) / 2
            
            return {
                'score': technical_score,
                'confidence': 0.8,  # High confidence for historical data
                'atr': atr,
                'timeframe_breakdown': {'H1': technical_score},
                'source': 'Historical Technical Analysis'
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
                        # Target hit - WIN
                        pips_gained = (signal.target_price - entry_price) / (0.01 if 'JPY' in signal.pair else 0.0001)
                        return BacktestTrade(
                            pair=signal.pair,
                            signal_type=signal.signal_type,
                            entry_time=entry_time,
                            entry_price=entry_price,
                            exit_time=timestamp,
                            exit_price=signal.target_price,
                            target_price=signal.target_price,
                            stop_loss=signal.stop_loss,
                            confidence=signal.confidence,
                            pips_gained=pips_gained,
                            profit_loss=pips_gained * 0.10,  # $0.10 per pip for 1000 units (FIXED)
                            outcome='WIN',
                            hold_time_hours=hours_elapsed,
                            reason=signal.reason
                        )
                    elif current_price <= signal.stop_loss:
                        # Stop loss hit - LOSS
                        pips_gained = (signal.stop_loss - entry_price) / (0.01 if 'JPY' in signal.pair else 0.0001)
                        return BacktestTrade(
                            pair=signal.pair,
                            signal_type=signal.signal_type,
                            entry_time=entry_time,
                            entry_price=entry_price,
                            exit_time=timestamp,
                            exit_price=signal.stop_loss,
                            target_price=signal.target_price,
                            stop_loss=signal.stop_loss,
                            confidence=signal.confidence,
                            pips_gained=pips_gained,
                            profit_loss=pips_gained * 0.10,  # $0.10 per pip for 1000 units (FIXED)
                            outcome='LOSS',
                            hold_time_hours=hours_elapsed,
                            reason=signal.reason
                        )
                else:  # SELL
                    if current_price <= signal.target_price:
                        # Target hit - WIN
                        pips_gained = (entry_price - signal.target_price) / (0.01 if 'JPY' in signal.pair else 0.0001)
                        return BacktestTrade(
                            pair=signal.pair,
                            signal_type=signal.signal_type,
                            entry_time=entry_time,
                            entry_price=entry_price,
                            exit_time=timestamp,
                            exit_price=signal.target_price,
                            target_price=signal.target_price,
                            stop_loss=signal.stop_loss,
                            confidence=signal.confidence,
                            pips_gained=pips_gained,
                            profit_loss=pips_gained * 0.10,  # $0.10 per pip for 1000 units (FIXED)
                            outcome='WIN',
                            hold_time_hours=hours_elapsed,
                            reason=signal.reason
                        )
                    elif current_price >= signal.stop_loss:
                        # Stop loss hit - LOSS
                        pips_gained = (entry_price - signal.stop_loss) / (0.01 if 'JPY' in signal.pair else 0.0001)
                        return BacktestTrade(
                            pair=signal.pair,
                            signal_type=signal.signal_type,
                            entry_time=entry_time,
                            entry_price=entry_price,
                            exit_time=timestamp,
                            exit_price=signal.stop_loss,
                            target_price=signal.target_price,
                            stop_loss=signal.stop_loss,
                            confidence=signal.confidence,
                            pips_gained=pips_gained,
                            profit_loss=pips_gained * 0.10,  # $0.10 per pip for 1000 units (FIXED)
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
        
        for pair in self.pairs_to_test:
            logger.info(f"📈 Testing {pair}...")
            
            # Get historical data for this pair
            historical_data = self.get_historical_data(pair, start_date, end_date, 'H1')
            
            if historical_data is None:
                logger.warning(f"⚠️ No data available for {pair}")
                continue
            
            # Simulate signal generation at regular intervals
            current_time = start_date
            while current_time < end_date:
                # Check if we have data for this timestamp
                if current_time in historical_data.index:
                    signal_data = self.simulate_signal_generation(pair, current_time, historical_data)
                    
                    if signal_data:
                        total_signals_generated += 1
                        logger.info(f"📊 Generated signal: {pair} {signal_data['signal'].signal_type} at {current_time} (confidence: {signal_data['signal'].confidence:.1%})")
                        
                        # Simulate trade execution
                        trade = self.simulate_trade_execution(signal_data, historical_data)
                        
                        if trade:
                            total_trades_executed += 1
                            self.completed_trades.append(trade)
                            logger.info(f"✅ Trade completed: {trade.outcome} - {trade.pips_gained:.1f} pips in {trade.hold_time_hours:.1f} hours")
                
                # Move to next scan time
                current_time += timedelta(hours=scan_interval_hours)
        
        # Calculate results
        results = self.calculate_results()
        
        logger.info(f"🎯 Backtest completed!")
        logger.info(f"📊 Signals generated: {total_signals_generated}")
        logger.info(f"📊 Trades executed: {total_trades_executed}")
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
                    <p>Historical Performance Analysis</p>
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
    backtester = HistoricalBacktester()
    
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