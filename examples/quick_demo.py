#!/usr/bin/env python3
"""
Quick Demo of Sniper Bot
This script demonstrates basic usage of the Sniper Bot.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from sniper_bot import SniperBot
from data_generator import NewsDataGenerator
import pandas as pd

def main():
    print("🎯 Sniper Bot Quick Demo")
    print("=" * 40)
    
    # Step 1: Generate sample data
    print("\n1️⃣ Generating sample news data...")
    generator = NewsDataGenerator()
    news_df = generator.generate_sample_data(
        num_articles=100,
        start_date='2023-06-01',
        end_date='2023-08-31'
    )
    
    # Save sample data
    os.makedirs('../data', exist_ok=True)
    sample_path = '../data/demo_news.csv'
    news_df.to_csv(sample_path, index=False)
    print(f"✅ Generated {len(news_df)} news articles")
    
    # Show sample headlines
    print("\n📰 Sample Headlines:")
    for i, row in news_df.head(3).iterrows():
        print(f"  • {row['headline']}")
    
    # Step 2: Initialize bot
    print("\n2️⃣ Initializing Sniper Bot...")
    bot = SniperBot(
        initial_capital=2000.0,  # $2,000 starting capital
        max_daily_trades=2       # Max 2 trades per day
    )
    print("✅ Bot initialized")
    
    # Step 3: Run backtest
    print("\n3️⃣ Running backtest...")
    print("⏳ This may take a few minutes...")
    
    try:
        results_df, performance = bot.run_full_backtest(
            sample_path, 
            confidence_threshold=0.5  # Lower threshold for demo
        )
        
        if results_df.empty:
            print("⚠️ No trades generated. Try lowering confidence threshold.")
            return
        
        # Step 4: Display results
        print("\n4️⃣ Results Summary:")
        print("-" * 30)
        print(f"📊 Total Trades: {performance['total_trades']}")
        print(f"🏆 Win Rate: {performance['win_rate']*100:.1f}%")
        print(f"💰 Total Return: {performance['total_return_pct']:.2f}%")
        print(f"💵 Final Capital: ${performance['final_capital']:,.2f}")
        
        # Show top trades
        if len(results_df) > 0:
            print(f"\n🏆 Best Trade:")
            best_trade = results_df.loc[results_df['return_pct'].idxmax()]
            print(f"  {best_trade['ticker']} on {best_trade['date']}: {best_trade['return_pct']:+.2f}%")
            
            print(f"\n💔 Worst Trade:")
            worst_trade = results_df.loc[results_df['return_pct'].idxmin()]
            print(f"  {worst_trade['ticker']} on {worst_trade['date']}: {worst_trade['return_pct']:+.2f}%")
        
        print(f"\n📁 Detailed results saved to: outputs/backtest_results.csv")
        
    except Exception as e:
        print(f"❌ Error running backtest: {e}")
        return
    
    print("\n✨ Demo completed!")
    print("💡 Try the full web interface with: python src/main.py ui")

if __name__ == "__main__":
    main() 