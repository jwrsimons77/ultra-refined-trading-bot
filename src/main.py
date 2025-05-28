#!/usr/bin/env python3
"""
Sniper Bot - Event-Driven Trading Bot
Main entry point for the application.
"""

import argparse
import os
import sys
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.dirname(__file__))

from sniper_bot import SniperBot
from data_generator import NewsDataGenerator

def generate_sample_data(args):
    """Generate sample news data."""
    print("🎲 Generating sample news data...")
    
    generator = NewsDataGenerator()
    df = generator.generate_sample_data(
        num_articles=args.num_articles,
        start_date=args.start_date,
        end_date=args.end_date
    )
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    output_path = args.output or 'data/sample_news.csv'
    
    df.to_csv(output_path, index=False)
    print(f"✅ Generated {len(df)} news articles and saved to {output_path}")
    
    # Show sample
    print("\n📋 Sample data:")
    print(df.head())

def run_backtest(args):
    """Run backtest on news data."""
    print("🎯 Starting Sniper Bot backtest...")
    
    if not os.path.exists(args.data_file):
        print(f"❌ Error: Data file '{args.data_file}' not found.")
        print("💡 Tip: Generate sample data first with: python main.py generate-data")
        return
    
    # Initialize bot
    bot = SniperBot(
        initial_capital=args.capital,
        max_daily_trades=args.max_trades
    )
    
    # Run backtest
    print(f"📊 Loading data from {args.data_file}")
    print(f"💰 Initial capital: ${args.capital:,}")
    print(f"📈 Max daily trades: {args.max_trades}")
    print(f"🎯 Confidence threshold: {args.confidence}")
    print()
    
    try:
        results_df, performance = bot.run_full_backtest(
            args.data_file, 
            confidence_threshold=args.confidence
        )
        
        if results_df.empty:
            print("⚠️ No trades were generated. Try lowering the confidence threshold.")
            return
        
        # Display results
        print("\n" + "="*60)
        print("🎯 SNIPER BOT BACKTEST RESULTS")
        print("="*60)
        
        print(f"📊 Total Trades: {performance['total_trades']}")
        print(f"🏆 Wins: {performance['wins']}")
        print(f"💔 Losses: {performance['losses']}")
        print(f"📈 Win Rate: {performance['win_rate']*100:.1f}%")
        print(f"💰 Total Return: {performance['total_return_pct']:.2f}%")
        print(f"📊 Average Return per Trade: {performance['avg_return_pct']:.2f}%")
        print(f"📉 Max Drawdown: {performance['max_drawdown_pct']:.2f}%")
        print(f"⚡ Sharpe Ratio: {performance['sharpe_ratio']:.2f}")
        print(f"💵 Final Capital: ${performance['final_capital']:,.2f}")
        
        # Show best trades
        print("\n🏆 Top 5 Best Trades:")
        top_trades = results_df.nlargest(5, 'return_pct')[['date', 'ticker', 'return_pct', 'outcome']]
        for _, trade in top_trades.iterrows():
            print(f"  {trade['date']} | {trade['ticker']} | {trade['return_pct']:+.2f}% | {trade['outcome']}")
        
        # Show worst trades
        print("\n💔 Top 5 Worst Trades:")
        worst_trades = results_df.nsmallest(5, 'return_pct')[['date', 'ticker', 'return_pct', 'outcome']]
        for _, trade in worst_trades.iterrows():
            print(f"  {trade['date']} | {trade['ticker']} | {trade['return_pct']:+.2f}% | {trade['outcome']}")
        
        print(f"\n📁 Detailed results saved to: outputs/backtest_results.csv")
        print(f"📊 Performance plots saved to: outputs/performance_plots.png")
        
    except Exception as e:
        print(f"❌ Error running backtest: {e}")
        return

def launch_ui():
    """Launch Streamlit UI."""
    print("🚀 Launching Sniper Bot UI...")
    print("🌐 Opening browser at http://localhost:8501")
    print("💡 Press Ctrl+C to stop the server")
    
    import subprocess
    import sys
    
    # Launch Streamlit
    cmd = [sys.executable, "-m", "streamlit", "run", "src/streamlit_app.py"]
    subprocess.run(cmd)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="🎯 Sniper Bot - Event-Driven Trading Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate sample data
  python main.py generate-data --num-articles 1000

  # Run backtest
  python main.py backtest --data-file data/sample_news.csv --capital 5000

  # Launch web UI
  python main.py ui
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate data command
    gen_parser = subparsers.add_parser('generate-data', help='Generate sample news data')
    gen_parser.add_argument('--num-articles', type=int, default=500, 
                           help='Number of articles to generate (default: 500)')
    gen_parser.add_argument('--start-date', default='2023-01-01',
                           help='Start date (YYYY-MM-DD, default: 2023-01-01)')
    gen_parser.add_argument('--end-date', default='2023-12-31',
                           help='End date (YYYY-MM-DD, default: 2023-12-31)')
    gen_parser.add_argument('--output', help='Output file path (default: data/sample_news.csv)')
    
    # Backtest command
    backtest_parser = subparsers.add_parser('backtest', help='Run backtest')
    backtest_parser.add_argument('--data-file', default='data/sample_news.csv',
                                help='Path to news data CSV file')
    backtest_parser.add_argument('--capital', type=float, default=1000.0,
                                help='Initial capital (default: 1000)')
    backtest_parser.add_argument('--max-trades', type=int, default=3,
                                help='Max daily trades (default: 3)')
    backtest_parser.add_argument('--confidence', type=float, default=0.6,
                                help='Confidence threshold (default: 0.6)')
    
    # UI command
    ui_parser = subparsers.add_parser('ui', help='Launch Streamlit web interface')
    
    args = parser.parse_args()
    
    if args.command == 'generate-data':
        generate_sample_data(args)
    elif args.command == 'backtest':
        run_backtest(args)
    elif args.command == 'ui':
        launch_ui()
    else:
        parser.print_help()
        print("\n🎯 Welcome to Sniper Bot!")
        print("💡 Use one of the commands above to get started.")
        print("🌐 For the best experience, try: python main.py ui")

if __name__ == "__main__":
    main()