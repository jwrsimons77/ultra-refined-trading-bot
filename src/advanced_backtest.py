#!/usr/bin/env python3
"""
🎯 Advanced Trading System Backtest
Comprehensive backtest integrating all advanced components:
- Advanced Position Sizing (Kelly Criterion + Volatility)
- Signal Quality Filter (Confluence Analysis)
- Session Optimizer (Peak Trading Hours)
- Dynamic Exit Manager (Trailing Stops + Partial Profits)
- Compound Profit Manager (Exponential Growth)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import json

# Import our advanced components
from forex_signal_generator import ForexSignalGenerator, ForexSignal
from simple_technical_analyzer import SimpleTechnicalAnalyzer
from advanced_position_sizer import AdvancedPositionSizer
from signal_quality_filter import SignalQualityFilter
from session_optimizer import SessionOptimizer
from dynamic_exit_manager import DynamicExitManager
from compound_profit_manager import CompoundProfitManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedTradingBacktest:
    """
    Professional-grade backtest with all advanced trading components
    """
    
    def __init__(self, initial_balance: float = 1000):
        self.initial_balance = initial_balance
        
        # Initialize all components
        self.signal_generator = ForexSignalGenerator()
        self.technical_analyzer = SimpleTechnicalAnalyzer()
        self.position_sizer = AdvancedPositionSizer(initial_balance)
        self.quality_filter = SignalQualityFilter()
        self.session_optimizer = SessionOptimizer()
        self.exit_manager = DynamicExitManager()
        self.compound_manager = CompoundProfitManager(initial_balance)
        
        # Trading parameters
        self.min_confluence_score = 0.65  # Minimum quality score
        self.max_concurrent_positions = 5
        self.min_session_performance = 0.6
        
        # Results tracking
        self.all_signals = []
        self.filtered_signals = []
        self.executed_trades = []
        self.active_positions = []
        self.rejected_signals = []
        
        logger.info("🎯 Advanced Trading Backtest initialized")
    
    def get_forex_data(self, pair: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get forex data from Yahoo Finance."""
        try:
            # Map forex pairs to Yahoo Finance symbols
            yf_symbols = {
                'EUR/USD': 'EURUSD=X', 'GBP/USD': 'GBPUSD=X', 'USD/JPY': 'USDJPY=X',
                'USD/CHF': 'USDCHF=X', 'AUD/USD': 'AUDUSD=X', 'USD/CAD': 'USDCAD=X',
                'NZD/USD': 'NZDUSD=X'
            }
            
            symbol = yf_symbols.get(pair)
            if not symbol:
                logger.error(f"Unknown pair: {pair}")
                return pd.DataFrame()
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date, interval='1h')
            
            if data.empty:
                logger.warning(f"No data for {pair}")
                return pd.DataFrame()
            
            logger.info(f"📊 Retrieved {len(data)} hourly candles for {pair}")
            return data
            
        except Exception as e:
            logger.error(f"Error getting data for {pair}: {e}")
            return pd.DataFrame()
    
    def analyze_signal_quality(self, signal: ForexSignal, technical_data: Dict, 
                             pair_volatility: float) -> Dict:
        """Analyze signal quality using confluence filter."""
        try:
            # Get confluence analysis
            confluence = self.quality_filter.calculate_confluence_score(
                signal, technical_data, pair_volatility
            )
            
            # Check session timing
            session_check = self.session_optimizer.should_trade_now(
                signal.timestamp, self.min_session_performance
            )
            
            # Combine quality factors
            final_score = confluence['confluence_score']
            
            # Session penalty/bonus
            if session_check['should_trade']:
                session_bonus = 0.1
            else:
                session_bonus = -0.2
            
            final_score = max(0.0, min(1.0, final_score + session_bonus))
            
            return {
                'confluence_score': confluence['confluence_score'],
                'session_score': session_check['session_info']['performance_factor'],
                'final_score': final_score,
                'should_trade': final_score >= self.min_confluence_score,
                'confluence_details': confluence,
                'session_details': session_check,
                'rejection_reason': None if final_score >= self.min_confluence_score else 
                                  f"Low quality score: {final_score:.2f} < {self.min_confluence_score:.2f}"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing signal quality: {e}")
            return {
                'final_score': 0.0,
                'should_trade': False,
                'rejection_reason': f"Analysis error: {e}"
            }
    
    def calculate_position_size(self, signal: ForexSignal, quality_analysis: Dict) -> Dict:
        """Calculate optimal position size using advanced sizing."""
        try:
            # Get current balance from compound manager
            current_balance = self.compound_manager.current_balance
            self.position_sizer.account_balance = current_balance
            
            # Calculate base position size
            position_info = self.position_sizer.calculate_optimal_position_size(
                signal, self.active_positions
            )
            
            # Apply compound sizing
            compound_info = self.compound_manager.calculate_compound_position_size(
                signal, position_info['units']
            )
            
            # Session multiplier
            session_multiplier = self.session_optimizer.calculate_session_multiplier(
                signal.timestamp
            )
            
            # Quality multiplier (higher quality = larger size)
            quality_multiplier = 0.5 + (quality_analysis['final_score'] * 1.0)
            
            # Final position size
            final_units = int(compound_info['units'] * session_multiplier * quality_multiplier)
            final_units = max(1000, min(final_units, 100000))  # Limits
            
            # Recalculate risk amount
            if 'JPY' in signal.pair:
                pip_value = 0.01
            else:
                pip_value = 0.0001
            
            stop_distance_pips = abs(signal.entry_price - signal.stop_loss) / pip_value
            pip_value_usd = 0.10
            final_risk = stop_distance_pips * pip_value_usd * (final_units / 1000)
            
            return {
                'units': final_units,
                'risk_amount': final_risk,
                'base_units': position_info['units'],
                'compound_units': compound_info['units'],
                'session_multiplier': session_multiplier,
                'quality_multiplier': quality_multiplier,
                'final_multiplier': final_units / position_info['units'] if position_info['units'] > 0 else 1.0
            }
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return {
                'units': 1000,
                'risk_amount': 30.0,
                'final_multiplier': 1.0
            }
    
    def simulate_trade_execution(self, signal: ForexSignal, position_info: Dict, 
                               price_data: pd.DataFrame) -> Dict:
        """Simulate trade execution with dynamic exit management."""
        try:
            entry_time = signal.timestamp
            entry_price = signal.entry_price
            target_price = signal.target_price
            stop_loss = signal.stop_loss
            units = position_info['units']
            
            # Find entry point in data
            entry_idx = None
            for i, (timestamp, row) in enumerate(price_data.iterrows()):
                if timestamp >= entry_time:
                    entry_idx = i
                    break
            
            if entry_idx is None:
                return {'outcome': 'NO_ENTRY', 'reason': 'Entry time not found in data'}
            
            # Track trade progress
            highest_favorable = entry_price
            current_stop = stop_loss
            current_target = target_price
            partial_profits_taken = []
            
            # Simulate trade progression
            for i in range(entry_idx + 1, len(price_data)):
                timestamp, row = list(price_data.iterrows())[i]
                current_price = row['Close']
                
                # Update highest favorable price
                if signal.signal_type == "BUY":
                    if current_price > highest_favorable:
                        highest_favorable = current_price
                else:  # SELL
                    if current_price < highest_favorable:
                        highest_favorable = current_price
                
                # Check exit conditions using dynamic exit manager
                exit_strategy = self.exit_manager.generate_exit_strategy(
                    signal, current_price, highest_favorable, 
                    pair_volatility=0.08, current_time=timestamp
                )
                
                # Update stops and targets
                if exit_strategy['should_update_stops']:
                    current_stop = exit_strategy['new_stop_loss']
                    current_target = exit_strategy['new_target']
                
                # Check for forced exit
                if exit_strategy['should_close_position']:
                    # Close at current price
                    if signal.signal_type == "BUY":
                        profit_pips = (current_price - entry_price) / (0.01 if 'JPY' in signal.pair else 0.0001)
                    else:
                        profit_pips = (entry_price - current_price) / (0.01 if 'JPY' in signal.pair else 0.0001)
                    
                    profit_usd = profit_pips * 0.10 * (units / 1000)
                    
                    return {
                        'outcome': 'FORCED_EXIT',
                        'exit_price': current_price,
                        'exit_time': timestamp,
                        'profit_pips': profit_pips,
                        'profit_usd': profit_usd,
                        'hold_time_hours': (timestamp - entry_time).total_seconds() / 3600,
                        'exit_reason': exit_strategy['primary_action']['reason']
                    }
                
                # Check stop loss
                if signal.signal_type == "BUY" and current_price <= current_stop:
                    profit_pips = (current_stop - entry_price) / (0.01 if 'JPY' in signal.pair else 0.0001)
                    profit_usd = profit_pips * 0.10 * (units / 1000)
                    
                    return {
                        'outcome': 'STOP_LOSS',
                        'exit_price': current_stop,
                        'exit_time': timestamp,
                        'profit_pips': profit_pips,
                        'profit_usd': profit_usd,
                        'hold_time_hours': (timestamp - entry_time).total_seconds() / 3600
                    }
                
                elif signal.signal_type == "SELL" and current_price >= current_stop:
                    profit_pips = (entry_price - current_stop) / (0.01 if 'JPY' in signal.pair else 0.0001)
                    profit_usd = profit_pips * 0.10 * (units / 1000)
                    
                    return {
                        'outcome': 'STOP_LOSS',
                        'exit_price': current_stop,
                        'exit_time': timestamp,
                        'profit_pips': profit_pips,
                        'profit_usd': profit_usd,
                        'hold_time_hours': (timestamp - entry_time).total_seconds() / 3600
                    }
                
                # Check target
                if signal.signal_type == "BUY" and current_price >= current_target:
                    profit_pips = (current_target - entry_price) / (0.01 if 'JPY' in signal.pair else 0.0001)
                    profit_usd = profit_pips * 0.10 * (units / 1000)
                    
                    return {
                        'outcome': 'TARGET_HIT',
                        'exit_price': current_target,
                        'exit_time': timestamp,
                        'profit_pips': profit_pips,
                        'profit_usd': profit_usd,
                        'hold_time_hours': (timestamp - entry_time).total_seconds() / 3600
                    }
                
                elif signal.signal_type == "SELL" and current_price <= current_target:
                    profit_pips = (entry_price - current_target) / (0.01 if 'JPY' in signal.pair else 0.0001)
                    profit_usd = profit_pips * 0.10 * (units / 1000)
                    
                    return {
                        'outcome': 'TARGET_HIT',
                        'exit_price': current_target,
                        'exit_time': timestamp,
                        'profit_pips': profit_pips,
                        'profit_usd': profit_usd,
                        'hold_time_hours': (timestamp - entry_time).total_seconds() / 3600
                    }
                
                # Check for timeout (48 hours max)
                if (timestamp - entry_time).total_seconds() > 48 * 3600:
                    if signal.signal_type == "BUY":
                        profit_pips = (current_price - entry_price) / (0.01 if 'JPY' in signal.pair else 0.0001)
                    else:
                        profit_pips = (entry_price - current_price) / (0.01 if 'JPY' in signal.pair else 0.0001)
                    
                    profit_usd = profit_pips * 0.10 * (units / 1000)
                    
                    return {
                        'outcome': 'TIMEOUT',
                        'exit_price': current_price,
                        'exit_time': timestamp,
                        'profit_pips': profit_pips,
                        'profit_usd': profit_usd,
                        'hold_time_hours': 48.0
                    }
            
            # If we reach here, trade wasn't closed
            return {'outcome': 'NO_EXIT', 'reason': 'End of data reached'}
            
        except Exception as e:
            logger.error(f"Error simulating trade: {e}")
            return {'outcome': 'ERROR', 'reason': str(e)}
    
    def run_backtest(self, pairs: List[str], start_date: datetime, end_date: datetime,
                    scan_interval_hours: int = 6) -> Dict:
        """Run comprehensive backtest with all advanced components."""
        try:
            logger.info(f"🎯 Starting advanced backtest: {start_date} to {end_date}")
            logger.info(f"📊 Pairs: {pairs}")
            logger.info(f"⏰ Scan interval: {scan_interval_hours} hours")
            
            # Get data for all pairs
            pair_data = {}
            for pair in pairs:
                data = self.get_forex_data(pair, start_date, end_date)
                if not data.empty:
                    pair_data[pair] = data
            
            if not pair_data:
                logger.error("No data retrieved for any pairs")
                return {}
            
            # Generate scan times
            scan_times = []
            current_time = start_date
            while current_time <= end_date:
                scan_times.append(current_time)
                current_time += timedelta(hours=scan_interval_hours)
            
            logger.info(f"📅 Generated {len(scan_times)} scan times")
            
            # Process each scan time
            for scan_time in scan_times:
                logger.info(f"🔍 Scanning at {scan_time}")
                
                # Check each pair for signals
                for pair in pairs:
                    if pair not in pair_data:
                        continue
                    
                    try:
                        # Get price data up to scan time
                        data = pair_data[pair]
                        scan_data = data[data.index <= scan_time]
                        
                        if len(scan_data) < 50:  # Need enough data for analysis
                            continue
                        
                        # Get current price
                        current_price = scan_data['Close'].iloc[-1]
                        
                        # Generate technical analysis
                        technical_analysis = self.technical_analyzer.analyze_pair(
                            pair, scan_data, scan_time
                        )
                        
                        # Generate signal
                        signal = self.signal_generator.generate_signal(
                            pair, current_price, technical_analysis, scan_time
                        )
                        
                        if signal:
                            self.all_signals.append(signal)
                            
                            # Get pair volatility
                            pair_volatility = self.position_sizer.get_pair_volatility(pair)
                            
                            # Analyze signal quality
                            quality_analysis = self.analyze_signal_quality(
                                signal, technical_analysis, pair_volatility
                            )
                            
                            if quality_analysis['should_trade']:
                                # Check position limits
                                if len(self.active_positions) >= self.max_concurrent_positions:
                                    self.rejected_signals.append({
                                        'signal': signal,
                                        'reason': 'Max concurrent positions reached'
                                    })
                                    continue
                                
                                # Calculate position size
                                position_info = self.calculate_position_size(signal, quality_analysis)
                                
                                # Execute trade simulation
                                future_data = data[data.index > scan_time]
                                if len(future_data) > 0:
                                    trade_result = self.simulate_trade_execution(
                                        signal, position_info, future_data
                                    )
                                    
                                    if trade_result['outcome'] not in ['NO_ENTRY', 'NO_EXIT', 'ERROR']:
                                        # Record successful trade
                                        trade_record = {
                                            'signal': signal,
                                            'position_info': position_info,
                                            'quality_analysis': quality_analysis,
                                            'trade_result': trade_result,
                                            'entry_time': scan_time,
                                            'pair': pair
                                        }
                                        
                                        self.executed_trades.append(trade_record)
                                        self.filtered_signals.append(signal)
                                        
                                        # Update compound manager
                                        outcome = 'WIN' if trade_result['profit_usd'] > 0 else 'LOSS'
                                        self.compound_manager.update_balance({
                                            'profit_loss': trade_result['profit_usd'],
                                            'outcome': outcome,
                                            'pips_gained': trade_result['profit_pips'],
                                            'pair': pair
                                        })
                                        
                                        logger.info(f"✅ Trade executed: {pair} {signal.signal_type} → "
                                                  f"{outcome} ${trade_result['profit_usd']:.2f}")
                                    
                                    else:
                                        self.rejected_signals.append({
                                            'signal': signal,
                                            'reason': f"Execution failed: {trade_result.get('reason', 'Unknown')}"
                                        })
                                
                            else:
                                self.rejected_signals.append({
                                    'signal': signal,
                                    'reason': quality_analysis['rejection_reason']
                                })
                    
                    except Exception as e:
                        logger.error(f"Error processing {pair} at {scan_time}: {e}")
                        continue
            
            # Calculate final results
            results = self.calculate_backtest_results()
            logger.info("🎯 Backtest completed successfully")
            
            return results
            
        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            return {}
    
    def calculate_backtest_results(self) -> Dict:
        """Calculate comprehensive backtest results."""
        try:
            if not self.executed_trades:
                return {
                    'total_trades': 0,
                    'error': 'No trades executed'
                }
            
            # Basic statistics
            total_trades = len(self.executed_trades)
            winning_trades = [t for t in self.executed_trades if t['trade_result']['profit_usd'] > 0]
            losing_trades = [t for t in self.executed_trades if t['trade_result']['profit_usd'] < 0]
            
            win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
            
            # Profit calculations
            total_profit = sum(t['trade_result']['profit_usd'] for t in self.executed_trades)
            total_pips = sum(t['trade_result']['profit_pips'] for t in self.executed_trades)
            
            avg_win = np.mean([t['trade_result']['profit_usd'] for t in winning_trades]) if winning_trades else 0
            avg_loss = np.mean([t['trade_result']['profit_usd'] for t in losing_trades]) if losing_trades else 0
            
            # Performance metrics
            final_balance = self.compound_manager.current_balance
            total_return = ((final_balance / self.initial_balance) - 1) * 100
            
            # Risk metrics
            profit_factor = abs(avg_win * len(winning_trades) / (avg_loss * len(losing_trades))) if losing_trades else float('inf')
            
            # Time analysis
            avg_hold_time = np.mean([t['trade_result']['hold_time_hours'] for t in self.executed_trades])
            
            # Pair performance
            pair_performance = {}
            for trade in self.executed_trades:
                pair = trade['pair']
                if pair not in pair_performance:
                    pair_performance[pair] = {
                        'trades': 0, 'wins': 0, 'profit': 0, 'pips': 0
                    }
                
                pair_performance[pair]['trades'] += 1
                pair_performance[pair]['profit'] += trade['trade_result']['profit_usd']
                pair_performance[pair]['pips'] += trade['trade_result']['profit_pips']
                
                if trade['trade_result']['profit_usd'] > 0:
                    pair_performance[pair]['wins'] += 1
            
            # Add win rates to pair performance
            for pair in pair_performance:
                pair_performance[pair]['win_rate'] = pair_performance[pair]['wins'] / pair_performance[pair]['trades']
            
            return {
                'total_trades': total_trades,
                'winning_trades': len(winning_trades),
                'losing_trades': len(losing_trades),
                'win_rate': win_rate,
                'total_profit': total_profit,
                'total_pips': total_pips,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'profit_factor': profit_factor,
                'initial_balance': self.initial_balance,
                'final_balance': final_balance,
                'total_return': total_return,
                'avg_hold_time': avg_hold_time,
                'pair_performance': pair_performance,
                'all_signals_count': len(self.all_signals),
                'filtered_signals_count': len(self.filtered_signals),
                'rejected_signals_count': len(self.rejected_signals),
                'signal_filter_rate': len(self.filtered_signals) / len(self.all_signals) if self.all_signals else 0,
                'compound_metrics': self.compound_manager.calculate_performance_metrics(),
                'executed_trades': self.executed_trades
            }
            
        except Exception as e:
            logger.error(f"Error calculating results: {e}")
            return {'error': str(e)}

def run_advanced_backtest():
    """Run the advanced backtest and return results."""
    try:
        # Initialize backtest
        backtest = AdvancedTradingBacktest(initial_balance=1000)
        
        # Test parameters
        pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD']
        start_date = datetime(2024, 12, 1)
        end_date = datetime(2024, 12, 15)  # 2 weeks
        scan_interval = 6  # Every 6 hours
        
        # Run backtest
        results = backtest.run_backtest(pairs, start_date, end_date, scan_interval)
        
        return results
        
    except Exception as e:
        logger.error(f"Error in advanced backtest: {e}")
        return {'error': str(e)}

if __name__ == "__main__":
    print("🎯 ADVANCED TRADING SYSTEM BACKTEST")
    print("=" * 60)
    
    results = run_advanced_backtest()
    
    if 'error' in results:
        print(f"❌ Error: {results['error']}")
    else:
        print(f"📊 Total Trades: {results['total_trades']}")
        print(f"🎯 Win Rate: {results['win_rate']:.1%}")
        print(f"💰 Total Profit: ${results['total_profit']:.2f}")
        print(f"📈 Total Return: {results['total_return']:.1f}%")
        print(f"⚡ Profit Factor: {results['profit_factor']:.2f}") 