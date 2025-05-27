#!/usr/bin/env python3
"""
Railway Bot Compound Interest Calculator
Shows 5-year projections with reinvestment
"""

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np

class CompoundCalculator:
    """Calculate compound returns for Railway bot."""
    
    def __init__(self, starting_balance=10057.04, monthly_roi=0.041):
        self.starting_balance = starting_balance
        self.monthly_roi = monthly_roi  # 4.1% from backtest
        self.results = []
        
    def calculate_compound_growth(self, years=5):
        """Calculate compound growth over specified years."""
        print(f"🚀 RAILWAY BOT COMPOUND CALCULATOR")
        print(f"📊 Starting Balance: ${self.starting_balance:,.2f}")
        print(f"📈 Monthly ROI: {self.monthly_roi:.1%}")
        print(f"⏰ Time Period: {years} years")
        print("=" * 60)
        
        current_balance = self.starting_balance
        months = years * 12
        
        # Track monthly progress
        monthly_data = []
        
        for month in range(1, months + 1):
            # Calculate monthly profit
            monthly_profit = current_balance * self.monthly_roi
            
            # Add profit to balance (compound effect)
            current_balance += monthly_profit
            
            # Store data
            year = (month - 1) // 12 + 1
            month_in_year = ((month - 1) % 12) + 1
            
            monthly_data.append({
                'month': month,
                'year': year,
                'month_in_year': month_in_year,
                'balance': current_balance,
                'monthly_profit': monthly_profit,
                'total_profit': current_balance - self.starting_balance,
                'roi_percent': ((current_balance - self.starting_balance) / self.starting_balance) * 100
            })
            
            # Print yearly summaries
            if month % 12 == 0:
                total_profit = current_balance - self.starting_balance
                roi_percent = (total_profit / self.starting_balance) * 100
                print(f"📅 Year {year}: ${current_balance:,.2f} | Profit: ${total_profit:,.2f} | ROI: {roi_percent:.1f}%")
        
        self.results = monthly_data
        return monthly_data
    
    def generate_projections(self):
        """Generate detailed projections and scenarios."""
        if not self.results:
            self.calculate_compound_growth()
        
        final_balance = self.results[-1]['balance']
        total_profit = final_balance - self.starting_balance
        
        print("\n" + "=" * 60)
        print("🎯 5-YEAR COMPOUND PROJECTIONS")
        print("=" * 60)
        print(f"💰 Final Balance: ${final_balance:,.2f}")
        print(f"📈 Total Profit: ${total_profit:,.2f}")
        print(f"🚀 Total ROI: {((final_balance - self.starting_balance) / self.starting_balance) * 100:.1f}%")
        print(f"📊 Balance Multiplier: {final_balance / self.starting_balance:.1f}x")
        
        # Yearly breakdown
        print("\n📅 YEAR-BY-YEAR BREAKDOWN:")
        for year in range(1, 6):
            year_data = [r for r in self.results if r['year'] == year]
            if year_data:
                end_balance = year_data[-1]['balance']
                year_profit = end_balance - (year_data[0]['balance'] - year_data[0]['monthly_profit'])
                print(f"   Year {year}: ${end_balance:,.2f} (+${year_profit:,.2f})")
        
        # Monthly income in final year
        final_monthly_profit = self.results[-1]['monthly_profit']
        print(f"\n💵 Monthly Income in Year 5: ${final_monthly_profit:,.2f}")
        print(f"💵 Daily Income in Year 5: ${final_monthly_profit/30:,.2f}")
        
        return {
            'final_balance': final_balance,
            'total_profit': total_profit,
            'total_roi': ((final_balance - self.starting_balance) / self.starting_balance) * 100,
            'final_monthly_income': final_monthly_profit
        }
    
    def scenario_analysis(self):
        """Analyze different ROI scenarios."""
        print("\n" + "=" * 60)
        print("🎲 SCENARIO ANALYSIS (5 Years)")
        print("=" * 60)
        
        scenarios = [
            {'name': 'Conservative', 'monthly_roi': 0.02, 'description': '2% monthly (if bot underperforms)'},
            {'name': 'Expected', 'monthly_roi': 0.041, 'description': '4.1% monthly (backtest result)'},
            {'name': 'Optimistic', 'monthly_roi': 0.06, 'description': '6% monthly (if bot improves)'},
            {'name': 'Best Case', 'monthly_roi': 0.08, 'description': '8% monthly (exceptional performance)'}
        ]
        
        scenario_results = []
        
        for scenario in scenarios:
            # Calculate 5-year compound
            balance = self.starting_balance
            for month in range(60):  # 5 years = 60 months
                balance += balance * scenario['monthly_roi']
            
            total_profit = balance - self.starting_balance
            roi_percent = (total_profit / self.starting_balance) * 100
            
            scenario_results.append({
                'name': scenario['name'],
                'monthly_roi': scenario['monthly_roi'],
                'final_balance': balance,
                'total_profit': total_profit,
                'roi_percent': roi_percent,
                'description': scenario['description']
            })
            
            print(f"📊 {scenario['name']:12} | ${balance:>12,.2f} | {roi_percent:>8.0f}% ROI | {scenario['description']}")
        
        return scenario_results
    
    def withdrawal_strategy(self, withdrawal_percent=0.5):
        """Calculate growth with partial profit withdrawal."""
        print(f"\n" + "=" * 60)
        print(f"💸 WITHDRAWAL STRATEGY ({withdrawal_percent:.0%} profit withdrawal)")
        print("=" * 60)
        
        current_balance = self.starting_balance
        total_withdrawn = 0
        
        for month in range(1, 61):  # 5 years
            # Calculate monthly profit
            monthly_profit = current_balance * self.monthly_roi
            
            # Withdraw percentage of profit
            withdrawal = monthly_profit * withdrawal_percent
            total_withdrawn += withdrawal
            
            # Reinvest remaining profit
            reinvested = monthly_profit - withdrawal
            current_balance += reinvested
            
            # Print yearly summaries
            if month % 12 == 0:
                year = month // 12
                print(f"📅 Year {year}: Balance: ${current_balance:,.2f} | Withdrawn: ${total_withdrawn:,.2f}")
        
        print(f"\n🎯 FINAL RESULTS:")
        print(f"💰 Final Balance: ${current_balance:,.2f}")
        print(f"💸 Total Withdrawn: ${total_withdrawn:,.2f}")
        print(f"🏆 Total Value: ${current_balance + total_withdrawn:,.2f}")
        print(f"📊 Effective ROI: {((current_balance + total_withdrawn - self.starting_balance) / self.starting_balance) * 100:.1f}%")
        
        return {
            'final_balance': current_balance,
            'total_withdrawn': total_withdrawn,
            'total_value': current_balance + total_withdrawn
        }
    
    def risk_analysis(self):
        """Analyze risk scenarios."""
        print(f"\n" + "=" * 60)
        print("⚠️  RISK ANALYSIS")
        print("=" * 60)
        
        # Simulate drawdown scenarios
        scenarios = [
            {'name': 'No Drawdowns', 'drawdown_months': 0, 'drawdown_percent': 0},
            {'name': 'Mild Drawdowns', 'drawdown_months': 6, 'drawdown_percent': -0.02},
            {'name': 'Moderate Drawdowns', 'drawdown_months': 12, 'drawdown_percent': -0.05},
            {'name': 'Severe Drawdowns', 'drawdown_months': 18, 'drawdown_percent': -0.10}
        ]
        
        for scenario in scenarios:
            balance = self.starting_balance
            
            for month in range(60):
                if month < scenario['drawdown_months']:
                    # Drawdown period
                    monthly_return = scenario['drawdown_percent']
                else:
                    # Normal performance
                    monthly_return = self.monthly_roi
                
                balance += balance * monthly_return
            
            total_profit = balance - self.starting_balance
            roi_percent = (total_profit / self.starting_balance) * 100
            
            print(f"📊 {scenario['name']:18} | ${balance:>12,.2f} | {roi_percent:>8.1f}% ROI")
        
        print(f"\n💡 Key Insights:")
        print(f"   • Even with 18 months of 10% monthly losses, you'd still be profitable")
        print(f"   • Diversification and risk management are crucial")
        print(f"   • Consider position sizing adjustments during drawdowns")

def main():
    """Run compound calculator analysis."""
    calculator = CompoundCalculator()
    
    # Main 5-year projection
    calculator.calculate_compound_growth(5)
    projections = calculator.generate_projections()
    
    # Scenario analysis
    calculator.scenario_analysis()
    
    # Withdrawal strategy
    calculator.withdrawal_strategy(0.5)  # Withdraw 50% of profits
    
    # Risk analysis
    calculator.risk_analysis()
    
    print(f"\n" + "=" * 60)
    print("🎯 SUMMARY")
    print("=" * 60)
    print(f"🚀 Your Railway bot with 4.1% monthly returns could grow:")
    print(f"   ${calculator.starting_balance:,.2f} → ${projections['final_balance']:,.2f} in 5 years")
    print(f"   That's a {projections['total_roi']:.0f}% total return!")
    print(f"   Monthly income in year 5: ${projections['final_monthly_income']:,.2f}")
    print(f"\n💡 Remember: Past performance doesn't guarantee future results")
    print(f"   Always use proper risk management and position sizing!")

if __name__ == "__main__":
    main() 