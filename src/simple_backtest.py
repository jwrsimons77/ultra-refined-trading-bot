"""
Simple FREE Backtesting System
Tests forex signals using historical OANDA data
No external costs - uses existing API access
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
from simple_technical_analyzer import SimpleTechnicalAnalyzer
from forex_signal_generator import ForexSignalGenerator

logger = logging.getLogger(__name__)

class SimpleBacktester:
    """
    FREE backtesting system using OANDA historical data
    Tests signal performance over historical periods
    """
    
    def __init__(self, initial_balance: float = 10000):
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.analyzer = SimpleTechnicalAnalyzer()
        self.signal_generator = ForexSignalGenerator()
        
        # Track performance
        self.trades = []
        self.equity_curve = []
        
    def get_historical_data_range(self, pair: str, start_days_ago: int = 30, end_days_ago: int = 0) -> Optional[pd.DataFrame]:
        """
        Get historical data for backtesting (simplified approach)
        """
        try:
            # Get historical data (simplified approach)
            hours_needed = start_days_ago * 24
            df = self.analyzer.get_historical_data(pair, 'H1', count=hours_needed)
            
            if df is None or len(df) < 100:
                logger.warning(f"Insufficient data for {pair}")
                return None
            
            # Use the most recent data (last X days)
            if end_days_ago > 0:
                # Remove the most recent days if specified
                end_hours = end_days_ago * 24
                df = df.iloc[:-end_hours] if end_hours < len(df) else df
            
            logger.info(f"📊 Backtest data for {pair}: {len(df)} candles over ~{len(df)/24:.1f} days")
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting historical data for {pair}: {e}")
            return None
    
    def simulate_signal_at_time(self, pair: str, timestamp: datetime, price_data: pd.DataFrame) -> Optional[Dict]:
        """
        Simulate generating a signal at a specific historical time
        """
        try:
            # Get data up to this timestamp for analysis
            historical_data = price_data[price_data.index <= timestamp]
            
            if len(historical_data) < 50:
                return None
            
            # Get the price at signal time
            entry_price = historical_data['close'].iloc[-1]
            
            # Simulate technical analysis at this point in time
            # Use last 50 candles for analysis
            analysis_data = historical_data.tail(50)
            
            # Calculate RSI
            rsi = self.analyzer.calculate_rsi(analysis_data['close']).iloc[-1]
            
            # Calculate MACD
            macd_data = self.analyzer.calculate_macd(analysis_data['close'])
            macd_signal = 1 if macd_data['macd'].iloc[-1] > macd_data['signal'].iloc[-1] else -1
            
            # Simple signal logic (more lenient for backtesting)
            if rsi < 35 and macd_signal > 0:  # Relaxed from 30
                signal_type = "BUY"
                signal_strength = 0.7
            elif rsi > 65 and macd_signal < 0:  # Relaxed from 70
                signal_type = "SELL"
                signal_strength = 0.7
            elif rsi < 40:  # Additional buy signals
                signal_type = "BUY"
                signal_strength = 0.5
            elif rsi > 60:  # Additional sell signals
                signal_type = "SELL"
                signal_strength = 0.5
            else:
                return None  # No signal
            
            # Calculate dynamic levels
            atr_series = self.analyzer.calculate_atr(analysis_data)
            atr = atr_series.iloc[-1] if not atr_series.empty else 0.001
            
            # Use realistic multipliers
            stop_multiplier = 0.5
            target_multiplier = 1.0
            
            # Cap ATR
            max_atr = 0.01
            capped_atr = min(atr, max_atr)
            
            stop_distance = capped_atr * stop_multiplier
            target_distance = capped_atr * target_multiplier
            
            if signal_type == "BUY":
                stop_loss = entry_price - stop_distance
                target = entry_price + target_distance
            else:
                stop_loss = entry_price + stop_distance
                target = entry_price - target_distance
            
            # Calculate pips
            pip_value = 0.01 if 'JPY' in pair else 0.0001
            target_pips = max(25, int(target_distance / pip_value))
            stop_pips = max(15, int(stop_distance / pip_value))
            
            return {
                'pair': pair,
                'signal_type': signal_type,
                'entry_price': entry_price,
                'target': target,
                'stop_loss': stop_loss,
                'target_pips': target_pips,
                'stop_pips': stop_pips,
                'strength': signal_strength,
                'timestamp': timestamp,
                'atr': atr
            }
            
        except Exception as e:
            logger.error(f"Error simulating signal for {pair} at {timestamp}: {e}")
            return None
    
    def simulate_trade_outcome(self, signal: Dict, future_data: pd.DataFrame) -> Dict:
        """
        Simulate what would have happened to this trade
        """
        try:
            entry_price = signal['entry_price']
            target = signal['target']
            stop_loss = signal['stop_loss']
            signal_type = signal['signal_type']
            
            # Track the trade through future price action
            for i, (timestamp, row) in enumerate(future_data.iterrows()):
                high = row['high']
                low = row['low']
                close = row['close']
                
                # Check if stop loss or target was hit
                if signal_type == "BUY":
                    if low <= stop_loss:
                        # Stop loss hit
                        exit_price = stop_loss
                        outcome = "LOSS"
                        pip_val = 0.01 if 'JPY' in signal['pair'] else 0.0001
                        pips = int((exit_price - entry_price) / pip_val)
                        hours_held = i + 1
                        break
                    elif high >= target:
                        # Target hit
                        exit_price = target
                        outcome = "WIN"
                        pip_val = 0.01 if 'JPY' in signal['pair'] else 0.0001
                        pips = int((exit_price - entry_price) / pip_val)
                        hours_held = i + 1
                        break
                else:  # SELL
                    if high >= stop_loss:
                        # Stop loss hit
                        exit_price = stop_loss
                        outcome = "LOSS"
                        pip_val = 0.01 if 'JPY' in signal['pair'] else 0.0001
                        pips = int((entry_price - exit_price) / pip_val)
                        hours_held = i + 1
                        break
                    elif low <= target:
                        # Target hit
                        exit_price = target
                        outcome = "WIN"
                        pip_val = 0.01 if 'JPY' in signal['pair'] else 0.0001
                        pips = int((entry_price - exit_price) / pip_val)
                        hours_held = i + 1
                        break
            else:
                # Trade didn't close within available data - close at last price
                exit_price = future_data['close'].iloc[-1]
                pip_val = 0.01 if 'JPY' in signal['pair'] else 0.0001
                if signal_type == "BUY":
                    pips = int((exit_price - entry_price) / pip_val)
                else:
                    pips = int((entry_price - exit_price) / pip_val)
                
                outcome = "WIN" if pips > 0 else "LOSS"
                hours_held = len(future_data)
            
            # Calculate P&L
            pip_value_usd = 1.0  # Simplified - $1 per pip for 10k units
            pnl = pips * pip_value_usd
            
            return {
                'outcome': outcome,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'pips': pips,
                'pnl': pnl,
                'hours_held': hours_held,
                'days_held': hours_held / 24
            }
            
        except Exception as e:
            logger.error(f"Error simulating trade outcome: {e}")
            return {
                'outcome': 'ERROR',
                'pips': 0,
                'pnl': 0,
                'hours_held': 0,
                'days_held': 0
            }
    
    def run_backtest(self, pairs: List[str], days_back: int = 14) -> Dict:
        """
        Run backtest on multiple pairs over specified period
        """
        logger.info(f"🔄 Starting backtest on {len(pairs)} pairs over {days_back} days")
        
        all_trades = []
        
        for pair in pairs:
            logger.info(f"📊 Backtesting {pair}...")
            
            # Get historical data
            price_data = self.get_historical_data_range(pair, days_back, 0)
            if price_data is None:
                continue
            
            # Look for signals every 4 hours (to avoid over-trading)
            signal_interval = 4
            
            for i in range(50, len(price_data) - 24, signal_interval):  # Leave 24 hours for trade simulation
                signal_time = price_data.index[i]
                
                # Get data up to signal time
                historical_data = price_data.iloc[:i+1]
                
                # Generate signal
                signal = self.simulate_signal_at_time(pair, signal_time, historical_data)
                
                if signal is None:
                    continue
                
                # Get future data to simulate trade
                future_data = price_data.iloc[i+1:i+1+48]  # Next 48 hours
                
                if len(future_data) < 10:
                    continue
                
                # Simulate trade outcome
                trade_result = self.simulate_trade_outcome(signal, future_data)
                
                # Combine signal and result
                trade = {**signal, **trade_result}
                all_trades.append(trade)
                
                logger.info(f"  📈 {signal['signal_type']} signal at {signal_time.strftime('%Y-%m-%d %H:%M')} -> {trade_result['outcome']} ({trade_result['pips']} pips in {trade_result['days_held']:.1f} days)")
        
        # Calculate performance metrics
        if not all_trades:
            logger.warning("No trades generated in backtest")
            return {'error': 'No trades generated'}
        
        wins = [t for t in all_trades if t['outcome'] == 'WIN']
        losses = [t for t in all_trades if t['outcome'] == 'LOSS']
        
        total_trades = len(all_trades)
        win_rate = len(wins) / total_trades if total_trades > 0 else 0
        
        total_pips = sum(t['pips'] for t in all_trades)
        total_pnl = sum(t['pnl'] for t in all_trades)
        
        avg_win_pips = np.mean([t['pips'] for t in wins]) if wins else 0
        avg_loss_pips = np.mean([abs(t['pips']) for t in losses]) if losses else 0
        
        avg_hold_time = np.mean([t['days_held'] for t in all_trades]) if all_trades else 0
        
        results = {
            'total_trades': total_trades,
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': win_rate,
            'total_pips': total_pips,
            'total_pnl': total_pnl,
            'avg_win_pips': avg_win_pips,
            'avg_loss_pips': avg_loss_pips,
            'avg_hold_time_days': avg_hold_time,
            'profit_factor': (avg_win_pips * len(wins)) / (avg_loss_pips * len(losses)) if losses else float('inf'),
            'trades': all_trades
        }
        
        return results
    
    def print_backtest_results(self, results: Dict):
        """
        Print formatted backtest results
        """
        if 'error' in results:
            print(f"❌ Backtest Error: {results['error']}")
            return
        
        print("\n" + "="*60)
        print("🔄 BACKTEST RESULTS")
        print("="*60)
        
        print(f"📊 Total Trades: {results['total_trades']}")
        print(f"✅ Wins: {results['wins']} ({results['win_rate']:.1%})")
        print(f"❌ Losses: {results['losses']} ({1-results['win_rate']:.1%})")
        print(f"📈 Total Pips: {results['total_pips']:+.0f}")
        print(f"💰 Total P&L: ${results['total_pnl']:+.2f}")
        print(f"⏰ Avg Hold Time: {results['avg_hold_time_days']:.1f} days")
        print(f"🎯 Avg Win: {results['avg_win_pips']:.0f} pips")
        print(f"🛑 Avg Loss: {results['avg_loss_pips']:.0f} pips")
        print(f"📊 Profit Factor: {results['profit_factor']:.2f}")
        
        print(f"\n📋 Recent Trades:")
        for i, trade in enumerate(results['trades'][-5:], 1):  # Last 5 trades
            print(f"  {i}. {trade['pair']} {trade['signal_type']} -> {trade['outcome']} ({trade['pips']:+.0f} pips in {trade['days_held']:.1f} days)")

def main():
    """Test the backtesting system"""
    backtest = SimpleBacktester()
    
    # Test on major pairs over last 2 weeks
    pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD']
    
    print("🔄 Running FREE Backtest...")
    print(f"📊 Testing {len(pairs)} pairs over 14 days")
    print("⏰ This may take 1-2 minutes...")
    
    results = backtest.run_backtest(pairs, days_back=14)
    backtest.print_backtest_results(results)

if __name__ == "__main__":
    main() 