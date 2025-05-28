#!/usr/bin/env python3
"""
Forex Signal Backtesting System
Analyzes performance of different confidence thresholds over time
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import random
from dataclasses import dataclass
from typing import List, Dict, Tuple
import logging
from forex_signal_generator import ForexSignalGenerator, ForexSignal

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BacktestResult:
    """Results from backtesting."""
    confidence_threshold: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_return: float
    max_drawdown: float
    sharpe_ratio: float
    avg_trade_duration: float
    profit_factor: float
    final_balance: float

class ForexBacktester:
    """Comprehensive forex backtesting system."""
    
    def __init__(self, initial_balance: float = 1000.0):
        self.initial_balance = initial_balance
        self.signal_generator = ForexSignalGenerator()
        
    def get_historical_prices(self, pair: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get historical forex prices."""
        try:
            # Convert forex pair to Yahoo Finance format
            if pair == "EUR/USD":
                symbol = "EURUSD=X"
            elif pair == "GBP/USD":
                symbol = "GBPUSD=X"
            elif pair == "USD/JPY":
                symbol = "USDJPY=X"
            elif pair == "USD/CHF":
                symbol = "USDCHF=X"
            elif pair == "AUD/USD":
                symbol = "AUDUSD=X"
            elif pair == "USD/CAD":
                symbol = "USDCAD=X"
            elif pair == "NZD/USD":
                symbol = "NZDUSD=X"
            else:
                symbol = f"{pair.replace('/', '')}=X"
            
            data = yf.download(symbol, start=start_date, end=end_date, interval="1d")
            
            if data.empty:
                logger.warning(f"No data for {pair}, using simulated data")
                return self.generate_simulated_prices(pair, start_date, end_date)
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting historical data for {pair}: {e}")
            return self.generate_simulated_prices(pair, start_date, end_date)
    
    def generate_simulated_prices(self, pair: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Generate realistic simulated forex prices."""
        days = (end_date - start_date).days
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Base prices for major pairs
        base_prices = {
            'EUR/USD': 1.0800, 'GBP/USD': 1.2600, 'USD/JPY': 149.50,
            'USD/CHF': 0.8900, 'AUD/USD': 0.6600, 'USD/CAD': 1.3700, 'NZD/USD': 0.6100
        }
        
        base_price = base_prices.get(pair, 1.0000)
        
        # Generate realistic price movements
        returns = np.random.normal(0, 0.01, len(dates))  # 1% daily volatility
        prices = [base_price]
        
        for ret in returns[1:]:
            new_price = prices[-1] * (1 + ret)
            prices.append(new_price)
        
        df = pd.DataFrame({
            'Open': prices,
            'High': [p * (1 + abs(np.random.normal(0, 0.005))) for p in prices],
            'Low': [p * (1 - abs(np.random.normal(0, 0.005))) for p in prices],
            'Close': prices,
            'Volume': [1000000] * len(prices)
        }, index=dates)
        
        return df

    def simulate_trade_execution(self, signal: ForexSignal, price_data: pd.DataFrame, 
                                entry_date: datetime) -> Dict:
        """Simulate trade execution and outcome."""
        try:
            # Find entry date in price data
            available_dates = price_data.index
            entry_idx = None
            
            for i, date in enumerate(available_dates):
                if date.date() >= entry_date.date():
                    entry_idx = i
                    break
            
            if entry_idx is None or entry_idx >= len(price_data) - 1:
                return {'status': 'NO_DATA', 'profit': 0, 'duration': 0}
            
            entry_price = signal.entry_price
            target_price = signal.target_price
            stop_loss = signal.stop_loss
            
            # Check each day after entry for target/stop hit
            max_hold_days = 30  # Maximum hold period
            
            for i in range(entry_idx + 1, min(entry_idx + max_hold_days, len(price_data))):
                day_data = price_data.iloc[i]
                high = day_data['High']
                low = day_data['Low']
                
                if signal.signal_type == "BUY":
                    # Check if target hit
                    if high >= target_price:
                        profit = target_price - entry_price
                        duration = i - entry_idx
                        return {'status': 'TARGET_HIT', 'profit': profit, 'duration': duration, 'exit_price': target_price}
                    
                    # Check if stop loss hit
                    if low <= stop_loss:
                        profit = stop_loss - entry_price
                        duration = i - entry_idx
                        return {'status': 'STOP_LOSS', 'profit': profit, 'duration': duration, 'exit_price': stop_loss}
                
                else:  # SELL
                    # Check if target hit
                    if low <= target_price:
                        profit = entry_price - target_price
                        duration = i - entry_idx
                        return {'status': 'TARGET_HIT', 'profit': profit, 'duration': duration, 'exit_price': target_price}
                    
                    # Check if stop loss hit
                    if high >= stop_loss:
                        profit = entry_price - stop_loss
                        duration = i - entry_idx
                        return {'status': 'STOP_LOSS', 'profit': profit, 'duration': duration, 'exit_price': stop_loss}
            
            # Trade expired without hitting target or stop
            final_price = price_data.iloc[min(entry_idx + max_hold_days - 1, len(price_data) - 1)]['Close']
            if signal.signal_type == "BUY":
                profit = final_price - entry_price
            else:
                profit = entry_price - final_price
            
            return {'status': 'EXPIRED', 'profit': profit, 'duration': max_hold_days, 'exit_price': final_price}
            
        except Exception as e:
            logger.error(f"Error simulating trade: {e}")
            return {'status': 'ERROR', 'profit': 0, 'duration': 0}

    def backtest_confidence_threshold(self, confidence_threshold: float, 
                                    start_date: datetime, end_date: datetime) -> BacktestResult:
        """Backtest signals with specific confidence threshold."""
        logger.info(f"🔍 Backtesting confidence threshold: {confidence_threshold:.1%}")
        
        balance = self.initial_balance
        trades = []
        daily_balances = []
        
        # Generate signals for each week over the period
        current_date = start_date
        week_delta = timedelta(weeks=1)
        
        while current_date < end_date:
            # Generate signals for this week
            signals = self.signal_generator.generate_forex_signals(
                max_signals=10, 
                min_confidence=confidence_threshold
            )
            
            for signal in signals:
                # Get historical price data for this pair
                price_data = self.get_historical_prices(
                    signal.pair, 
                    current_date - timedelta(days=30), 
                    current_date + timedelta(days=60)
                )
                
                if price_data.empty:
                    continue
                
                # Simulate trade execution
                trade_result = self.simulate_trade_execution(signal, price_data, current_date)
                
                if trade_result['status'] != 'NO_DATA' and trade_result['status'] != 'ERROR':
                    # Calculate position size (2% risk)
                    risk_amount = balance * 0.02
                    
                    # Calculate position size based on stop loss distance
                    if 'JPY' in signal.pair:
                        pip_value = 0.01
                    else:
                        pip_value = 0.0001
                    
                    stop_distance = abs(signal.entry_price - signal.stop_loss)
                    position_size = risk_amount / stop_distance if stop_distance > 0 else 1000
                    
                    # Calculate actual profit/loss
                    profit_pips = trade_result['profit'] / pip_value if pip_value > 0 else 0
                    actual_profit = (trade_result['profit'] / signal.entry_price) * position_size
                    
                    # Update balance
                    balance += actual_profit
                    
                    # Record trade
                    trades.append({
                        'date': current_date,
                        'pair': signal.pair,
                        'type': signal.signal_type,
                        'confidence': signal.confidence,
                        'entry_price': signal.entry_price,
                        'exit_price': trade_result.get('exit_price', signal.entry_price),
                        'target_price': signal.target_price,
                        'stop_loss': signal.stop_loss,
                        'status': trade_result['status'],
                        'profit_pips': profit_pips,
                        'profit_usd': actual_profit,
                        'duration': trade_result['duration'],
                        'balance_after': balance
                    })
            
            daily_balances.append(balance)
            current_date += week_delta
        
        # Calculate performance metrics
        if not trades:
            return BacktestResult(
                confidence_threshold=confidence_threshold,
                total_trades=0, winning_trades=0, losing_trades=0,
                win_rate=0, total_return=0, max_drawdown=0,
                sharpe_ratio=0, avg_trade_duration=0,
                profit_factor=0, final_balance=balance
            )
        
        df_trades = pd.DataFrame(trades)
        
        winning_trades = len(df_trades[df_trades['profit_usd'] > 0])
        losing_trades = len(df_trades[df_trades['profit_usd'] <= 0])
        win_rate = winning_trades / len(trades) if trades else 0
        
        total_return = (balance - self.initial_balance) / self.initial_balance
        
        # Calculate max drawdown
        peak = self.initial_balance
        max_drawdown = 0
        for bal in daily_balances:
            if bal > peak:
                peak = bal
            drawdown = (peak - bal) / peak
            max_drawdown = max(max_drawdown, drawdown)
        
        # Calculate Sharpe ratio (simplified)
        returns = df_trades['profit_usd'].tolist()
        if len(returns) > 1:
            sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
        else:
            sharpe_ratio = 0
        
        avg_duration = df_trades['duration'].mean()
        
        # Profit factor
        gross_profit = df_trades[df_trades['profit_usd'] > 0]['profit_usd'].sum()
        gross_loss = abs(df_trades[df_trades['profit_usd'] < 0]['profit_usd'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        result = BacktestResult(
            confidence_threshold=confidence_threshold,
            total_trades=len(trades),
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            total_return=total_return,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            avg_trade_duration=avg_duration,
            profit_factor=profit_factor,
            final_balance=balance
        )
        
        logger.info(f"✅ Backtest complete: {len(trades)} trades, {win_rate:.1%} win rate, {total_return:.1%} return")
        return result

    def run_comprehensive_backtest(self) -> List[BacktestResult]:
        """Run backtest for multiple confidence thresholds over 1 year."""
        logger.info("🚀 Starting comprehensive 1-year backtest...")
        
        # Test period: 1 year
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        # Test different confidence thresholds
        confidence_levels = [0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85]
        
        results = []
        
        for confidence in confidence_levels:
            result = self.backtest_confidence_threshold(confidence, start_date, end_date)
            results.append(result)
        
        return results

def main():
    """Run the backtesting analysis."""
    backtester = ForexBacktester(initial_balance=1000.0)
    
    print("🔍 Running 1-Year Forex Signal Backtest...")
    print("=" * 60)
    
    results = backtester.run_comprehensive_backtest()
    
    print("\n📊 BACKTEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"{'Confidence':<12} {'Trades':<8} {'Win Rate':<10} {'Return':<10} {'Final $':<10} {'Drawdown':<10}")
    print("-" * 60)
    
    for result in results:
        print(f"{result.confidence_threshold:<12.1%} "
              f"{result.total_trades:<8} "
              f"{result.win_rate:<10.1%} "
              f"{result.total_return:<10.1%} "
              f"${result.final_balance:<9.0f} "
              f"{result.max_drawdown:<10.1%}")
    
    # Find best performing confidence level
    best_result = max(results, key=lambda x: x.total_return)
    
    print(f"\n🏆 BEST PERFORMING CONFIDENCE LEVEL: {best_result.confidence_threshold:.1%}")
    print(f"   Total Return: {best_result.total_return:.1%}")
    print(f"   Final Balance: ${best_result.final_balance:.2f}")
    print(f"   Win Rate: {best_result.win_rate:.1%}")
    print(f"   Total Trades: {best_result.total_trades}")
    print(f"   Max Drawdown: {best_result.max_drawdown:.1%}")
    
    # Specific analysis for 0.65 confidence
    confidence_65_result = next((r for r in results if abs(r.confidence_threshold - 0.65) < 0.01), None)
    
    if confidence_65_result:
        print(f"\n🎯 ANALYSIS FOR 0.65 CONFIDENCE THRESHOLD:")
        print(f"   ✅ Successful: {'YES' if confidence_65_result.total_return > 0 else 'NO'}")
        print(f"   📈 Annual Return: {confidence_65_result.total_return:.1%}")
        print(f"   💰 Profit: ${confidence_65_result.final_balance - 1000:.2f}")
        print(f"   📊 Win Rate: {confidence_65_result.win_rate:.1%}")
        print(f"   🔢 Total Trades: {confidence_65_result.total_trades}")
        print(f"   📉 Max Drawdown: {confidence_65_result.max_drawdown:.1%}")
        print(f"   ⚡ Avg Trade Duration: {confidence_65_result.avg_trade_duration:.1f} days")

if __name__ == "__main__":
    main() 