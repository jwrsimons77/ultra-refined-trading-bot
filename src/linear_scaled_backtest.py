#!/usr/bin/env python3
"""
🎯 Linear Scaled Trading System Backtest
Ensures perfect linear scaling: 10x capital = 10x profits
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from optimized_advanced_backtest import OptimizedAdvancedBacktest
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LinearScaledBacktest(OptimizedAdvancedBacktest):
    """
    Linear scaling backtest that ensures perfect proportional results
    """
    
    def __init__(self, initial_balance: float = 1000):
        super().__init__(initial_balance)
        self.base_balance = 1000  # Reference balance for linear scaling
        self.scale_factor = initial_balance / self.base_balance
        self.original_balance = initial_balance  # Store original balance
        
        logger.info(f"🎯 Linear Scaled Backtest initialized with {self.scale_factor:.1f}x scaling")
    
    def calculate_optimized_position_size(self, signal: dict, quality_score: float) -> dict:
        """Calculate position size with perfect linear scaling."""
        try:
            # ALWAYS use original balance for consistent scaling
            # This prevents compound effects from affecting scaling
            base_risk = self.base_balance * self.base_risk_pct  # Always use $1,000 base
            
            # Quality multiplier (consistent across all account sizes)
            if quality_score > 0.7:
                quality_multiplier = 1.4
            elif quality_score > 0.6:
                quality_multiplier = 1.2
            elif quality_score > 0.5:
                quality_multiplier = 1.0
            else:
                quality_multiplier = 0.8
            
            # Session multiplier (consistent)
            if signal['session_name'] == "London-NY Overlap":
                session_multiplier = 1.3
            elif signal['session_name'] in ["London Session", "NY Session"]:
                session_multiplier = 1.15
            elif signal['session_name'] == "Asian Session":
                session_multiplier = 1.0
            else:
                session_multiplier = 0.85
            
            # Technical strength multiplier (consistent)
            if signal['technical_strength'] == 'strong':
                strength_multiplier = 1.2
            elif signal['technical_strength'] == 'moderate':
                strength_multiplier = 1.1
            else:
                strength_multiplier = 1.0
            
            # Calculate base risk for $1,000 account
            base_final_risk = base_risk * quality_multiplier * session_multiplier * strength_multiplier
            base_final_risk = max(15, min(base_final_risk, self.base_balance * 0.1))
            
            # Scale linearly by account size (using ORIGINAL balance, not current)
            final_risk = base_final_risk * self.scale_factor
            final_risk = max(15 * self.scale_factor, min(final_risk, self.original_balance * 0.1))
            
            # Calculate units (scales linearly)
            stop_distance_pips = signal['pips_risk']
            pip_value_usd = 0.10  # $0.10 per pip for 1000 units
            
            base_units = int(base_final_risk / (stop_distance_pips * pip_value_usd))
            base_units = max(1000, min(base_units, 150000))
            
            # Scale units linearly
            units = int(base_units * self.scale_factor)
            units = max(1000, min(units, 150000 * int(self.scale_factor)))
            
            return {
                'units': units,
                'risk_amount': final_risk,
                'base_units': base_units,
                'scale_factor': self.scale_factor,
                'quality_multiplier': quality_multiplier,
                'session_multiplier': session_multiplier,
                'strength_multiplier': strength_multiplier,
                'compound_multiplier': 1.0,  # Always 1.0 for linear scaling
                'total_multiplier': quality_multiplier * session_multiplier * strength_multiplier
            }
            
        except Exception as e:
            logger.error(f"Error calculating linear position size: {e}")
            return {
                'units': int(1000 * self.scale_factor),
                'risk_amount': 25.0 * self.scale_factor,
                'scale_factor': self.scale_factor
            }

def run_linear_scaled_backtest(initial_balance: float = 10000):
    """Run the linear scaled backtest."""
    try:
        # Initialize with specified balance
        backtest = LinearScaledBacktest(initial_balance=initial_balance)
        
        pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD']
        start_date = datetime(2024, 12, 1)
        end_date = datetime(2024, 12, 15)
        
        results = backtest.run_optimized_backtest(pairs, start_date, end_date)
        
        # Add scaling information
        results['scale_factor'] = backtest.scale_factor
        results['base_balance'] = backtest.base_balance
        
        return results
        
    except Exception as e:
        print(f"Error in linear scaled backtest: {e}")
        return {'error': str(e)}

if __name__ == "__main__":
    print("🎯 LINEAR SCALED TRADING SYSTEM BACKTEST")
    print("💰 Perfect Linear Scaling Test")
    print("=" * 60)
    
    # Test with $1,000
    print("\n📊 Testing $1,000 account...")
    results_1k = run_linear_scaled_backtest(1000)
    
    # Test with $10,000
    print("\n📊 Testing $10,000 account...")
    results_10k = run_linear_scaled_backtest(10000)
    
    if 'error' not in results_1k and 'error' not in results_10k:
        print(f"\n🔍 LINEAR SCALING VERIFICATION:")
        print(f"   $1,000 Profit: ${results_1k['total_profit']:,.2f}")
        print(f"   $10,000 Profit: ${results_10k['total_profit']:,.2f}")
        print(f"   Expected 10x: ${results_1k['total_profit'] * 10:,.2f}")
        print(f"   Actual Ratio: {results_10k['total_profit'] / results_1k['total_profit']:.2f}x")
        
        if abs(results_10k['total_profit'] / results_1k['total_profit'] - 10.0) < 0.1:
            print(f"   ✅ PERFECT LINEAR SCALING ACHIEVED!")
        else:
            print(f"   ⚠️  Scaling deviation detected")
            
        # Show detailed comparison
        print(f"\n📊 DETAILED COMPARISON:")
        print(f"   Trade Count: {results_1k['total_trades']} vs {results_10k['total_trades']}")
        print(f"   Win Rate: {results_1k['win_rate']:.1%} vs {results_10k['win_rate']:.1%}")
        print(f"   Avg Win: ${results_1k['avg_win']:.2f} vs ${results_10k['avg_win']:.2f}")
        print(f"   Avg Loss: ${results_1k['avg_loss']:.2f} vs ${results_10k['avg_loss']:.2f}")
        
    else:
        print(f"❌ Error in one or both tests")
        if 'error' in results_1k:
            print(f"   $1,000 Error: {results_1k['error']}")
        if 'error' in results_10k:
            print(f"   $10,000 Error: {results_10k['error']}") 