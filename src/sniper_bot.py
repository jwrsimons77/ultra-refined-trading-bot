import pandas as pd
import numpy as np
import yfinance as yf
import re
import warnings
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
from tqdm import tqdm
import logging

warnings.filterwarnings('ignore')

class SniperBot:
    """
    Event-driven trading bot that analyzes news sentiment and executes backtested trades.
    """
    
    def __init__(self, initial_capital: float = 1000.0, max_daily_trades: int = 3):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.max_daily_trades = max_daily_trades
        self.trades = []
        self.portfolio_history = []
        
        # Event type weights
        self.event_weights = {
            'earnings': 2.0,
            'merger': 2.0,
            'acquisition': 2.0,
            'product launch': 2.0,
            'executive': 1.5,
            'partnership': 1.3,
            'default': 1.0
        }
        
        # Source weights
        self.source_weights = {
            'bloomberg': 1.5,
            'wsj': 1.5,
            'wall street journal': 1.5,
            'reuters': 1.4,
            'cnbc': 1.3,
            'marketwatch': 1.2,
            'yahoo finance': 1.1,
            'default': 1.0
        }
        
        # Load S&P 500 tickers
        self.sp500_tickers = self._load_sp500_tickers()
        
        # Initialize sentiment analyzer
        self.sentiment_analyzer = self._initialize_sentiment_analyzer()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _load_sp500_tickers(self) -> List[str]:
        """Load S&P 500 ticker symbols."""
        try:
            # Try to get from Wikipedia
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            tables = pd.read_html(url)
            sp500_table = tables[0]
            tickers = sp500_table['Symbol'].tolist()
            self.logger.info(f"Loaded {len(tickers)} S&P 500 tickers from Wikipedia")
            return tickers
        except Exception as e:
            self.logger.warning(f"Could not load S&P 500 tickers from Wikipedia: {e}")
            # Fallback to a subset of major tickers
            return [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'BRK-B',
                'UNH', 'JNJ', 'JPM', 'V', 'PG', 'HD', 'MA', 'DIS', 'PYPL', 'BAC',
                'ADBE', 'CRM', 'NFLX', 'CMCSA', 'XOM', 'VZ', 'ABT', 'KO', 'PFE',
                'TMO', 'COST', 'AVGO', 'ACN', 'DHR', 'NEE', 'LLY', 'TXN', 'WMT'
            ]
    
    def _initialize_sentiment_analyzer(self):
        """Initialize FinBERT sentiment analyzer."""
        try:
            # Try to load FinBERT
            model_name = "ProsusAI/finbert"
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
            sentiment_pipeline = pipeline("sentiment-analysis", 
                                         model=model, 
                                         tokenizer=tokenizer,
                                         device=0 if torch.cuda.is_available() else -1)
            self.logger.info("FinBERT sentiment analyzer loaded successfully")
            return sentiment_pipeline
        except Exception as e:
            self.logger.warning(f"Could not load FinBERT: {e}. Falling back to TextBlob.")
            return None
    
    def load_news_data(self, file_path: str) -> pd.DataFrame:
        """
        Load news data from CSV file.
        Expected columns: headline, date, source (optional), ticker (optional)
        """
        try:
            df = pd.read_csv(file_path)
            required_columns = ['headline', 'date']
            
            if not all(col in df.columns for col in required_columns):
                raise ValueError(f"CSV must contain columns: {required_columns}")
            
            # Convert date column
            df['date'] = pd.to_datetime(df['date'])
            
            # Add source column if missing
            if 'source' not in df.columns:
                df['source'] = 'unknown'
            
            # Add ticker column if missing
            if 'ticker' not in df.columns:
                df['ticker'] = None
            
            self.logger.info(f"Loaded {len(df)} news articles from {file_path}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading news data: {e}")
            raise
    
    def filter_event_driven_news(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter news for event-driven content."""
        event_keywords = [
            # Earnings
            'earnings', 'quarterly results', 'q1', 'q2', 'q3', 'q4', 'revenue', 'profit',
            'eps', 'earnings per share', 'beat estimates', 'miss estimates',
            
            # M&A
            'merger', 'acquisition', 'acquire', 'merge', 'takeover', 'buyout',
            'deal', 'purchase', 'bought', 'sold to',
            
            # Product launches
            'launch', 'unveil', 'announce', 'release', 'debut', 'introduce',
            'new product', 'product line',
            
            # Executive changes
            'ceo', 'cfo', 'coo', 'president', 'executive', 'resign', 'retire',
            'appoint', 'hire', 'step down', 'leadership change',
            
            # Partnerships
            'partnership', 'collaborate', 'joint venture', 'alliance'
        ]
        
        pattern = '|'.join(event_keywords)
        mask = df['headline'].str.contains(pattern, case=False, na=False)
        filtered_df = df[mask].copy()
        
        self.logger.info(f"Filtered to {len(filtered_df)} event-driven news articles")
        return filtered_df
    
    def extract_tickers(self, headline: str) -> List[str]:
        """Extract ticker symbols from headline."""
        found_tickers = []
        
        # Look for ticker patterns (1-5 uppercase letters)
        ticker_pattern = r'\b[A-Z]{1,5}\b'
        potential_tickers = re.findall(ticker_pattern, headline)
        
        # Filter to only include known S&P 500 tickers
        for ticker in potential_tickers:
            if ticker in self.sp500_tickers:
                found_tickers.append(ticker)
        
        return list(set(found_tickers))  # Remove duplicates
    
    def analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of text using FinBERT or TextBlob."""
        try:
            if self.sentiment_analyzer:
                # Use FinBERT
                result = self.sentiment_analyzer(text)[0]
                label = result['label'].lower()
                score = result['score']
                
                if label == 'positive':
                    return score
                elif label == 'negative':
                    return -score
                else:  # neutral
                    return 0.0
            else:
                # Fallback to TextBlob
                blob = TextBlob(text)
                return blob.sentiment.polarity
                
        except Exception as e:
            self.logger.warning(f"Error in sentiment analysis: {e}")
            return 0.0
    
    def get_event_type_weight(self, headline: str) -> float:
        """Determine event type and return corresponding weight."""
        headline_lower = headline.lower()
        
        for event_type, weight in self.event_weights.items():
            if event_type in headline_lower:
                return weight
        
        return self.event_weights['default']
    
    def get_source_weight(self, source: str) -> float:
        """Get weight based on news source credibility."""
        source_lower = source.lower()
        
        for source_name, weight in self.source_weights.items():
            if source_name in source_lower:
                return weight
        
        return self.source_weights['default']
    
    def calculate_confidence_score(self, sentiment_score: float, headline: str, source: str) -> float:
        """Calculate confidence score for trading decision."""
        event_weight = self.get_event_type_weight(headline)
        source_weight = self.get_source_weight(source)
        
        confidence_score = abs(sentiment_score) * event_weight * source_weight
        return min(confidence_score, 1.0)  # Cap at 1.0
    
    def get_price_data(self, ticker: str, start_date: datetime, days_ahead: int = 10) -> Dict:
        """Fetch price data for backtesting."""
        try:
            end_date = start_date + timedelta(days=days_ahead + 10)  # Extra buffer
            
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date - timedelta(days=20), end=end_date)
            
            if hist.empty:
                return None
            
            # Find next trading day after news date
            trading_days = hist.index[hist.index > start_date]
            if len(trading_days) == 0:
                return None
            
            next_trading_day = trading_days[0]
            next_day_open = hist.loc[next_trading_day, 'Open']
            
            # Get prices for 3 and 5 days ahead
            future_prices = {}
            for days in [3, 5]:
                future_date_idx = min(days, len(trading_days) - 1)
                if future_date_idx < len(trading_days):
                    future_date = trading_days[future_date_idx]
                    future_prices[f'price_{days}_day'] = hist.loc[future_date, 'Close']
                else:
                    future_prices[f'price_{days}_day'] = hist.iloc[-1]['Close']
            
            # Calculate volatility (10-day standard deviation)
            pre_news_data = hist[hist.index < start_date].tail(10)
            volatility = pre_news_data['Close'].pct_change().std() if len(pre_news_data) > 1 else 0.02
            
            return {
                'next_day_open': next_day_open,
                'volatility': volatility,
                **future_prices,
                'trading_days': trading_days[:5]  # First 5 trading days
            }
            
        except Exception as e:
            self.logger.warning(f"Error fetching price data for {ticker}: {e}")
            return None
    
    def calculate_trade_levels(self, buy_price: float, volatility: float, sentiment_score: float) -> Dict:
        """Calculate entry, target, and stop loss levels."""
        # Adjust target and stop based on volatility and sentiment strength
        volatility_multiplier = max(2.0, min(4.0, volatility * 100))  # 2x to 4x volatility
        
        if sentiment_score > 0:  # Bullish
            target_price = buy_price * (1 + 0.05 + volatility_multiplier * 0.01)
            stop_loss = buy_price * 0.97
        else:  # Bearish (short position)
            target_price = buy_price * 0.95
            stop_loss = buy_price * (1 + 0.03 + volatility_multiplier * 0.01)
        
        return {
            'buy_price': buy_price,
            'target_price': target_price,
            'stop_loss': stop_loss
        }
    
    def simulate_trade(self, ticker: str, trade_levels: Dict, price_data: Dict, sentiment_score: float) -> Dict:
        """Simulate a single trade over 5 days."""
        buy_price = trade_levels['buy_price']
        target_price = trade_levels['target_price']
        stop_loss = trade_levels['stop_loss']
        
        is_long = sentiment_score > 0
        
        # Check each trading day
        for i, trading_day in enumerate(price_data['trading_days']):
            try:
                stock = yf.Ticker(ticker)
                day_data = stock.history(start=trading_day, end=trading_day + timedelta(days=1))
                
                if day_data.empty:
                    continue
                
                high = day_data['High'].iloc[0]
                low = day_data['Low'].iloc[0]
                close = day_data['Close'].iloc[0]
                
                if is_long:
                    # Long position
                    if high >= target_price:
                        return {
                            'outcome': 'WIN',
                            'exit_price': target_price,
                            'days_held': i + 1,
                            'return_pct': (target_price - buy_price) / buy_price * 100
                        }
                    elif low <= stop_loss:
                        return {
                            'outcome': 'LOSS',
                            'exit_price': stop_loss,
                            'days_held': i + 1,
                            'return_pct': (stop_loss - buy_price) / buy_price * 100
                        }
                else:
                    # Short position
                    if low <= target_price:
                        return {
                            'outcome': 'WIN',
                            'exit_price': target_price,
                            'days_held': i + 1,
                            'return_pct': (buy_price - target_price) / buy_price * 100
                        }
                    elif high >= stop_loss:
                        return {
                            'outcome': 'LOSS',
                            'exit_price': stop_loss,
                            'days_held': i + 1,
                            'return_pct': (buy_price - stop_loss) / buy_price * 100
                        }
                
                # If it's the last day, exit at close
                if i == 4:  # 5th day (0-indexed)
                    if is_long:
                        return_pct = (close - buy_price) / buy_price * 100
                    else:
                        return_pct = (buy_price - close) / buy_price * 100
                    
                    return {
                        'outcome': 'EXIT_DAY_5',
                        'exit_price': close,
                        'days_held': 5,
                        'return_pct': return_pct
                    }
                    
            except Exception as e:
                self.logger.warning(f"Error simulating day {i} for {ticker}: {e}")
                continue
        
        # If we get here, something went wrong
        return {
            'outcome': 'ERROR',
            'exit_price': buy_price,
            'days_held': 0,
            'return_pct': 0.0
        }
    
    def process_news_and_generate_trades(self, news_df: pd.DataFrame, confidence_threshold: float = 0.6) -> pd.DataFrame:
        """Process news data and generate trade ideas."""
        trade_ideas = []
        
        for _, row in tqdm(news_df.iterrows(), total=len(news_df), desc="Processing news"):
            headline = row['headline']
            date = row['date']
            source = row['source']
            
            # Extract tickers
            tickers = self.extract_tickers(headline)
            if not tickers:
                continue
            
            # Analyze sentiment
            sentiment_score = self.analyze_sentiment(headline)
            
            # Calculate confidence score
            confidence_score = self.calculate_confidence_score(sentiment_score, headline, source)
            
            # Only proceed if confidence is high enough
            if confidence_score < confidence_threshold:
                continue
            
            for ticker in tickers:
                trade_ideas.append({
                    'date': date,
                    'ticker': ticker,
                    'headline': headline,
                    'source': source,
                    'sentiment_score': sentiment_score,
                    'confidence_score': confidence_score
                })
        
        trade_ideas_df = pd.DataFrame(trade_ideas)
        
        if not trade_ideas_df.empty:
            # Sort by confidence score and limit to top trades per day
            trade_ideas_df = trade_ideas_df.sort_values(['date', 'confidence_score'], ascending=[True, False])
            trade_ideas_df = trade_ideas_df.groupby('date').head(self.max_daily_trades).reset_index(drop=True)
        
        self.logger.info(f"Generated {len(trade_ideas_df)} trade ideas")
        return trade_ideas_df
    
    def backtest_trades(self, trade_ideas_df: pd.DataFrame) -> pd.DataFrame:
        """Backtest all trade ideas."""
        results = []
        
        for _, trade in tqdm(trade_ideas_df.iterrows(), total=len(trade_ideas_df), desc="Backtesting trades"):
            ticker = trade['ticker']
            date = trade['date']
            sentiment_score = trade['sentiment_score']
            confidence_score = trade['confidence_score']
            
            # Get price data
            price_data = self.get_price_data(ticker, date)
            if not price_data:
                continue
            
            # Calculate trade levels
            trade_levels = self.calculate_trade_levels(
                price_data['next_day_open'], 
                price_data['volatility'], 
                sentiment_score
            )
            
            # Simulate trade
            trade_result = self.simulate_trade(ticker, trade_levels, price_data, sentiment_score)
            
            # Record result
            result = {
                'date': date,
                'ticker': ticker,
                'headline': trade['headline'],
                'source': trade['source'],
                'sentiment_score': sentiment_score,
                'confidence_score': confidence_score,
                'buy_price': trade_levels['buy_price'],
                'target_price': trade_levels['target_price'],
                'stop_loss': trade_levels['stop_loss'],
                'exit_price': trade_result['exit_price'],
                'outcome': trade_result['outcome'],
                'days_held': trade_result['days_held'],
                'return_pct': trade_result['return_pct'],
                'position_type': 'LONG' if sentiment_score > 0 else 'SHORT'
            }
            
            results.append(result)
            self.trades.append(result)
        
        results_df = pd.DataFrame(results)
        self.logger.info(f"Backtested {len(results_df)} trades")
        return results_df
    
    def calculate_portfolio_performance(self, results_df: pd.DataFrame) -> Dict:
        """Calculate overall portfolio performance."""
        if results_df.empty:
            return {}
        
        # Calculate basic metrics
        total_trades = len(results_df)
        wins = len(results_df[results_df['outcome'] == 'WIN'])
        losses = len(results_df[results_df['outcome'] == 'LOSS'])
        win_rate = wins / total_trades if total_trades > 0 else 0
        
        # Calculate returns
        total_return_pct = results_df['return_pct'].sum()
        avg_return_pct = results_df['return_pct'].mean()
        
        # Calculate Sharpe ratio (simplified)
        returns_std = results_df['return_pct'].std()
        sharpe_ratio = avg_return_pct / returns_std if returns_std > 0 else 0
        
        # Calculate max drawdown
        cumulative_returns = (1 + results_df['return_pct'] / 100).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - rolling_max) / rolling_max
        max_drawdown = drawdown.min() * 100
        
        return {
            'total_trades': total_trades,
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'total_return_pct': total_return_pct,
            'avg_return_pct': avg_return_pct,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown_pct': max_drawdown,
            'final_capital': self.initial_capital * (1 + total_return_pct / 100)
        }
    
    def save_results(self, results_df: pd.DataFrame, output_path: str = 'outputs/backtest_results.csv'):
        """Save backtest results to CSV."""
        results_df.to_csv(output_path, index=False)
        self.logger.info(f"Results saved to {output_path}")
    
    def plot_performance(self, results_df: pd.DataFrame, save_path: str = 'outputs/performance_plots.png'):
        """Create performance visualization plots."""
        if results_df.empty:
            self.logger.warning("No results to plot")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Cumulative Returns
        cumulative_returns = (1 + results_df['return_pct'] / 100).cumprod()
        axes[0, 0].plot(range(len(cumulative_returns)), cumulative_returns)
        axes[0, 0].set_title('Cumulative Returns')
        axes[0, 0].set_xlabel('Trade Number')
        axes[0, 0].set_ylabel('Cumulative Return')
        axes[0, 0].grid(True)
        
        # 2. Return Distribution
        axes[0, 1].hist(results_df['return_pct'], bins=30, alpha=0.7, edgecolor='black')
        axes[0, 1].set_title('Return Distribution')
        axes[0, 1].set_xlabel('Return %')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].grid(True)
        
        # 3. Win/Loss by Confidence Score
        win_loss_data = results_df.groupby('outcome')['confidence_score'].mean()
        axes[1, 0].bar(win_loss_data.index, win_loss_data.values)
        axes[1, 0].set_title('Average Confidence Score by Outcome')
        axes[1, 0].set_ylabel('Average Confidence Score')
        axes[1, 0].grid(True)
        
        # 4. Monthly Performance
        results_df['month'] = pd.to_datetime(results_df['date']).dt.to_period('M')
        monthly_returns = results_df.groupby('month')['return_pct'].sum()
        axes[1, 1].bar(range(len(monthly_returns)), monthly_returns.values)
        axes[1, 1].set_title('Monthly Returns')
        axes[1, 1].set_xlabel('Month')
        axes[1, 1].set_ylabel('Return %')
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        self.logger.info(f"Performance plots saved to {save_path}")
    
    def run_full_backtest(self, news_file_path: str, confidence_threshold: float = 0.6) -> Tuple[pd.DataFrame, Dict]:
        """Run the complete backtesting pipeline."""
        self.logger.info("Starting full backtest pipeline...")
        
        # Load and filter news
        news_df = self.load_news_data(news_file_path)
        filtered_news = self.filter_event_driven_news(news_df)
        
        # Generate trade ideas
        trade_ideas = self.process_news_and_generate_trades(filtered_news, confidence_threshold)
        
        if trade_ideas.empty:
            self.logger.warning("No trade ideas generated")
            return pd.DataFrame(), {}
        
        # Backtest trades
        results_df = self.backtest_trades(trade_ideas)
        
        if results_df.empty:
            self.logger.warning("No successful trades to analyze")
            return pd.DataFrame(), {}
        
        # Calculate performance
        performance = self.calculate_portfolio_performance(results_df)
        
        # Save results
        self.save_results(results_df)
        
        # Create plots
        self.plot_performance(results_df)
        
        self.logger.info("Backtest completed successfully!")
        return results_df, performance 