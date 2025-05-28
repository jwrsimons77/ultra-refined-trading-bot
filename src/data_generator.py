import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class NewsDataGenerator:
    """
    Generate sample news data for testing the Sniper Bot.
    """
    
    def __init__(self):
        self.tickers = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM',
            'V', 'PG', 'HD', 'MA', 'DIS', 'PYPL', 'BAC', 'ADBE', 'CRM', 'NFLX'
        ]
        
        self.sources = [
            'Bloomberg', 'WSJ', 'Reuters', 'CNBC', 'MarketWatch', 
            'Yahoo Finance', 'Financial Times', 'TechCrunch'
        ]
        
        # Positive headlines templates
        self.positive_templates = [
            "{ticker} beats Q{quarter} earnings expectations with strong revenue growth",
            "{ticker} announces major acquisition of competitor for ${amount}B",
            "{ticker} launches revolutionary new product line",
            "{ticker} reports record quarterly revenue of ${amount}B",
            "{ticker} CEO announces ambitious expansion plans",
            "{ticker} forms strategic partnership with major tech company",
            "{ticker} receives upgrade from analysts following strong performance",
            "{ticker} announces ${amount}B share buyback program",
            "{ticker} beats earnings estimates by {percent}%",
            "{ticker} unveils breakthrough technology platform"
        ]
        
        # Negative headlines templates
        self.negative_templates = [
            "{ticker} misses Q{quarter} earnings amid declining sales",
            "{ticker} faces regulatory investigation over business practices",
            "{ticker} CEO resigns following company scandal",
            "{ticker} cuts guidance for next quarter due to market headwinds",
            "{ticker} reports disappointing quarterly results",
            "{ticker} faces class action lawsuit from shareholders",
            "{ticker} announces layoffs affecting {percent}% of workforce",
            "{ticker} stock downgraded by major investment firm",
            "{ticker} warns of supply chain disruptions impacting revenue",
            "{ticker} loses major client contract worth ${amount}M"
        ]
        
        # Neutral headlines templates
        self.neutral_templates = [
            "{ticker} schedules Q{quarter} earnings call for next week",
            "{ticker} announces board meeting to discuss strategic initiatives",
            "{ticker} files quarterly report with SEC",
            "{ticker} executive to speak at industry conference",
            "{ticker} updates corporate governance policies",
            "{ticker} announces dividend payment date",
            "{ticker} releases sustainability report",
            "{ticker} participates in industry trade show"
        ]
    
    def generate_headline(self, ticker: str, sentiment: str) -> str:
        """Generate a headline for a given ticker and sentiment."""
        if sentiment == 'positive':
            template = random.choice(self.positive_templates)
        elif sentiment == 'negative':
            template = random.choice(self.negative_templates)
        else:
            template = random.choice(self.neutral_templates)
        
        # Fill in template variables
        quarter = random.choice(['1', '2', '3', '4'])
        amount = random.choice(['1.2', '2.5', '5.1', '10.3', '15.7'])
        percent = random.choice(['5', '10', '15', '20', '25'])
        
        headline = template.format(
            ticker=ticker,
            quarter=quarter,
            amount=amount,
            percent=percent
        )
        
        return headline
    
    def generate_sample_data(self, 
                           num_articles: int = 500, 
                           start_date: str = '2023-01-01',
                           end_date: str = '2023-12-31') -> pd.DataFrame:
        """
        Generate sample news dataset.
        
        Args:
            num_articles: Number of news articles to generate
            start_date: Start date for news articles
            end_date: End date for news articles
            
        Returns:
            DataFrame with columns: headline, date, source, ticker
        """
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        articles = []
        
        for _ in range(num_articles):
            # Random date between start and end
            random_days = random.randint(0, (end_dt - start_dt).days)
            article_date = start_dt + timedelta(days=random_days)
            
            # Skip weekends (assuming news comes out on weekdays)
            while article_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                article_date += timedelta(days=1)
            
            # Random ticker and source
            ticker = random.choice(self.tickers)
            source = random.choice(self.sources)
            
            # Random sentiment (weighted towards positive/negative for more interesting trades)
            sentiment_weights = [0.4, 0.4, 0.2]  # positive, negative, neutral
            sentiment = random.choices(['positive', 'negative', 'neutral'], weights=sentiment_weights)[0]
            
            # Generate headline
            headline = self.generate_headline(ticker, sentiment)
            
            articles.append({
                'headline': headline,
                'date': article_date.strftime('%Y-%m-%d'),
                'source': source,
                'ticker': ticker
            })
        
        df = pd.DataFrame(articles)
        df = df.sort_values('date').reset_index(drop=True)
        
        return df
    
    def save_sample_data(self, output_path: str = 'data/sample_news.csv', **kwargs):
        """Generate and save sample news data to CSV."""
        df = self.generate_sample_data(**kwargs)
        df.to_csv(output_path, index=False)
        print(f"Generated {len(df)} news articles and saved to {output_path}")
        return df

if __name__ == "__main__":
    generator = NewsDataGenerator()
    generator.save_sample_data() 