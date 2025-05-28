#!/usr/bin/env python3
"""
🎯 Compound Profit Manager - Exponential Growth Through Reinvestment
Automatically scales position sizes as account grows for maximum compound returns
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import numpy as np
import json

logger = logging.getLogger(__name__)

class CompoundProfitManager:
    """
    Manage profit compounding and position size scaling for exponential growth
    """
    
    def __init__(self, initial_balance: float = 1000):
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.total_profit = 0.0
        self.total_trades = 0
        self.winning_trades = 0
        
        # Compounding parameters
        self.base_risk_percentage = 0.03  # 3% base risk
        self.max_risk_percentage = 0.08   # 8% maximum risk
        self.compound_frequency = 10      # Recalculate after every 10 trades
        self.profit_threshold = 0.20      # 20% profit before increasing risk
        
        # Performance tracking
        self.trade_history = []
        self.balance_history = []
        self.drawdown_history = []
        self.peak_balance = initial_balance
        
        # Risk scaling factors
        self.performance_multipliers = {
            'excellent': 1.5,  # >75% win rate
            'good': 1.2,       # 60-75% win rate
            'average': 1.0,    # 50-60% win rate
            'poor': 0.7        # <50% win rate
        }
        
        logger.info(f"🎯 Compound Profit Manager initialized with ${initial_balance:.2f}")
    
    def update_balance(self, trade_result: Dict):
        """Update account balance and performance metrics after each trade."""
        try:
            profit_loss = trade_result.get('profit_loss', 0)
            outcome = trade_result.get('outcome', 'UNKNOWN')
            
            # Update balance
            self.current_balance += profit_loss
            self.total_profit += profit_loss
            self.total_trades += 1
            
            if outcome == 'WIN':
                self.winning_trades += 1
            
            # Track peak balance for drawdown calculation
            if self.current_balance > self.peak_balance:
                self.peak_balance = self.current_balance
            
            # Calculate current drawdown
            current_drawdown = (self.peak_balance - self.current_balance) / self.peak_balance
            
            # Record history
            self.trade_history.append(trade_result)
            self.balance_history.append(self.current_balance)
            self.drawdown_history.append(current_drawdown)
            
            # Log significant milestones
            if len(self.balance_history) > 1:
                growth_rate = (self.current_balance / self.initial_balance - 1) * 100
                if growth_rate > 0 and int(growth_rate) % 25 == 0:  # Every 25% growth
                    logger.info(f"🎯 Milestone: {growth_rate:.0f}% account growth! Balance: ${self.current_balance:.2f}")
            
            logger.info(f"💰 Balance updated: ${self.current_balance:.2f} (P&L: ${profit_loss:.2f})")
            
        except Exception as e:
            logger.error(f"Error updating balance: {e}")
    
    def calculate_performance_metrics(self) -> Dict:
        """Calculate current performance metrics."""
        try:
            if self.total_trades == 0:
                return {
                    'win_rate': 0.0,
                    'total_return': 0.0,
                    'max_drawdown': 0.0,
                    'profit_factor': 0.0,
                    'performance_rating': 'unknown'
                }
            
            # Basic metrics
            win_rate = self.winning_trades / self.total_trades
            total_return = (self.current_balance / self.initial_balance - 1) * 100
            max_drawdown = max(self.drawdown_history) if self.drawdown_history else 0.0
            
            # Calculate profit factor
            winning_trades = [t for t in self.trade_history if t.get('outcome') == 'WIN']
            losing_trades = [t for t in self.trade_history if t.get('outcome') == 'LOSS']
            
            total_wins = sum(t.get('profit_loss', 0) for t in winning_trades)
            total_losses = abs(sum(t.get('profit_loss', 0) for t in losing_trades))
            
            profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
            
            # Performance rating
            if win_rate >= 0.75:
                performance_rating = 'excellent'
            elif win_rate >= 0.60:
                performance_rating = 'good'
            elif win_rate >= 0.50:
                performance_rating = 'average'
            else:
                performance_rating = 'poor'
            
            return {
                'win_rate': win_rate,
                'total_return': total_return,
                'max_drawdown': max_drawdown,
                'profit_factor': profit_factor,
                'performance_rating': performance_rating,
                'total_trades': self.total_trades,
                'current_balance': self.current_balance,
                'total_profit': self.total_profit
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return {}
    
    def calculate_optimal_risk_percentage(self) -> float:
        """Calculate optimal risk percentage based on performance and balance growth."""
        try:
            metrics = self.calculate_performance_metrics()
            
            if metrics['total_trades'] < 10:
                # Use conservative risk for first 10 trades
                return self.base_risk_percentage
            
            # Base risk adjustment based on performance
            performance_rating = metrics['performance_rating']
            performance_multiplier = self.performance_multipliers.get(performance_rating, 1.0)
            
            # Growth-based adjustment
            total_return = metrics['total_return']
            if total_return > 50:  # >50% growth
                growth_multiplier = 1.3
            elif total_return > 25:  # >25% growth
                growth_multiplier = 1.2
            elif total_return > 10:  # >10% growth
                growth_multiplier = 1.1
            else:
                growth_multiplier = 1.0
            
            # Drawdown protection
            max_drawdown = metrics['max_drawdown']
            if max_drawdown > 0.15:  # >15% drawdown
                drawdown_multiplier = 0.7
            elif max_drawdown > 0.10:  # >10% drawdown
                drawdown_multiplier = 0.8
            elif max_drawdown > 0.05:  # >5% drawdown
                drawdown_multiplier = 0.9
            else:
                drawdown_multiplier = 1.0
            
            # Calculate optimal risk
            optimal_risk = (self.base_risk_percentage * 
                          performance_multiplier * 
                          growth_multiplier * 
                          drawdown_multiplier)
            
            # Apply limits
            optimal_risk = max(0.01, min(optimal_risk, self.max_risk_percentage))
            
            logger.info(f"📊 Risk calculation: Base={self.base_risk_percentage:.1%}, "
                       f"Performance={performance_multiplier:.1f}x, Growth={growth_multiplier:.1f}x, "
                       f"Drawdown={drawdown_multiplier:.1f}x → Optimal={optimal_risk:.1%}")
            
            return optimal_risk
            
        except Exception as e:
            logger.error(f"Error calculating optimal risk: {e}")
            return self.base_risk_percentage
    
    def calculate_compound_position_size(self, signal, base_position_size: int = None) -> Dict:
        """Calculate position size with compound growth consideration."""
        try:
            # Get optimal risk percentage
            optimal_risk_pct = self.calculate_optimal_risk_percentage()
            
            # Calculate risk amount
            risk_amount = self.current_balance * optimal_risk_pct
            
            # Calculate stop distance in pips
            if 'JPY' in signal.pair:
                pip_value = 0.01
            else:
                pip_value = 0.0001
            
            stop_distance_pips = abs(signal.entry_price - signal.stop_loss) / pip_value
            
            # Calculate position size
            if stop_distance_pips > 0:
                pip_value_usd = 0.10  # $0.10 per pip for 1000 units
                units = int(risk_amount / (stop_distance_pips * pip_value_usd))
                units = max(1000, min(units, 200000))  # Min 1k, max 200k units
            else:
                units = 1000
            
            # Compare with base position size if provided
            if base_position_size:
                size_multiplier = units / base_position_size
            else:
                size_multiplier = 1.0
            
            # Calculate potential profit with compound sizing
            potential_profit = (signal.pips_target * pip_value_usd * units / 1000)
            potential_loss = (signal.pips_risk * pip_value_usd * units / 1000)
            
            result = {
                'units': units,
                'risk_amount': risk_amount,
                'risk_percentage': optimal_risk_pct,
                'size_multiplier': size_multiplier,
                'potential_profit': potential_profit,
                'potential_loss': potential_loss,
                'current_balance': self.current_balance,
                'growth_factor': self.current_balance / self.initial_balance
            }
            
            logger.info(f"💰 Compound position: {units:,} units (${risk_amount:.2f} risk, "
                       f"{optimal_risk_pct:.1%}) - {size_multiplier:.1f}x base size")
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating compound position size: {e}")
            return {
                'units': 1000,
                'risk_amount': self.current_balance * 0.03,
                'risk_percentage': 0.03,
                'size_multiplier': 1.0,
                'potential_profit': 25.0,
                'potential_loss': 15.0,
                'current_balance': self.current_balance,
                'growth_factor': 1.0
            }
    
    def project_compound_growth(self, months: int = 12, avg_trades_per_month: int = 20) -> Dict:
        """Project potential account growth with compound reinvestment."""
        try:
            metrics = self.calculate_performance_metrics()
            
            # Use historical performance or defaults
            if metrics['total_trades'] > 20:
                win_rate = metrics['win_rate']
                avg_win_pips = np.mean([t.get('pips_gained', 25) for t in self.trade_history if t.get('outcome') == 'WIN'])
                avg_loss_pips = abs(np.mean([t.get('pips_gained', -15) for t in self.trade_history if t.get('outcome') == 'LOSS']))
            else:
                # Conservative defaults
                win_rate = 0.60
                avg_win_pips = 25
                avg_loss_pips = 15
            
            # Simulation parameters
            current_balance = self.current_balance
            monthly_projections = []
            
            for month in range(1, months + 1):
                monthly_profit = 0
                
                for trade in range(avg_trades_per_month):
                    # Calculate position size for current balance
                    risk_pct = self.calculate_optimal_risk_percentage()
                    risk_amount = current_balance * risk_pct
                    
                    # Simulate trade outcome
                    if np.random.random() < win_rate:
                        # Winning trade
                        pip_profit = avg_win_pips
                        trade_profit = (pip_profit * 0.10 * risk_amount) / (avg_loss_pips * 0.10)
                    else:
                        # Losing trade
                        trade_profit = -risk_amount
                    
                    monthly_profit += trade_profit
                    current_balance += trade_profit
                
                monthly_projections.append({
                    'month': month,
                    'balance': current_balance,
                    'monthly_profit': monthly_profit,
                    'monthly_return': (monthly_profit / (current_balance - monthly_profit)) * 100,
                    'total_return': ((current_balance / self.initial_balance) - 1) * 100
                })
            
            final_balance = current_balance
            total_return = ((final_balance / self.initial_balance) - 1) * 100
            annualized_return = ((final_balance / self.initial_balance) ** (12 / months) - 1) * 100
            
            return {
                'projections': monthly_projections,
                'final_balance': final_balance,
                'total_return': total_return,
                'annualized_return': annualized_return,
                'assumptions': {
                    'win_rate': win_rate,
                    'avg_win_pips': avg_win_pips,
                    'avg_loss_pips': avg_loss_pips,
                    'trades_per_month': avg_trades_per_month
                }
            }
            
        except Exception as e:
            logger.error(f"Error projecting compound growth: {e}")
            return {}
    
    def generate_compound_report(self) -> str:
        """Generate comprehensive compound growth report."""
        try:
            metrics = self.calculate_performance_metrics()
            projections = self.project_compound_growth(12, 20)
            
            report = f"""
