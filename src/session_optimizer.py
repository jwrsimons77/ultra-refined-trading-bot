#!/usr/bin/env python3
"""
🎯 Session Optimizer - Trade Only During Peak Profit Hours
Maximizes profit by identifying optimal trading sessions and market conditions
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pytz
import numpy as np

logger = logging.getLogger(__name__)

class SessionOptimizer:
    """
    Optimize trading based on market sessions, volatility patterns, and historical performance
    """
    
    def __init__(self):
        # Market sessions (UTC times)
        self.sessions = {
            'tokyo': {'start': 0, 'end': 9, 'name': 'Tokyo', 'liquidity': 0.6},
            'london': {'start': 8, 'end': 17, 'name': 'London', 'liquidity': 0.9},
            'new_york': {'start': 13, 'end': 22, 'name': 'New York', 'liquidity': 0.9},
            'london_ny_overlap': {'start': 13, 'end': 17, 'name': 'London-NY Overlap', 'liquidity': 1.0}
        }
        
        # Historical performance by hour (UTC) - based on forex market data
        self.hourly_performance = {
            0: 0.4,   1: 0.3,   2: 0.3,   3: 0.4,   4: 0.5,   5: 0.6,
            6: 0.7,   7: 0.8,   8: 0.9,   9: 0.8,   10: 0.8,  11: 0.8,
            12: 0.9,  13: 1.0,  14: 1.0,  15: 1.0,  16: 0.9,  17: 0.8,
            18: 0.8,  19: 0.7,  20: 0.7,  21: 0.6,  22: 0.5,  23: 0.4
        }
        
        # Day of week performance (0=Monday, 6=Sunday)
        self.daily_performance = {
            0: 0.9,   # Monday - Good
            1: 1.0,   # Tuesday - Best
            2: 1.0,   # Wednesday - Best  
            3: 0.8,   # Thursday - Good
            4: 0.6,   # Friday - Avoid late trades
            5: 0.3,   # Saturday - Closed
            6: 0.3    # Sunday - Closed/Low volume
        }
        
        # News impact times (hours to avoid after major news)
        self.news_blackout_hours = 2  # Avoid trading 2 hours after major news
        
        logger.info("🎯 Session Optimizer initialized")
    
    def get_current_session(self, timestamp: datetime = None) -> Dict:
        """Identify current market session and characteristics."""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        hour = timestamp.hour
        weekday = timestamp.weekday()
        
        # Check if market is closed (weekend)
        if weekday >= 5:  # Saturday/Sunday
            return {
                'session': 'closed',
                'name': 'Market Closed',
                'liquidity': 0.0,
                'performance_factor': 0.3,
                'recommendation': 'AVOID'
            }
        
        # Determine active session
        active_sessions = []
        
        for session_key, session_data in self.sessions.items():
            if session_data['start'] <= hour <= session_data['end']:
                active_sessions.append((session_key, session_data))
        
        if not active_sessions:
            return {
                'session': 'off_hours',
                'name': 'Off Hours',
                'liquidity': 0.2,
                'performance_factor': 0.4,
                'recommendation': 'AVOID'
            }
        
        # If multiple sessions active, pick the highest liquidity
        best_session = max(active_sessions, key=lambda x: x[1]['liquidity'])
        session_key, session_data = best_session
        
        # Get performance factors
        hourly_factor = self.hourly_performance.get(hour, 0.5)
        daily_factor = self.daily_performance.get(weekday, 0.5)
        
        # Combined performance factor
        performance_factor = (session_data['liquidity'] + hourly_factor + daily_factor) / 3
        
        # Generate recommendation
        if performance_factor >= 0.8:
            recommendation = 'EXCELLENT'
        elif performance_factor >= 0.7:
            recommendation = 'GOOD'
        elif performance_factor >= 0.6:
            recommendation = 'FAIR'
        else:
            recommendation = 'AVOID'
        
        return {
            'session': session_key,
            'name': session_data['name'],
            'liquidity': session_data['liquidity'],
            'hourly_factor': hourly_factor,
            'daily_factor': daily_factor,
            'performance_factor': performance_factor,
            'recommendation': recommendation,
            'hour': hour,
            'weekday': weekday
        }
    
    def calculate_session_multiplier(self, timestamp: datetime = None) -> float:
        """Calculate position size multiplier based on session quality."""
        session_info = self.get_current_session(timestamp)
        
        performance = session_info['performance_factor']
        
        # Convert performance to position size multiplier
        if performance >= 0.9:
            return 1.3  # Increase position by 30%
        elif performance >= 0.8:
            return 1.2  # Increase position by 20%
        elif performance >= 0.7:
            return 1.1  # Increase position by 10%
        elif performance >= 0.6:
            return 1.0  # Normal position size
        elif performance >= 0.5:
            return 0.8  # Reduce position by 20%
        else:
            return 0.5  # Reduce position by 50%
    
    def should_trade_now(self, timestamp: datetime = None, min_performance: float = 0.6) -> Dict:
        """Determine if current time is suitable for trading."""
        session_info = self.get_current_session(timestamp)
        
        should_trade = session_info['performance_factor'] >= min_performance
        
        return {
            'should_trade': should_trade,
            'session_info': session_info,
            'reason': f"{session_info['name']} - {session_info['recommendation']} (Performance: {session_info['performance_factor']:.1%})"
        }
    
    def get_next_optimal_session(self, timestamp: datetime = None) -> Dict:
        """Find the next optimal trading session."""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        # Look ahead 48 hours to find next good session
        for hours_ahead in range(1, 49):
            future_time = timestamp + timedelta(hours=hours_ahead)
            session_check = self.should_trade_now(future_time, min_performance=0.7)
            
            if session_check['should_trade']:
                return {
                    'next_session_time': future_time,
                    'hours_until': hours_ahead,
                    'session_info': session_check['session_info']
                }
        
        return {
            'next_session_time': None,
            'hours_until': None,
            'session_info': None
        }
    
    def analyze_pair_session_performance(self, pair: str, timestamp: datetime = None) -> Dict:
        """Analyze how specific currency pairs perform in different sessions."""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        # Pair-specific session preferences
        pair_preferences = {
            'EUR/USD': {
                'best_sessions': ['london', 'london_ny_overlap', 'new_york'],
                'multiplier': 1.0
            },
            'GBP/USD': {
                'best_sessions': ['london', 'london_ny_overlap'],
                'multiplier': 1.1  # Performs better during London
            },
            'USD/JPY': {
                'best_sessions': ['tokyo', 'london_ny_overlap'],
                'multiplier': 1.0
            },
            'USD/CHF': {
                'best_sessions': ['london', 'new_york'],
                'multiplier': 0.9  # Less volatile
            },
            'AUD/USD': {
                'best_sessions': ['tokyo', 'london_ny_overlap'],
                'multiplier': 1.0
            },
            'USD/CAD': {
                'best_sessions': ['new_york', 'london_ny_overlap'],
                'multiplier': 1.0
            },
            'NZD/USD': {
                'best_sessions': ['tokyo', 'london_ny_overlap'],
                'multiplier': 0.9  # Lower liquidity
            }
        }
        
        current_session = self.get_current_session(timestamp)
        pair_data = pair_preferences.get(pair, {'best_sessions': ['london_ny_overlap'], 'multiplier': 1.0})
        
        # Check if current session is optimal for this pair
        is_optimal_session = current_session['session'] in pair_data['best_sessions']
        
        # Calculate pair-specific multiplier
        if is_optimal_session:
            pair_multiplier = pair_data['multiplier'] * 1.2  # 20% bonus for optimal session
        else:
            pair_multiplier = pair_data['multiplier'] * 0.8  # 20% penalty for non-optimal
        
        return {
            'pair': pair,
            'current_session': current_session['name'],
            'is_optimal_session': is_optimal_session,
            'pair_multiplier': pair_multiplier,
            'best_sessions': pair_data['best_sessions'],
            'recommendation': 'TRADE' if is_optimal_session and current_session['performance_factor'] > 0.6 else 'WAIT'
        }
    
    def get_volatility_forecast(self, timestamp: datetime = None) -> Dict:
        """Forecast expected volatility based on upcoming sessions."""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        hour = timestamp.hour
        weekday = timestamp.weekday()
        
        # Volatility patterns by hour
        volatility_by_hour = {
            0: 0.3, 1: 0.2, 2: 0.2, 3: 0.3, 4: 0.4, 5: 0.5,
            6: 0.6, 7: 0.7, 8: 0.8, 9: 0.7, 10: 0.6, 11: 0.6,
            12: 0.7, 13: 0.9, 14: 1.0, 15: 1.0, 16: 0.8, 17: 0.7,
            18: 0.6, 19: 0.5, 20: 0.5, 21: 0.4, 22: 0.4, 23: 0.3
        }
        
        current_volatility = volatility_by_hour.get(hour, 0.5)
        
        # Look ahead 4 hours
        future_volatility = []
        for i in range(1, 5):
            future_hour = (hour + i) % 24
            future_vol = volatility_by_hour.get(future_hour, 0.5)
            future_volatility.append(future_vol)
        
        avg_future_volatility = np.mean(future_volatility)
        
        # Volatility trend
        if avg_future_volatility > current_volatility * 1.2:
            trend = 'INCREASING'
            recommendation = 'WAIT_FOR_VOLATILITY'
        elif avg_future_volatility < current_volatility * 0.8:
            trend = 'DECREASING'
            recommendation = 'TRADE_NOW'
        else:
            trend = 'STABLE'
            recommendation = 'NORMAL'
        
        return {
            'current_volatility': current_volatility,
            'future_volatility': avg_future_volatility,
            'trend': trend,
            'recommendation': recommendation,
            'optimal_for_scalping': 0.6 <= current_volatility <= 0.9
        }
    
    def generate_session_report(self, timestamp: datetime = None) -> str:
        """Generate comprehensive session analysis report."""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        session_info = self.get_current_session(timestamp)
        should_trade = self.should_trade_now(timestamp)
        next_session = self.get_next_optimal_session(timestamp)
        volatility = self.get_volatility_forecast(timestamp)
        
        report = f"""
