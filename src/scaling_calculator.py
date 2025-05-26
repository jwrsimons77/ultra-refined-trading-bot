#!/usr/bin/env python3
"""
🎯 Account Scaling Calculator
Calculate time to scale from $10,000 to $100,000 based on real backtest data
"""

import math
from monthly_backtest_10k import run_monthly_backtest

def calculate_scaling_timeline():
    """Calculate how long to scale $10,000 to $100,000."""
    
    print("🎯 ACCOUNT SCALING CALCULATOR")
    print("=" * 50)
    print("📊 Based on REAL historical backtest data")
    print()
    
    # Get real backtest results
    print("🔄 Running backtest to get real performance data...")
    results = run_monthly_backtest()
    
    if 'error' in results:
        print(f"❌ Error: {results['error']}")
        return
    
    # Extract performance metrics
    initial_balance = results['initial_balance']
    final_balance = results['final_balance']
    total_profit = results['total_profit']
    monthly_return = results['total_return']
    
    print(f"✅ Backtest completed successfully!")
    print()
    
    print("📊 REAL PERFORMANCE DATA:")
    print(f"   💰 Starting Capital: ${initial_balance:,.2f}")
    print(f"   💰 Final Balance: ${final_balance:,.2f}")
    print(f"   📈 Monthly Profit: ${total_profit:,.2f}")
    print(f"   📈 Monthly Return: {monthly_return:.2f}%")
    print()
    
    # Calculate scaling scenarios
    target_balance = 100000
    current_balance = 10000
    
    # Convert monthly return to decimal
    monthly_rate = monthly_return / 100
    
    print("🎯 SCALING SCENARIOS:")
    print("=" * 50)
    
    # Scenario 1: Conservative (use actual monthly return)
    if monthly_rate > 0:
        months_needed = math.log(target_balance / current_balance) / math.log(1 + monthly_rate)
        years_needed = months_needed / 12
        
        print(f"📈 SCENARIO 1: Conservative (Actual Performance)")
        print(f"   Monthly Return: {monthly_return:.2f}%")
        print(f"   Time to $100,000: {months_needed:.1f} months ({years_needed:.1f} years)")
        print(f"   Growth Factor: {target_balance/current_balance:.1f}x")
        print()
        
        # Show year-by-year progression
        print("📅 YEAR-BY-YEAR PROGRESSION:")
        balance = current_balance
        for year in range(1, int(years_needed) + 2):
            for month in range(12):
                balance *= (1 + monthly_rate)
                if balance >= target_balance:
                    print(f"   🎯 Year {year}, Month {month+1}: ${balance:,.2f} - TARGET REACHED!")
                    break
            else:
                print(f"   📊 Year {year}: ${balance:,.2f}")
                continue
            break
        print()
    
    # Scenario 2: Optimistic (assume 25% higher returns)
    optimistic_rate = monthly_rate * 1.25
    if optimistic_rate > 0:
        months_optimistic = math.log(target_balance / current_balance) / math.log(1 + optimistic_rate)
        years_optimistic = months_optimistic / 12
        
        print(f"🚀 SCENARIO 2: Optimistic (+25% Performance)")
        print(f"   Monthly Return: {optimistic_rate*100:.2f}%")
        print(f"   Time to $100,000: {months_optimistic:.1f} months ({years_optimistic:.1f} years)")
        print()
    
    # Scenario 3: Conservative (assume 25% lower returns)
    conservative_rate = monthly_rate * 0.75
    if conservative_rate > 0:
        months_conservative = math.log(target_balance / current_balance) / math.log(1 + conservative_rate)
        years_conservative = months_conservative / 12
        
        print(f"⚖️ SCENARIO 3: Conservative (-25% Performance)")
        print(f"   Monthly Return: {conservative_rate*100:.2f}%")
        print(f"   Time to $100,000: {months_conservative:.1f} months ({years_conservative:.1f} years)")
        print()
    
    # Key milestones
    print("🎯 KEY MILESTONES:")
    print("=" * 30)
    balance = current_balance
    milestones = [15000, 20000, 30000, 50000, 75000, 100000]
    
    for month in range(1, 120):  # Max 10 years
        balance *= (1 + monthly_rate)
        
        for milestone in milestones[:]:
            if balance >= milestone:
                years = month / 12
                print(f"   💰 ${milestone:,}: Month {month} ({years:.1f} years)")
                milestones.remove(milestone)
        
        if not milestones:
            break
    print()
    
    # Risk factors
    print("⚠️ IMPORTANT CONSIDERATIONS:")
    print("=" * 40)
    print("   • Results based on 30-day real historical data")
    print("   • Market conditions can vary significantly")
    print("   • Past performance doesn't guarantee future results")
    print("   • Compound growth assumes consistent reinvestment")
    print("   • Risk management is crucial for long-term success")
    print("   • Consider diversification and position sizing")
    print()
    
    # Summary
    if monthly_rate > 0:
        print("📋 SUMMARY:")
        print(f"   🎯 Goal: Scale ${current_balance:,} → ${target_balance:,}")
        print(f"   📈 Based on: {monthly_return:.2f}% monthly returns")
        print(f"   ⏱️ Estimated Time: {years_needed:.1f} years")
        print(f"   💪 Growth Required: {target_balance/current_balance:.1f}x")
        print(f"   📊 Annual Return: {(monthly_rate * 12) * 100:.1f}%")

def main():
    """Run the scaling calculator."""
    calculate_scaling_timeline()

if __name__ == "__main__":
    main() 