🎯 COMPOUND PROFIT ANALYSIS REPORT
{'='*60}

📊 CURRENT PERFORMANCE:
Initial Balance: ${self.initial_balance:.2f}
Current Balance: ${self.current_balance:.2f}
Total Profit: ${self.total_profit:.2f}
Total Return: {metrics.get('total_return', 0):.1f}%
Win Rate: {metrics.get('win_rate', 0):.1%}
Max Drawdown: {metrics.get('max_drawdown', 0):.1%}
Performance Rating: {metrics.get('performance_rating', 'unknown').upper()}

💰 POSITION SIZING:
Current Risk %: {self.calculate_optimal_risk_percentage():.1%}
Growth Factor: {self.current_balance / self.initial_balance:.1f}x
Next Position Multiplier: {self.current_balance / self.initial_balance:.1f}x base size

📈 12-MONTH PROJECTIONS:
"""
            
            if projections:
                report += f"Projected Final Balance: ${projections['final_balance']:,.2f}\n"
                report += f"Projected Total Return: {projections['total_return']:.1f}%\n"
                report += f"Annualized Return: {projections['annualized_return']:.1f}%\n"
                
                report += "\n📅 QUARTERLY BREAKDOWN:\n"
                for quarter in [3, 6, 9, 12]:
                    if quarter <= len(projections['projections']):
                        q_data = projections['projections'][quarter-1]
                        report += f"Month {quarter}: ${q_data['balance']:,.2f} ({q_data['total_return']:.1f}% total return)\n"
                
                report += f"\n🎯 ASSUMPTIONS:\n"
                report += f"Win Rate: {projections['assumptions']['win_rate']:.1%}\n"
                report += f"Avg Win: {projections['assumptions']['avg_win_pips']:.1f} pips\n"
                report += f"Avg Loss: {projections['assumptions']['avg_loss_pips']:.1f} pips\n"
                report += f"Trades/Month: {projections['assumptions']['trades_per_month']}\n"
            
            report += f"""
