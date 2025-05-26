#!/usr/bin/env python3
"""
🎯 Dynamic Exit Manager - Maximize Profits with Smart Exits
Advanced exit strategies: trailing stops, partial profits, volatility-based exits
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np

logger = logging.getLogger(__name__)

class DynamicExitManager:
    """
    Professional exit management to maximize profits and minimize losses
    """
    
    def __init__(self):
        # Exit strategy parameters
        self.trailing_stop_activation = 0.5  # Start trailing after 50% to target
        self.trailing_stop_distance = 0.3    # Trail 30% of original stop distance
        self.partial_profit_levels = [0.5, 0.75]  # Take partial profits at 50% and 75%
        self.partial_profit_amounts = [0.3, 0.3]  # Take 30% each time
        
        # Volatility-based adjustments
        self.high_volatility_threshold = 0.12  # 12% annual volatility
        self.low_volatility_threshold = 0.06   # 6% annual volatility
        
        logger.info("🎯 Dynamic Exit Manager initialized")
    
    def calculate_trailing_stop(self, signal, current_price: float, highest_favorable: float) -> Dict:
        """
        Calculate trailing stop loss based on current market conditions
        """
        try:
            entry_price = signal.entry_price
            original_stop = signal.stop_loss
            target_price = signal.target_price
            
            # Calculate progress toward target
            if signal.signal_type == "BUY":
                total_distance = target_price - entry_price
                current_progress = current_price - entry_price
                favorable_progress = highest_favorable - entry_price
            else:  # SELL
                total_distance = entry_price - target_price
                current_progress = entry_price - current_price
                favorable_progress = entry_price - highest_favorable
            
            progress_ratio = favorable_progress / total_distance if total_distance > 0 else 0
            
            # Only activate trailing stop after significant progress
            if progress_ratio < self.trailing_stop_activation:
                return {
                    'use_trailing': False,
                    'new_stop': original_stop,
                    'reason': f'Progress {progress_ratio:.1%} < {self.trailing_stop_activation:.1%} activation threshold'
                }
            
            # Calculate trailing distance
            original_stop_distance = abs(entry_price - original_stop)
            trailing_distance = original_stop_distance * self.trailing_stop_distance
            
            # Calculate new trailing stop
            if signal.signal_type == "BUY":
                new_trailing_stop = highest_favorable - trailing_distance
                # Ensure trailing stop is better than original
                new_stop = max(new_trailing_stop, original_stop)
            else:  # SELL
                new_trailing_stop = highest_favorable + trailing_distance
                # Ensure trailing stop is better than original
                new_stop = min(new_trailing_stop, original_stop)
            
            # Calculate pip values for display
            if 'JPY' in signal.pair:
                pip_value = 0.01
            else:
                pip_value = 0.0001
            
            stop_improvement_pips = abs(new_stop - original_stop) / pip_value
            
            return {
                'use_trailing': True,
                'new_stop': new_stop,
                'original_stop': original_stop,
                'improvement_pips': stop_improvement_pips,
                'progress_ratio': progress_ratio,
                'reason': f'Trailing activated: {progress_ratio:.1%} progress, improved by {stop_improvement_pips:.1f} pips'
            }
            
        except Exception as e:
            logger.error(f"Error calculating trailing stop: {e}")
            return {
                'use_trailing': False,
                'new_stop': signal.stop_loss,
                'reason': 'Error in trailing stop calculation'
            }
    
    def calculate_partial_profit_levels(self, signal, current_price: float) -> List[Dict]:
        """
        Calculate partial profit taking opportunities
        """
        try:
            entry_price = signal.entry_price
            target_price = signal.target_price
            
            # Calculate total distance to target
            if signal.signal_type == "BUY":
                total_distance = target_price - entry_price
                current_progress = current_price - entry_price
            else:  # SELL
                total_distance = entry_price - target_price
                current_progress = entry_price - current_price
            
            progress_ratio = current_progress / total_distance if total_distance > 0 else 0
            
            partial_opportunities = []
            
            for i, level in enumerate(self.partial_profit_levels):
                if progress_ratio >= level:
                    # Calculate partial profit price
                    if signal.signal_type == "BUY":
                        partial_price = entry_price + (total_distance * level)
                    else:  # SELL
                        partial_price = entry_price - (total_distance * level)
                    
                    # Calculate profit amount
                    profit_amount = self.partial_profit_amounts[i]
                    
                    # Calculate pip profit
                    if 'JPY' in signal.pair:
                        pip_value = 0.01
                    else:
                        pip_value = 0.0001
                    
                    pip_profit = abs(partial_price - entry_price) / pip_value
                    
                    partial_opportunities.append({
                        'level': level,
                        'price': partial_price,
                        'amount': profit_amount,
                        'pip_profit': pip_profit,
                        'triggered': progress_ratio >= level,
                        'description': f'Take {profit_amount:.0%} profit at {level:.0%} target ({pip_profit:.1f} pips)'
                    })
            
            return partial_opportunities
            
        except Exception as e:
            logger.error(f"Error calculating partial profits: {e}")
            return []
    
    def analyze_volatility_exit(self, signal, current_price: float, pair_volatility: float = None) -> Dict:
        """
        Analyze if volatility conditions suggest early exit or hold
        """
        try:
            if pair_volatility is None:
                # Default volatility estimates
                volatility_estimates = {
                    'EUR/USD': 0.08, 'GBP/USD': 0.12, 'USD/JPY': 0.09,
                    'USD/CHF': 0.10, 'AUD/USD': 0.11, 'USD/CAD': 0.09,
                    'NZD/USD': 0.13
                }
                pair_volatility = volatility_estimates.get(signal.pair, 0.10)
            
            entry_price = signal.entry_price
            target_price = signal.target_price
            
            # Calculate current profit
            if signal.signal_type == "BUY":
                current_profit = current_price - entry_price
                total_target_profit = target_price - entry_price
            else:  # SELL
                current_profit = entry_price - current_price
                total_target_profit = entry_price - target_price
            
            profit_ratio = current_profit / total_target_profit if total_target_profit > 0 else 0
            
            # Volatility-based exit logic
            if pair_volatility > self.high_volatility_threshold:
                # High volatility - consider early exit to lock in profits
                if profit_ratio >= 0.6:  # 60% of target reached
                    recommendation = 'TAKE_PROFIT_EARLY'
                    reason = f'High volatility ({pair_volatility:.1%}) - secure {profit_ratio:.1%} profit'
                    multiplier = 0.8  # Reduce target by 20%
                else:
                    recommendation = 'HOLD'
                    reason = f'High volatility but insufficient profit ({profit_ratio:.1%})'
                    multiplier = 1.0
                    
            elif pair_volatility < self.low_volatility_threshold:
                # Low volatility - extend targets for more profit
                if profit_ratio >= 0.8:  # 80% of target reached
                    recommendation = 'EXTEND_TARGET'
                    reason = f'Low volatility ({pair_volatility:.1%}) - extend target for more profit'
                    multiplier = 1.3  # Extend target by 30%
                else:
                    recommendation = 'HOLD'
                    reason = f'Low volatility - normal target appropriate'
                    multiplier = 1.0
            else:
                # Normal volatility - standard exit strategy
                recommendation = 'NORMAL'
                reason = f'Normal volatility ({pair_volatility:.1%}) - standard exit'
                multiplier = 1.0
            
            return {
                'recommendation': recommendation,
                'reason': reason,
                'volatility': pair_volatility,
                'profit_ratio': profit_ratio,
                'target_multiplier': multiplier,
                'current_profit_pips': abs(current_profit) / (0.01 if 'JPY' in signal.pair else 0.0001)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing volatility exit: {e}")
            return {
                'recommendation': 'NORMAL',
                'reason': 'Error in volatility analysis',
                'volatility': 0.10,
                'profit_ratio': 0.0,
                'target_multiplier': 1.0,
                'current_profit_pips': 0.0
            }
    
    def calculate_time_based_exit(self, signal, current_time: datetime = None) -> Dict:
        """
        Calculate time-based exit adjustments
        """
        try:
            if current_time is None:
                current_time = datetime.now()
            
            entry_time = signal.timestamp
            time_elapsed = (current_time - entry_time).total_seconds() / 3600  # Hours
            
            # Time-based exit thresholds
            if time_elapsed > 48:  # 2 days
                recommendation = 'CLOSE_POSITION'
                reason = f'Position held too long ({time_elapsed:.1f} hours) - close to avoid weekend risk'
                urgency = 'HIGH'
            elif time_elapsed > 24:  # 1 day
                recommendation = 'REDUCE_TARGET'
                reason = f'Long hold time ({time_elapsed:.1f} hours) - reduce target for quicker exit'
                urgency = 'MEDIUM'
            elif time_elapsed > 12:  # 12 hours
                recommendation = 'MONITOR_CLOSELY'
                reason = f'Moderate hold time ({time_elapsed:.1f} hours) - monitor for exit opportunities'
                urgency = 'LOW'
            else:
                recommendation = 'NORMAL'
                reason = f'Fresh position ({time_elapsed:.1f} hours) - normal exit strategy'
                urgency = 'NONE'
            
            # Check for Friday close (avoid weekend gaps)
            if current_time.weekday() == 4 and current_time.hour >= 20:  # Friday after 8 PM UTC
                recommendation = 'CLOSE_BEFORE_WEEKEND'
                reason = 'Friday evening - close to avoid weekend gap risk'
                urgency = 'HIGH'
            
            return {
                'recommendation': recommendation,
                'reason': reason,
                'urgency': urgency,
                'time_elapsed_hours': time_elapsed,
                'is_friday_close': current_time.weekday() == 4 and current_time.hour >= 20
            }
            
        except Exception as e:
            logger.error(f"Error calculating time-based exit: {e}")
            return {
                'recommendation': 'NORMAL',
                'reason': 'Error in time analysis',
                'urgency': 'NONE',
                'time_elapsed_hours': 0,
                'is_friday_close': False
            }
    
    def generate_exit_strategy(self, signal, current_price: float, highest_favorable: float,
                             pair_volatility: float = None, current_time: datetime = None) -> Dict:
        """
        Generate comprehensive exit strategy combining all factors
        """
        try:
            logger.info(f"🎯 Generating exit strategy for {signal.pair} {signal.signal_type}")
            
            # Calculate all exit components
            trailing_stop = self.calculate_trailing_stop(signal, current_price, highest_favorable)
            partial_profits = self.calculate_partial_profit_levels(signal, current_price)
            volatility_exit = self.analyze_volatility_exit(signal, current_price, pair_volatility)
            time_exit = self.calculate_time_based_exit(signal, current_time)
            
            # Determine primary recommendation
            recommendations = []
            
            # High priority: Time-based urgent exits
            if time_exit['urgency'] == 'HIGH':
                recommendations.append({
                    'action': time_exit['recommendation'],
                    'priority': 'HIGH',
                    'reason': time_exit['reason']
                })
            
            # Medium priority: Volatility-based exits
            if volatility_exit['recommendation'] in ['TAKE_PROFIT_EARLY', 'CLOSE_POSITION']:
                recommendations.append({
                    'action': volatility_exit['recommendation'],
                    'priority': 'MEDIUM',
                    'reason': volatility_exit['reason']
                })
            
            # Standard priority: Partial profits and trailing stops
            triggered_partials = [p for p in partial_profits if p['triggered']]
            if triggered_partials:
                recommendations.append({
                    'action': 'TAKE_PARTIAL_PROFIT',
                    'priority': 'MEDIUM',
                    'reason': f"Take partial profits: {len(triggered_partials)} levels triggered"
                })
            
            if trailing_stop['use_trailing']:
                recommendations.append({
                    'action': 'UPDATE_TRAILING_STOP',
                    'priority': 'LOW',
                    'reason': trailing_stop['reason']
                })
            
            # Select primary action
            if recommendations:
                primary_action = max(recommendations, key=lambda x: {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}[x['priority']])
            else:
                primary_action = {
                    'action': 'HOLD',
                    'priority': 'LOW',
                    'reason': 'No exit conditions met - continue holding'
                }
            
            # Calculate updated targets and stops
            new_stop_loss = trailing_stop['new_stop'] if trailing_stop['use_trailing'] else signal.stop_loss
            
            # Adjust target based on volatility
            if volatility_exit['recommendation'] == 'EXTEND_TARGET':
                target_adjustment = volatility_exit['target_multiplier']
                if signal.signal_type == "BUY":
                    new_target = signal.entry_price + ((signal.target_price - signal.entry_price) * target_adjustment)
                else:
                    new_target = signal.entry_price - ((signal.entry_price - signal.target_price) * target_adjustment)
            else:
                new_target = signal.target_price
                target_adjustment = 1.0
            
            result = {
                'primary_action': primary_action,
                'all_recommendations': recommendations,
                'new_stop_loss': new_stop_loss,
                'new_target': new_target,
                'target_adjustment': target_adjustment,
                'trailing_stop_info': trailing_stop,
                'partial_profit_opportunities': partial_profits,
                'volatility_analysis': volatility_exit,
                'time_analysis': time_exit,
                'should_close_position': primary_action['action'] in ['CLOSE_POSITION', 'CLOSE_BEFORE_WEEKEND'],
                'should_update_stops': trailing_stop['use_trailing'] or primary_action['action'] == 'UPDATE_TRAILING_STOP'
            }
            
            logger.info(f"🎯 Exit strategy: {primary_action['action']} - {primary_action['reason']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating exit strategy: {e}")
            return {
                'primary_action': {'action': 'HOLD', 'priority': 'LOW', 'reason': 'Error in exit analysis'},
                'all_recommendations': [],
                'new_stop_loss': signal.stop_loss,
                'new_target': signal.target_price,
                'should_close_position': False,
                'should_update_stops': False
            }

# Test the dynamic exit manager
if __name__ == "__main__":
    from forex_signal_generator import ForexSignal
    from datetime import datetime
    
    # Initialize exit manager
    exit_manager = DynamicExitManager()
    
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
        timestamp=datetime.now() - timedelta(hours=6),  # 6 hours ago
        news_sentiment=0.6,
        technical_score=0.7
    )
    
    # Test scenarios
    test_scenarios = [
        {'current_price': 1.0825, 'highest_favorable': 1.0830, 'description': '50% to target'},
        {'current_price': 1.0840, 'highest_favorable': 1.0845, 'description': '80% to target'},
        {'current_price': 1.0820, 'highest_favorable': 1.0835, 'description': 'Pullback from high'},
    ]
    
    print("🎯 DYNAMIC EXIT MANAGER TEST:")
    print("=" * 60)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📊 Scenario {i}: {scenario['description']}")
        print("-" * 40)
        
        strategy = exit_manager.generate_exit_strategy(
            test_signal,
            scenario['current_price'],
            scenario['highest_favorable'],
            pair_volatility=0.08
        )
        
        print(f"Primary Action: {strategy['primary_action']['action']}")
        print(f"Reason: {strategy['primary_action']['reason']}")
        print(f"New Stop: {strategy['new_stop_loss']:.5f}")
        print(f"New Target: {strategy['new_target']:.5f}")
        print(f"Should Close: {strategy['should_close_position']}")
        print(f"Update Stops: {strategy['should_update_stops']}")
        
        if strategy['partial_profit_opportunities']:
            triggered = [p for p in strategy['partial_profit_opportunities'] if p['triggered']]
            if triggered:
                print(f"Partial Profits: {len(triggered)} levels triggered") 