#!/usr/bin/env python3
"""
🎯 Advanced Position Sizing System
Maximizes profit using Kelly Criterion, volatility adjustment, and correlation checks to maximize profits while managing risk.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import yfinance as yf

logger = logging.getLogger(__name__)

class AdvancedPositionSizer:
    """
    Professional position sizing using multiple optimization techniques
    """
    
    def __init__(self, account_balance: float = 1000):
        self.account_balance = account_balance
        self.max_position_risk = 0.05  # 5% max risk per trade
        self.max_portfolio_risk = 0.20  # 20% max total portfolio risk
        self.max_correlation = 0.7  # Max correlation between positions
        
        # Historical performance tracking
        self.trade_history = []
        self.pair_performance = {}
        
        # Volatility data cache
        self.volatility_cache = {}
        self.correlation_cache = {}
        
        logger.info("🎯 Advanced Position Sizer initialized")
    
    def calculate_kelly_optimal_size(self, signal, historical_performance: Dict = None) -> float:
        """
        Calculate optimal position size using Kelly Criterion
        Kelly% = (bp - q) / b
        where: b = odds, p = win probability, q = loss probability
        """
        try:
            if historical_performance:
                win_rate = historical_performance.get('win_rate', 0.6)
                avg_win = historical_performance.get('avg_win', 25)  # pips
                avg_loss = historical_performance.get('avg_loss', 15)  # pips
            else:
                # Use signal confidence as proxy for win rate
                win_rate = min(signal.confidence + 0.1, 0.8)  # Cap at 80%
                avg_win = signal.pips_target
                avg_loss = signal.pips_risk
            
            # Calculate Kelly percentage
            if avg_loss > 0:
                odds = avg_win / avg_loss  # Risk:Reward ratio
                kelly_pct = (win_rate * (odds + 1) - 1) / odds
            else:
                kelly_pct = 0.05  # Default 5%
            
            # Apply Kelly fraction (use 25% of full Kelly for safety)
            fractional_kelly = kelly_pct * 0.25
            
            # Cap at maximum position risk
            optimal_size = min(fractional_kelly, self.max_position_risk)
            optimal_size = max(optimal_size, 0.01)  # Minimum 1%
            
            logger.info(f"📊 Kelly Optimal: {optimal_size:.1%} (Win Rate: {win_rate:.1%}, R:R: {odds:.1f})")
            
            return optimal_size
            
        except Exception as e:
            logger.error(f"Error calculating Kelly size: {e}")
            return 0.03  # Default 3%
    
    def get_pair_volatility(self, pair: str, days: int = 30) -> float:
        """Get recent volatility for the currency pair."""
        try:
            # Check cache first
            cache_key = f"{pair}_{days}"
            if cache_key in self.volatility_cache:
                cache_time, volatility = self.volatility_cache[cache_key]
                if (datetime.now() - cache_time).hours < 4:  # Cache for 4 hours
                    return volatility
            
            # Map forex pairs to Yahoo Finance symbols
            yf_symbols = {
                'EUR/USD': 'EURUSD=X',
                'GBP/USD': 'GBPUSD=X',
                'USD/JPY': 'USDJPY=X',
                'USD/CHF': 'USDCHF=X',
                'AUD/USD': 'AUDUSD=X',
                'USD/CAD': 'USDCAD=X',
                'NZD/USD': 'NZDUSD=X'
            }
            
            yf_symbol = yf_symbols.get(pair)
            if not yf_symbol:
                return 0.02  # Default 2% volatility
            
            # Get historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            ticker = yf.Ticker(yf_symbol)
            data = ticker.history(start=start_date, end=end_date, interval='1d')
            
            if len(data) < 10:
                return 0.02  # Default if insufficient data
            
            # Calculate daily returns
            data['returns'] = data['Close'].pct_change()
            
            # Calculate annualized volatility
            daily_vol = data['returns'].std()
            annualized_vol = daily_vol * np.sqrt(252)  # 252 trading days
            
            # Cache the result
            self.volatility_cache[cache_key] = (datetime.now(), annualized_vol)
            
            logger.info(f"📊 {pair} volatility: {annualized_vol:.1%}")
            return annualized_vol
            
        except Exception as e:
            logger.error(f"Error getting volatility for {pair}: {e}")
            return 0.02  # Default 2%
    
    def volatility_adjusted_size(self, base_size: float, pair: str, target_vol: float = 0.02) -> float:
        """
        Adjust position size based on pair volatility
        Higher volatility = smaller position size
        """
        try:
            current_vol = self.get_pair_volatility(pair)
            
            # Volatility adjustment factor
            vol_adjustment = target_vol / current_vol if current_vol > 0 else 1.0
            
            # Cap adjustment to reasonable range
            vol_adjustment = max(0.5, min(vol_adjustment, 2.0))
            
            adjusted_size = base_size * vol_adjustment
            
            logger.info(f"📊 Volatility adjustment: {vol_adjustment:.2f}x (target: {target_vol:.1%}, actual: {current_vol:.1%})")
            
            return adjusted_size
            
        except Exception as e:
            logger.error(f"Error in volatility adjustment: {e}")
            return base_size
    
    def check_correlation_impact(self, new_pair: str, current_positions: List[Dict]) -> float:
        """
        Check correlation with existing positions and adjust size accordingly
        """
        try:
            if not current_positions:
                return 1.0  # No adjustment needed
            
            max_correlation = 0.0
            
            for position in current_positions:
                existing_pair = position.get('pair', '')
                correlation = self.get_pair_correlation(new_pair, existing_pair)
                max_correlation = max(max_correlation, abs(correlation))
            
            # Reduce position size if high correlation
            if max_correlation > self.max_correlation:
                correlation_factor = 1.0 - (max_correlation - self.max_correlation)
                correlation_factor = max(0.3, correlation_factor)  # Minimum 30% size
                
                logger.info(f"📊 Correlation adjustment: {correlation_factor:.2f}x (max correlation: {max_correlation:.2f})")
                return correlation_factor
            
            return 1.0
            
        except Exception as e:
            logger.error(f"Error checking correlation: {e}")
            return 1.0
    
    def get_pair_correlation(self, pair1: str, pair2: str, days: int = 60) -> float:
        """Calculate correlation between two currency pairs."""
        try:
            if pair1 == pair2:
                return 1.0
            
            # Check cache
            cache_key = f"{pair1}_{pair2}_{days}"
            if cache_key in self.correlation_cache:
                cache_time, correlation = self.correlation_cache[cache_key]
                if (datetime.now() - cache_time).hours < 12:  # Cache for 12 hours
                    return correlation
            
            # Get data for both pairs
            yf_symbols = {
                'EUR/USD': 'EURUSD=X', 'GBP/USD': 'GBPUSD=X', 'USD/JPY': 'USDJPY=X',
                'USD/CHF': 'USDCHF=X', 'AUD/USD': 'AUDUSD=X', 'USD/CAD': 'USDCAD=X',
                'NZD/USD': 'NZDUSD=X'
            }
            
            symbol1 = yf_symbols.get(pair1)
            symbol2 = yf_symbols.get(pair2)
            
            if not symbol1 or not symbol2:
                return 0.0  # Default no correlation
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get data
            data1 = yf.Ticker(symbol1).history(start=start_date, end=end_date)['Close']
            data2 = yf.Ticker(symbol2).history(start=start_date, end=end_date)['Close']
            
            if len(data1) < 20 or len(data2) < 20:
                return 0.0
            
            # Calculate returns
            returns1 = data1.pct_change().dropna()
            returns2 = data2.pct_change().dropna()
            
            # Align data
            aligned_data = pd.concat([returns1, returns2], axis=1, join='inner')
            if len(aligned_data) < 20:
                return 0.0
            
            # Calculate correlation
            correlation = aligned_data.iloc[:, 0].corr(aligned_data.iloc[:, 1])
            
            # Cache result
            self.correlation_cache[cache_key] = (datetime.now(), correlation)
            
            return correlation if not np.isnan(correlation) else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating correlation between {pair1} and {pair2}: {e}")
            return 0.0
    
    def calculate_portfolio_heat(self, current_positions: List[Dict]) -> float:
        """
        Calculate total portfolio risk exposure
        Returns factor to reduce new position size if portfolio heat is high
        """
        try:
            total_risk = 0.0
            
            for position in current_positions:
                position_risk = position.get('risk_amount', 0)
                total_risk += position_risk
            
            # Calculate risk as percentage of account
            risk_percentage = total_risk / self.account_balance
            
            # If approaching max portfolio risk, reduce new position sizes
            if risk_percentage > self.max_portfolio_risk * 0.8:  # 80% of max
                heat_factor = (self.max_portfolio_risk - risk_percentage) / (self.max_portfolio_risk * 0.2)
                heat_factor = max(0.2, heat_factor)  # Minimum 20% size
                
                logger.info(f"📊 Portfolio heat adjustment: {heat_factor:.2f}x (risk: {risk_percentage:.1%})")
                return heat_factor
            
            return 1.0
            
        except Exception as e:
            logger.error(f"Error calculating portfolio heat: {e}")
            return 1.0
    
    def time_based_adjustment(self, signal_time: datetime = None) -> float:
        """
        Adjust position size based on time of day and market session
        """
        try:
            if not signal_time:
                signal_time = datetime.now()
            
            hour = signal_time.hour
            
            # Market session adjustments (UTC time)
            if 8 <= hour <= 16:  # London session
                return 1.1  # Increase size by 10% (high liquidity)
            elif 13 <= hour <= 21:  # New York session
                return 1.1  # Increase size by 10% (high liquidity)
            elif 0 <= hour <= 8:  # Tokyo session
                return 0.9  # Reduce size by 10% (lower liquidity for majors)
            else:  # Off-hours
                return 0.8  # Reduce size by 20% (low liquidity)
                
        except Exception as e:
            logger.error(f"Error in time-based adjustment: {e}")
            return 1.0
    
    def calculate_optimal_position_size(self, signal, current_positions: List[Dict] = None, 
                                      historical_performance: Dict = None) -> Dict:
        """
        Calculate optimal position size using all optimization techniques
        """
        try:
            if current_positions is None:
                current_positions = []
            
            logger.info(f"🎯 Calculating optimal position size for {signal.pair}")
            
            # 1. Kelly Criterion base size
            kelly_size = self.calculate_kelly_optimal_size(signal, historical_performance)
            
            # 2. Volatility adjustment
            vol_adjusted_size = self.volatility_adjusted_size(kelly_size, signal.pair)
            
            # 3. Correlation adjustment
            correlation_factor = self.check_correlation_impact(signal.pair, current_positions)
            
            # 4. Portfolio heat adjustment
            heat_factor = self.calculate_portfolio_heat(current_positions)
            
            # 5. Time-based adjustment
            time_factor = self.time_based_adjustment(signal.timestamp)
            
            # Calculate final size
            final_size_pct = vol_adjusted_size * correlation_factor * heat_factor * time_factor
            
            # Apply absolute limits
            final_size_pct = max(0.01, min(final_size_pct, self.max_position_risk))
            
            # Calculate position size in units
            risk_amount = self.account_balance * final_size_pct
            
            # Calculate stop distance in pips
            if 'JPY' in signal.pair:
                pip_value = 0.01
            else:
                pip_value = 0.0001
            
            stop_distance_pips = abs(signal.entry_price - signal.stop_loss) / pip_value
            
            # Calculate units
            if stop_distance_pips > 0:
                pip_value_usd = 0.10  # $0.10 per pip for 1000 units
                units = int(risk_amount / (stop_distance_pips * pip_value_usd))
                units = max(1000, min(units, 100000))  # Min 1k, max 100k units
            else:
                units = 1000
            
            result = {
                'units': units,
                'risk_amount': risk_amount,
                'risk_percentage': final_size_pct,
                'kelly_base': kelly_size,
                'volatility_factor': vol_adjusted_size / kelly_size if kelly_size > 0 else 1.0,
                'correlation_factor': correlation_factor,
                'heat_factor': heat_factor,
                'time_factor': time_factor,
                'final_factor': final_size_pct / kelly_size if kelly_size > 0 else 1.0
            }
            
            logger.info(f"🎯 Optimal position: {units:,} units (${risk_amount:.2f} risk, {final_size_pct:.1%})")
            logger.info(f"📊 Factors: Vol={result['volatility_factor']:.2f}, Corr={correlation_factor:.2f}, Heat={heat_factor:.2f}, Time={time_factor:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating optimal position size: {e}")
            return {
                'units': 1000,
                'risk_amount': self.account_balance * 0.03,
                'risk_percentage': 0.03,
                'kelly_base': 0.03,
                'volatility_factor': 1.0,
                'correlation_factor': 1.0,
                'heat_factor': 1.0,
                'time_factor': 1.0,
                'final_factor': 1.0
            }
    
    def update_performance_history(self, trade_result: Dict):
        """Update historical performance for future Kelly calculations."""
        try:
            self.trade_history.append(trade_result)
            
            # Update pair-specific performance
            pair = trade_result.get('pair')
            if pair:
                if pair not in self.pair_performance:
                    self.pair_performance[pair] = {
                        'trades': [],
                        'win_rate': 0.6,
                        'avg_win': 25,
                        'avg_loss': 15
                    }
                
                self.pair_performance[pair]['trades'].append(trade_result)
                
                # Recalculate performance metrics
                recent_trades = self.pair_performance[pair]['trades'][-50:]  # Last 50 trades
                
                wins = [t for t in recent_trades if t.get('outcome') == 'WIN']
                losses = [t for t in recent_trades if t.get('outcome') == 'LOSS']
                
                if len(recent_trades) > 10:
                    self.pair_performance[pair]['win_rate'] = len(wins) / len(recent_trades)
                    
                    if wins:
                        self.pair_performance[pair]['avg_win'] = np.mean([t.get('pips_gained', 25) for t in wins])
                    
                    if losses:
                        self.pair_performance[pair]['avg_loss'] = abs(np.mean([t.get('pips_gained', -15) for t in losses]))
                
                logger.info(f"📊 Updated {pair} performance: {self.pair_performance[pair]['win_rate']:.1%} win rate")
            
        except Exception as e:
            logger.error(f"Error updating performance history: {e}")

# Test the advanced position sizer
if __name__ == "__main__":
    from forex_signal_generator import ForexSignal
    from datetime import datetime
    
    # Initialize sizer
    sizer = AdvancedPositionSizer(account_balance=10000)
    
    # Create test signal
    test_signal = ForexSignal(
        pair="EUR/USD",
        signal_type="BUY",
        entry_price=1.0800,
        target_price=1.0850,
        stop_loss=1.0750,
        confidence=0.75,
        pips_target=50,
        pips_risk=50,
        risk_reward_ratio="1:1",
        reason="Test signal",
        timestamp=datetime.now(),
        news_sentiment=0.7,
        technical_score=0.8
    )
    
    # Calculate optimal position size
    result = sizer.calculate_optimal_position_size(test_signal)
    
    print("🎯 ADVANCED POSITION SIZING RESULTS:")
    print("=" * 50)
    print(f"Optimal Units: {result['units']:,}")
    print(f"Risk Amount: ${result['risk_amount']:.2f}")
    print(f"Risk Percentage: {result['risk_percentage']:.1%}")
    print(f"Kelly Base: {result['kelly_base']:.1%}")
    print(f"Final Multiplier: {result['final_factor']:.2f}x") 