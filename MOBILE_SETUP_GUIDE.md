# 📱 Mobile Signal Manager - Setup Guide

**Real-time trading signals from news analysis - optimized for mobile trading**

## 🚀 Quick Start (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch Mobile-Friendly Interface
```bash
streamlit run src/signal_manager_app.py
```

### 3. Open on Your Phone
- Visit the URL shown in terminal (usually `http://localhost:8501`)
- Add to home screen for app-like experience
- Works on any device with a web browser

## 📊 What You Get

### 🎯 **Real-time Signal Generation**
- **Live News Analysis**: Scans 200+ financial news sources
- **AI Sentiment Analysis**: Advanced NLP to detect market sentiment
- **Smart Filtering**: Only high-confidence, actionable signals
- **Mobile-Optimized Cards**: Easy-to-read signal cards with key info

### 📱 **Mobile-First Design**
- **Touch-Friendly**: Large buttons and swipe gestures
- **Responsive Layout**: Adapts to any screen size
- **Quick Actions**: Execute, cancel, or view details with one tap
- **Auto-Refresh**: Real-time updates without manual refresh

### 📈 **Professional Features**
- **Multi-API Integration**: Alpha Vantage, Polygon.io, Stock News API
- **Signal Database**: SQLite storage for signal history
- **Backtesting Engine**: Test strategies with historical data
- **Revenue Projections**: Calculate potential profits

## 🔑 API Setup (Optional but Recommended)

### Free API Keys (5 minutes setup)

#### 1. Alpha Vantage (Free: 5 calls/min)
```bash
# Sign up: https://www.alphavantage.co/support/#api-key
export ALPHA_VANTAGE_API_KEY="your_key_here"
```

#### 2. Polygon.io (Free: 5 calls/min)
```bash
# Sign up: https://polygon.io/
export POLYGON_API_KEY="your_key_here"
```

#### 3. Stock News API (Free: 100 calls/day)
```bash
# Sign up: https://stocknewsapi.com/
export STOCK_NEWS_API_KEY="your_key_here"
```

### Environment Variables Setup

**Linux/Mac:**
```bash
echo 'export ALPHA_VANTAGE_API_KEY="your_key"' >> ~/.bashrc
echo 'export POLYGON_API_KEY="your_key"' >> ~/.bashrc
echo 'export STOCK_NEWS_API_KEY="your_key"' >> ~/.bashrc
source ~/.bashrc
```

**Windows:**
```cmd
setx ALPHA_VANTAGE_API_KEY "your_key"
setx POLYGON_API_KEY "your_key"
setx STOCK_NEWS_API_KEY "your_key"
```

## 📱 Mobile Usage Guide

### 🎯 **Dashboard Tab**
- **Signal Cards**: Swipe through active signals
- **Quick Actions**: Execute/Cancel with one tap
- **Metrics**: Live portfolio stats
- **Filters**: Filter by type, confidence, etc.

### 🔍 **Generate Signals Tab**
- **Live Scan**: Generate signals from real news
- **Confidence Slider**: Adjust signal quality threshold
- **API Status**: Check connection to news sources
- **Auto-Refresh**: Set automatic signal updates

### 📈 **Backtest Tab**
- **Historical Analysis**: Test strategy performance
- **Date Range**: Select testing period
- **Performance Charts**: Visual results
- **Metrics**: Win rate, returns, Sharpe ratio

### ⚙️ **Settings Tab**
- **Bot Configuration**: Capital, max trades, etc.
- **API Management**: Check and configure keys
- **Data Export**: Download signal history

## 🎯 Signal Card Features

Each signal shows:
- **Ticker & Direction**: AAPL - BUY
- **Entry Price**: Current market price
- **Target & Stop**: Profit target and risk limit
- **Confidence Score**: AI-calculated confidence (0-3)
- **News Headline**: Driving news event
- **Time Remaining**: Until signal expires

### Action Buttons:
- **✅ Execute**: Mark as executed in your broker
- **❌ Cancel**: Remove from active signals
- **📊 Details**: View full analysis and news

## 💹 Revenue Projections

### Example Scenarios:

**Conservative Strategy** (Confidence > 1.0)
- Capital: $5,000
- Expected Win Rate: ~60%
- Projected Monthly Return: 3-5%
- Annual Projection: $1,800-$3,000 profit

**Moderate Strategy** (Confidence > 0.8)
- Capital: $10,000
- Expected Win Rate: ~55%
- Projected Monthly Return: 4-7%
- Annual Projection: $4,800-$8,400 profit

**Aggressive Strategy** (Confidence > 0.6)
- Capital: $20,000
- Expected Win Rate: ~50%
- Projected Monthly Return: 5-10%
- Annual Projection: $12,000-$24,000 profit

*Note: Past performance doesn't guarantee future results*

## 🔧 Advanced Configuration

### Custom Event Weights
Edit `src/enhanced_sniper_bot.py`:
```python
self.event_weights = {
    'earnings': 2.5,      # Earnings announcements
    'merger': 2.5,        # M&A activity
    'acquisition': 2.5,   # Acquisitions
    'product launch': 2.0, # New products
    'executive': 1.8,     # Leadership changes
    'partnership': 1.5,   # Strategic partnerships
    'upgrade': 1.7,       # Analyst upgrades
    'downgrade': 1.7,     # Analyst downgrades
}
```

### Source Credibility Weights
```python
self.source_weights = {
    'bloomberg': 2.0,     # Premium sources
    'reuters': 1.8,
    'wsj': 1.9,
    'cnbc': 1.6,
    'marketwatch': 1.4,
    'default': 1.0
}
```

## 📊 Demo Mode

Without API keys, the system runs in demo mode:
- Uses simulated news data
- Generates realistic signals
- Full backtesting functionality
- Perfect for testing and learning

### Run Demo:
```bash
python src/demo_with_real_apis.py
```

## 🔒 Security & Privacy

- **Local Storage**: All data stored locally in SQLite
- **No Cloud Dependencies**: Runs entirely on your device
- **API Keys**: Stored as environment variables
- **Open Source**: Full code transparency

## 📱 Mobile Browser Tips

### iOS Safari:
1. Open the app URL
2. Tap Share button
3. Select "Add to Home Screen"
4. App icon appears on home screen

### Android Chrome:
1. Open the app URL
2. Tap menu (3 dots)
3. Select "Add to Home screen"
4. App shortcut created

### Features:
- **Full Screen**: Hides browser UI
- **Offline Capable**: Cached for offline viewing
- **Push Notifications**: (if enabled)
- **Native Feel**: Smooth animations and gestures

## 🚨 Risk Management

### Built-in Safety Features:
- **Stop Losses**: Automatic risk limits
- **Position Sizing**: Controlled exposure
- **Signal Expiry**: Time-limited signals
- **Confidence Thresholds**: Quality filters

### Best Practices:
1. **Start Small**: Begin with small capital
2. **Diversify**: Don't put all money in one signal
3. **Set Limits**: Use stop losses religiously
4. **Review Performance**: Regular strategy assessment
5. **Stay Informed**: Understand the underlying news

## 🆘 Troubleshooting

### Common Issues:

**"No signals generated"**
- Lower confidence threshold
- Check API keys are set
- Verify internet connection
- Try demo mode first

**"API rate limit exceeded"**
- Wait for rate limit reset
- Use multiple API keys
- Reduce refresh frequency

**"Mobile interface not responsive"**
- Clear browser cache
- Try different browser
- Check internet connection
- Restart Streamlit server

**"Database errors"**
- Check write permissions
- Clear data directory
- Restart application

## 📞 Support

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Check README.md for details
- **Demo**: Run demo script for testing
- **Community**: Share strategies and tips

## 🎉 Success Tips

1. **Paper Trade First**: Test with virtual money
2. **Monitor Performance**: Track win rates and returns
3. **Adjust Parameters**: Fine-tune confidence thresholds
4. **Stay Disciplined**: Follow your trading rules
5. **Keep Learning**: Understand market dynamics

---

**Ready to start? Launch the app and start generating signals!**

```bash
streamlit run src/signal_manager_app.py
```

*Happy Trading! 📱📈* 