🎯 SESSION ANALYSIS REPORT
{'='*50}
📅 Time: {timestamp.strftime('%Y-%m-%d %H:%M UTC')}
📊 Current Session: {session_info['name']}
📈 Performance Factor: {session_info['performance_factor']:.1%}
💡 Recommendation: {session_info['recommendation']}

🔍 TRADING DECISION:
Should Trade Now: {'✅ YES' if should_trade['should_trade'] else '❌ NO'}
Reason: {should_trade['reason']}

⏰ NEXT OPTIMAL SESSION:
"""
        
        if next_session['next_session_time']:
            report += f"Next Good Session: {next_session['session_info']['name']}\n"
            report += f"Time Until: {next_session['hours_until']} hours\n"
        else:
            report += "No optimal sessions found in next 48 hours\n"
        
        report += f"""
📊 VOLATILITY FORECAST:
Current: {volatility['current_volatility']:.1%}
Trend: {volatility['trend']}
Recommendation: {volatility['recommendation']}
Good for Scalping: {'✅ YES' if volatility['optimal_for_scalping'] else '❌ NO'}

💰 POSITION SIZE MULTIPLIER: {self.calculate_session_multiplier(timestamp):.1f}x
"""
        
        return report

# Test the session optimizer
if __name__ == "__main__":
    optimizer = SessionOptimizer()
    
    # Test current session
    print("🎯 SESSION OPTIMIZER TEST:")
    print("=" * 50)
    
    # Generate report
    report = optimizer.generate_session_report()
    print(report)
    
    # Test specific pairs
    print("\n📊 PAIR-SPECIFIC ANALYSIS:")
    print("-" * 30)
    
    test_pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY']
    for pair in test_pairs:
        analysis = optimizer.analyze_pair_session_performance(pair)
        print(f"{pair}: {analysis['recommendation']} (Multiplier: {analysis['pair_multiplier']:.1f}x)")
        print(f"  Current: {analysis['current_session']}, Optimal: {analysis['is_optimal_session']}")
    
    # Test position size multiplier
    multiplier = optimizer.calculate_session_multiplier()
    print(f"\n💰 Current Position Size Multiplier: {multiplier:.1f}x") 