💡 COMPOUND STRATEGY:
✅ Risk scales with account growth
✅ Performance-based position sizing
✅ Drawdown protection built-in
✅ Automatic profit reinvestment

🚀 NEXT MILESTONES:
"""
            
            # Calculate next milestones
            current_growth = (self.current_balance / self.initial_balance - 1) * 100
            next_milestone = ((int(current_growth) // 25) + 1) * 25
            milestone_balance = self.initial_balance * (1 + next_milestone / 100)
            
            report += f"Next {next_milestone}% Growth: ${milestone_balance:.2f}\n"
            report += f"Profit Needed: ${milestone_balance - self.current_balance:.2f}\n"
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating compound report: {e}")
            return "Error generating compound report"
    
    def save_performance_data(self, filename: str = "compound_performance.json"):
        """Save performance data to file."""
        try:
            data = {
                'initial_balance': self.initial_balance,
                'current_balance': self.current_balance,
                'total_profit': self.total_profit,
                'total_trades': self.total_trades,
                'winning_trades': self.winning_trades,
                'trade_history': self.trade_history[-100:],  # Last 100 trades
                'balance_history': self.balance_history[-100:],  # Last 100 balances
                'performance_metrics': self.calculate_performance_metrics(),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"💾 Performance data saved to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving performance data: {e}")

# Test the compound profit manager
if __name__ == "__main__":
    # Initialize manager
    compound_manager = CompoundProfitManager(initial_balance=1000)
    
    print("🎯 COMPOUND PROFIT MANAGER TEST:")
    print("=" * 60)
    
    # Simulate some trades
    test_trades = [
        {'profit_loss': 25.0, 'outcome': 'WIN', 'pips_gained': 25},
        {'profit_loss': -15.0, 'outcome': 'LOSS', 'pips_gained': -15},
        {'profit_loss': 30.0, 'outcome': 'WIN', 'pips_gained': 30},
        {'profit_loss': 20.0, 'outcome': 'WIN', 'pips_gained': 20},
        {'profit_loss': -15.0, 'outcome': 'LOSS', 'pips_gained': -15},
    ]
    
    print("📊 Simulating trades...")
    for i, trade in enumerate(test_trades, 1):
        compound_manager.update_balance(trade)
        print(f"Trade {i}: ${trade['profit_loss']:.2f} → Balance: ${compound_manager.current_balance:.2f}")
    
    # Show performance metrics
    metrics = compound_manager.calculate_performance_metrics()
    print(f"\n📈 Performance Metrics:")
    print(f"Win Rate: {metrics['win_rate']:.1%}")
    print(f"Total Return: {metrics['total_return']:.1f}%")
    print(f"Performance Rating: {metrics['performance_rating'].upper()}")
    
    # Show optimal risk
    optimal_risk = compound_manager.calculate_optimal_risk_percentage()
    print(f"\n💰 Optimal Risk: {optimal_risk:.1%}")
    
    # Generate full report
    print("\n" + compound_manager.generate_compound_report()) 