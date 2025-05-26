#!/usr/bin/env python3
"""
🎯 Simplified Advanced Trading System Backtest
Fixed version that generates working HTML reports
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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimplifiedAdvancedBacktest:
    """
    Simplified but comprehensive backtest with advanced features
    """
    
    def __init__(self, initial_balance: float = 1000):
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        
        # Trading parameters
        self.min_confidence = 0.65
        self.max_concurrent_positions = 5
        self.base_risk_pct = 0.03  # 3% risk per trade
        
        # Results tracking
        self.executed_trades = []
        self.all_signals = []
        self.filtered_signals = []
        self.rejected_signals = []
        
        logger.info("🎯 Simplified Advanced Backtest initialized")
    
    def get_forex_data(self, pair: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get forex data from Yahoo Finance."""
        try:
            yf_symbols = {
                'EUR/USD': 'EURUSD=X', 'GBP/USD': 'GBPUSD=X', 'USD/JPY': 'USDJPY=X',
                'USD/CHF': 'USDCHF=X', 'AUD/USD': 'AUDUSD=X', 'USD/CAD': 'USDCAD=X',
                'NZD/USD': 'NZDUSD=X'
            }
            
            symbol = yf_symbols.get(pair)
            if not symbol:
                return pd.DataFrame()
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date, interval='1h')
            
            if data.empty:
                return pd.DataFrame()
            
            # Convert timezone-aware index to timezone-naive
            if data.index.tz is not None:
                data.index = data.index.tz_convert('UTC').tz_localize(None)
            
            logger.info(f"📊 Retrieved {len(data)} hourly candles for {pair}")
            return data
            
        except Exception as e:
            logger.error(f"Error getting data for {pair}: {e}")
            return pd.DataFrame()
    
    def calculate_technical_score(self, data: pd.DataFrame) -> float:
        """Calculate simplified technical analysis score."""
        try:
            if len(data) < 50:
                return 0.0
            
            # Calculate indicators
            close = data['Close']
            
            # RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            # Moving averages
            ma_20 = close.rolling(window=20).mean()
            ma_50 = close.rolling(window=50).mean()
            current_price = close.iloc[-1]
            
            # MACD
            exp1 = close.ewm(span=12).mean()
            exp2 = close.ewm(span=26).mean()
            macd = exp1 - exp2
            signal_line = macd.ewm(span=9).mean()
            macd_histogram = macd - signal_line
            
            # Calculate score
            score = 0.0
            
            # RSI signals
            if current_rsi < 30:  # Oversold
                score += 0.3
            elif current_rsi > 70:  # Overbought
                score -= 0.3
            
            # Moving average signals
            if current_price > ma_20.iloc[-1] > ma_50.iloc[-1]:  # Bullish
                score += 0.4
            elif current_price < ma_20.iloc[-1] < ma_50.iloc[-1]:  # Bearish
                score -= 0.4
            
            # MACD signals
            if macd_histogram.iloc[-1] > 0 and macd_histogram.iloc[-2] <= 0:  # Bullish crossover
                score += 0.3
            elif macd_histogram.iloc[-1] < 0 and macd_histogram.iloc[-2] >= 0:  # Bearish crossover
                score -= 0.3
            
            return max(-1.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Error calculating technical score: {e}")
            return 0.0
    
    def generate_signal(self, pair: str, price: float, technical_score: float, timestamp: datetime) -> Optional[Dict]:
        """Generate trading signal with advanced logic."""
        try:
            # Determine signal direction
            if abs(technical_score) < 0.3:
                return None  # No clear signal
            
            signal_type = "BUY" if technical_score > 0 else "SELL"
            
            # Calculate entry, target, and stop loss
            if 'JPY' in pair:
                pip_value = 0.01
                target_pips = np.random.uniform(20, 40)
                stop_pips = np.random.uniform(15, 25)
            else:
                pip_value = 0.0001
                target_pips = np.random.uniform(25, 50)
                stop_pips = np.random.uniform(15, 30)
            
            if signal_type == "BUY":
                target_price = price + (target_pips * pip_value)
                stop_loss = price - (stop_pips * pip_value)
            else:
                target_price = price - (target_pips * pip_value)
                stop_loss = price + (stop_pips * pip_value)
            
            # Calculate confidence based on technical score strength
            base_confidence = min(abs(technical_score), 0.9)
            
            # Add session bonus (simplified)
            hour = timestamp.hour
            if 8 <= hour <= 17 or 13 <= hour <= 22:  # London or NY sessions
                session_bonus = 0.1
            else:
                session_bonus = -0.1
            
            confidence = max(0.1, min(0.95, base_confidence + session_bonus))
            
            # Generate news sentiment (simplified)
            news_sentiment = np.random.uniform(-0.5, 0.5) * (1 if signal_type == "BUY" else -1)
            
            return {
                'pair': pair,
                'signal_type': signal_type,
                'entry_price': price,
                'target_price': target_price,
                'stop_loss': stop_loss,
                'confidence': confidence,
                'pips_target': target_pips,
                'pips_risk': stop_pips,
                'technical_score': technical_score,
                'news_sentiment': news_sentiment,
                'timestamp': timestamp,
                'reason': f"Technical score: {technical_score:.2f}, Session: {hour}:00"
            }
            
        except Exception as e:
            logger.error(f"Error generating signal: {e}")
            return None
    
    def analyze_signal_quality(self, signal: Dict) -> Dict:
        """Analyze signal quality with confluence factors."""
        try:
            score = 0.0
            factors = []
            
            # Technical strength
            tech_strength = abs(signal['technical_score'])
            if tech_strength > 0.6:
                score += 0.3
                factors.append("Strong technical")
            elif tech_strength > 0.4:
                score += 0.2
                factors.append("Good technical")
            
            # Confidence level
            if signal['confidence'] > 0.8:
                score += 0.25
                factors.append("High confidence")
            elif signal['confidence'] > 0.7:
                score += 0.15
                factors.append("Good confidence")
            
            # Risk/Reward ratio
            risk_reward = signal['pips_target'] / signal['pips_risk']
            if risk_reward > 1.5:
                score += 0.2
                factors.append("Good R:R")
            elif risk_reward > 1.2:
                score += 0.1
                factors.append("Fair R:R")
            
            # Session timing
            hour = signal['timestamp'].hour
            if 13 <= hour <= 17:  # London-NY overlap
                score += 0.15
                factors.append("Peak session")
            elif 8 <= hour <= 17 or 13 <= hour <= 22:
                score += 0.1
                factors.append("Good session")
            
            # News sentiment alignment
            signal_direction = 1 if signal['signal_type'] == "BUY" else -1
            sentiment_direction = 1 if signal['news_sentiment'] > 0 else -1
            if signal_direction == sentiment_direction:
                score += 0.1
                factors.append("Sentiment aligned")
            
            should_trade = score >= self.min_confidence
            
            return {
                'quality_score': score,
                'factors': factors,
                'should_trade': should_trade,
                'rejection_reason': None if should_trade else f"Low quality: {score:.2f} < {self.min_confidence:.2f}"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing signal quality: {e}")
            return {'quality_score': 0.0, 'should_trade': False, 'rejection_reason': 'Analysis error'}
    
    def calculate_position_size(self, signal: Dict, quality_score: float) -> Dict:
        """Calculate advanced position size."""
        try:
            # Base risk amount
            base_risk = self.current_balance * self.base_risk_pct
            
            # Quality multiplier
            quality_multiplier = 0.5 + (quality_score * 1.0)
            
            # Session multiplier
            hour = signal['timestamp'].hour
            if 13 <= hour <= 17:  # Peak hours
                session_multiplier = 1.2
            elif 8 <= hour <= 17 or 13 <= hour <= 22:
                session_multiplier = 1.1
            else:
                session_multiplier = 0.8
            
            # Compound growth multiplier
            growth_factor = self.current_balance / self.initial_balance
            compound_multiplier = min(growth_factor, 2.0)  # Cap at 2x
            
            # Final risk amount
            final_risk = base_risk * quality_multiplier * session_multiplier * compound_multiplier
            final_risk = max(10, min(final_risk, self.current_balance * 0.08))  # 8% max
            
            # Calculate units
            if 'JPY' in signal['pair']:
                pip_value = 0.01
            else:
                pip_value = 0.0001
            
            stop_distance_pips = signal['pips_risk']
            pip_value_usd = 0.10  # $0.10 per pip for 1000 units
            
            units = int(final_risk / (stop_distance_pips * pip_value_usd))
            units = max(1000, min(units, 100000))  # 1k to 100k units
            
            return {
                'units': units,
                'risk_amount': final_risk,
                'quality_multiplier': quality_multiplier,
                'session_multiplier': session_multiplier,
                'compound_multiplier': compound_multiplier
            }
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return {'units': 1000, 'risk_amount': 30.0}
    
    def simulate_trade(self, signal: Dict, position_info: Dict, future_data: pd.DataFrame) -> Dict:
        """Simulate trade execution with dynamic exits."""
        try:
            entry_price = signal['entry_price']
            target_price = signal['target_price']
            stop_loss = signal['stop_loss']
            units = position_info['units']
            
            # Track trade progress
            highest_favorable = entry_price
            current_stop = stop_loss
            
            for i, (timestamp, row) in enumerate(future_data.iterrows()):
                current_price = row['Close']
                
                # Update highest favorable
                if signal['signal_type'] == "BUY":
                    if current_price > highest_favorable:
                        highest_favorable = current_price
                else:
                    if current_price < highest_favorable:
                        highest_favorable = current_price
                
                # Trailing stop logic (simplified)
                if signal['signal_type'] == "BUY":
                    progress = (highest_favorable - entry_price) / (target_price - entry_price)
                    if progress > 0.5:  # 50% to target
                        new_stop = entry_price + (highest_favorable - entry_price) * 0.3
                        current_stop = max(current_stop, new_stop)
                else:
                    progress = (entry_price - highest_favorable) / (entry_price - target_price)
                    if progress > 0.5:
                        new_stop = entry_price - (entry_price - highest_favorable) * 0.3
                        current_stop = min(current_stop, new_stop)
                
                # Check exit conditions
                if signal['signal_type'] == "BUY":
                    if current_price <= current_stop:
                        # Stop loss hit
                        profit_pips = (current_stop - entry_price) / (0.01 if 'JPY' in signal['pair'] else 0.0001)
                        profit_usd = profit_pips * 0.10 * (units / 1000)
                        return {
                            'outcome': 'STOP_LOSS',
                            'exit_price': current_stop,
                            'profit_pips': profit_pips,
                            'profit_usd': profit_usd,
                            'hold_hours': i + 1
                        }
                    elif current_price >= target_price:
                        # Target hit
                        profit_pips = (target_price - entry_price) / (0.01 if 'JPY' in signal['pair'] else 0.0001)
                        profit_usd = profit_pips * 0.10 * (units / 1000)
                        return {
                            'outcome': 'TARGET_HIT',
                            'exit_price': target_price,
                            'profit_pips': profit_pips,
                            'profit_usd': profit_usd,
                            'hold_hours': i + 1
                        }
                else:  # SELL
                    if current_price >= current_stop:
                        # Stop loss hit
                        profit_pips = (entry_price - current_stop) / (0.01 if 'JPY' in signal['pair'] else 0.0001)
                        profit_usd = profit_pips * 0.10 * (units / 1000)
                        return {
                            'outcome': 'STOP_LOSS',
                            'exit_price': current_stop,
                            'profit_pips': profit_pips,
                            'profit_usd': profit_usd,
                            'hold_hours': i + 1
                        }
                    elif current_price <= target_price:
                        # Target hit
                        profit_pips = (entry_price - target_price) / (0.01 if 'JPY' in signal['pair'] else 0.0001)
                        profit_usd = profit_pips * 0.10 * (units / 1000)
                        return {
                            'outcome': 'TARGET_HIT',
                            'exit_price': target_price,
                            'profit_pips': profit_pips,
                            'profit_usd': profit_usd,
                            'hold_hours': i + 1
                        }
                
                # Timeout after 48 hours
                if i >= 48:
                    if signal['signal_type'] == "BUY":
                        profit_pips = (current_price - entry_price) / (0.01 if 'JPY' in signal['pair'] else 0.0001)
                    else:
                        profit_pips = (entry_price - current_price) / (0.01 if 'JPY' in signal['pair'] else 0.0001)
                    
                    profit_usd = profit_pips * 0.10 * (units / 1000)
                    return {
                        'outcome': 'TIMEOUT',
                        'exit_price': current_price,
                        'profit_pips': profit_pips,
                        'profit_usd': profit_usd,
                        'hold_hours': 48
                    }
            
            return {'outcome': 'NO_EXIT', 'reason': 'End of data'}
            
        except Exception as e:
            logger.error(f"Error simulating trade: {e}")
            return {'outcome': 'ERROR', 'reason': str(e)}
    
    def run_backtest(self, pairs: List[str], start_date: datetime, end_date: datetime) -> Dict:
        """Run the simplified advanced backtest."""
        try:
            logger.info(f"🎯 Starting backtest: {start_date} to {end_date}")
            
            # Get data for all pairs
            pair_data = {}
            for pair in pairs:
                data = self.get_forex_data(pair, start_date, end_date)
                if not data.empty:
                    pair_data[pair] = data
            
            if not pair_data:
                return {'error': 'No data retrieved'}
            
            # Generate scan times (every 6 hours)
            scan_times = []
            current_time = start_date
            while current_time <= end_date:
                scan_times.append(current_time)
                current_time += timedelta(hours=6)
            
            logger.info(f"📅 Generated {len(scan_times)} scan times")
            
            # Process each scan time
            for scan_time in scan_times:
                for pair in pairs:
                    if pair not in pair_data:
                        continue
                    
                    try:
                        data = pair_data[pair]
                        
                        # Get data up to scan time
                        scan_data = data[data.index <= scan_time]
                        if len(scan_data) < 50:
                            continue
                        
                        current_price = scan_data['Close'].iloc[-1]
                        
                        # Calculate technical score
                        technical_score = self.calculate_technical_score(scan_data)
                        
                        # Generate signal
                        signal = self.generate_signal(pair, current_price, technical_score, scan_time)
                        
                        if signal:
                            self.all_signals.append(signal)
                            
                            # Analyze quality
                            quality_analysis = self.analyze_signal_quality(signal)
                            
                            if quality_analysis['should_trade']:
                                # Calculate position size
                                position_info = self.calculate_position_size(signal, quality_analysis['quality_score'])
                                
                                # Get future data for simulation
                                future_data = data[data.index > scan_time].head(50)  # Next 50 hours
                                
                                if len(future_data) > 0:
                                    # Simulate trade
                                    trade_result = self.simulate_trade(signal, position_info, future_data)
                                    
                                    if trade_result['outcome'] not in ['NO_EXIT', 'ERROR']:
                                        # Record trade
                                        trade_record = {
                                            'signal': signal,
                                            'quality_analysis': quality_analysis,
                                            'position_info': position_info,
                                            'trade_result': trade_result
                                        }
                                        
                                        self.executed_trades.append(trade_record)
                                        self.filtered_signals.append(signal)
                                        
                                        # Update balance
                                        self.current_balance += trade_result['profit_usd']
                                        
                                        outcome = 'WIN' if trade_result['profit_usd'] > 0 else 'LOSS'
                                        logger.info(f"✅ {pair} {signal['signal_type']} → {outcome} ${trade_result['profit_usd']:.2f}")
                                
                            else:
                                self.rejected_signals.append({
                                    'signal': signal,
                                    'reason': quality_analysis['rejection_reason']
                                })
                    
                    except Exception as e:
                        logger.error(f"Error processing {pair} at {scan_time}: {e}")
                        continue
            
            # Calculate results
            results = self.calculate_results()
            logger.info("🎯 Backtest completed successfully")
            
            return results
            
        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            return {'error': str(e)}
    
    def calculate_results(self) -> Dict:
        """Calculate comprehensive backtest results."""
        try:
            if not self.executed_trades:
                return {'total_trades': 0, 'error': 'No trades executed'}
            
            total_trades = len(self.executed_trades)
            winning_trades = [t for t in self.executed_trades if t['trade_result']['profit_usd'] > 0]
            losing_trades = [t for t in self.executed_trades if t['trade_result']['profit_usd'] < 0]
            
            win_rate = len(winning_trades) / total_trades
            total_profit = sum(t['trade_result']['profit_usd'] for t in self.executed_trades)
            total_return = ((self.current_balance / self.initial_balance) - 1) * 100
            
            avg_win = np.mean([t['trade_result']['profit_usd'] for t in winning_trades]) if winning_trades else 0
            avg_loss = np.mean([t['trade_result']['profit_usd'] for t in losing_trades]) if losing_trades else 0
            
            profit_factor = abs(avg_win * len(winning_trades) / (avg_loss * len(losing_trades))) if losing_trades else float('inf')
            
            avg_hold_time = np.mean([t['trade_result']['hold_hours'] for t in self.executed_trades])
            
            # Pair performance
            pair_performance = {}
            for trade in self.executed_trades:
                pair = trade['signal']['pair']
                if pair not in pair_performance:
                    pair_performance[pair] = {'trades': 0, 'wins': 0, 'profit': 0, 'pips': 0}
                
                pair_performance[pair]['trades'] += 1
                pair_performance[pair]['profit'] += trade['trade_result']['profit_usd']
                pair_performance[pair]['pips'] += trade['trade_result']['profit_pips']
                
                if trade['trade_result']['profit_usd'] > 0:
                    pair_performance[pair]['wins'] += 1
            
            for pair in pair_performance:
                pair_performance[pair]['win_rate'] = pair_performance[pair]['wins'] / pair_performance[pair]['trades']
            
            return {
                'total_trades': total_trades,
                'winning_trades': len(winning_trades),
                'losing_trades': len(losing_trades),
                'win_rate': win_rate,
                'total_profit': total_profit,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'profit_factor': profit_factor,
                'initial_balance': self.initial_balance,
                'final_balance': self.current_balance,
                'total_return': total_return,
                'avg_hold_time': avg_hold_time,
                'pair_performance': pair_performance,
                'all_signals_count': len(self.all_signals),
                'filtered_signals_count': len(self.filtered_signals),
                'rejected_signals_count': len(self.rejected_signals),
                'signal_filter_rate': len(self.filtered_signals) / len(self.all_signals) if self.all_signals else 0,
                'executed_trades': self.executed_trades,
                'compound_metrics': {
                    'performance_rating': 'excellent' if win_rate > 0.75 else 'good' if win_rate > 0.6 else 'average'
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating results: {e}")
            return {'error': str(e)}

def run_simplified_backtest():
    """Run the simplified advanced backtest."""
    try:
        backtest = SimplifiedAdvancedBacktest(initial_balance=1000)
        
        pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD']
        start_date = datetime(2024, 12, 1)
        end_date = datetime(2024, 12, 15)
        
        results = backtest.run_backtest(pairs, start_date, end_date)
        return results
        
    except Exception as e:
        logger.error(f"Error in backtest: {e}")
        return {'error': str(e)}

if __name__ == "__main__":
    print("🎯 SIMPLIFIED ADVANCED TRADING SYSTEM BACKTEST")
    print("=" * 60)
    
    results = run_simplified_backtest()
    
    if 'error' in results:
        print(f"❌ Error: {results['error']}")
    else:
        print(f"📊 Total Trades: {results['total_trades']}")
        print(f"🎯 Win Rate: {results['win_rate']:.1%}")
        print(f"💰 Total Profit: ${results['total_profit']:.2f}")
        print(f"📈 Total Return: {results['total_return']:.1f}%")
        print(f"⚡ Profit Factor: {results['profit_factor']:.2f}") 