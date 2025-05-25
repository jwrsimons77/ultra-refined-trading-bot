# 🚀 Getting Started with Sniper Bot

Welcome to the Sniper Bot! This guide will help you get up and running quickly.

## 📋 Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Internet connection (for downloading dependencies and stock data)

## ⚡ Quick Start (5 minutes)

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Run Simple Demo
```bash
python3 src/simple_demo.py
```

This will:
- Generate 100 sample news articles
- Analyze them for trading signals
- Show you BUY/SELL recommendations
- Save results to CSV

### 3. Generate More Data
```bash
python3 src/data_generator.py
```

### 4. Launch Web Interface
```bash
python3 src/main.py ui
```

Then open http://localhost:8501 in your browser.

## 🎯 What You'll See

The simple demo will output something like:

```
🎯 Simple Sniper Bot Demo
==================================================

1️⃣ Generating sample news data...
✅ Generated 100 news articles

📰 Sample Headlines:
  • AAPL beats Q3 earnings expectations with strong iPhone sales
  • TSLA announces major acquisition of battery manufacturer
  • GOOGL launches revolutionary new AI platform

2️⃣ Initializing Simple Sniper Bot...
✅ Bot initialized

3️⃣ Analyzing news for trading signals...
📰 Filtered to 64 event-driven articles

4️⃣ Generated 59 trading signals:
--------------------------------------------------
📈 BUY signals: 35
📉 SELL signals: 24

🏆 Top 5 Highest Confidence Signals:
  BUY AAPL | Confidence: 2.100 | 2023-03-13
  BUY GOOGL | Confidence: 2.100 | 2023-04-24
  BUY TSLA | Confidence: 1.960 | 2023-07-13
```

## 📊 Understanding the Output

### Trading Signals
- **BUY**: Positive sentiment detected (earnings beats, acquisitions, product launches)
- **SELL**: Negative sentiment detected (earnings misses, lawsuits, executive departures)

### Confidence Score
- **Range**: 0.0 to 3.0+
- **Formula**: `sentiment_strength × event_weight × source_weight`
- **Higher = Better**: More confident trading signals

### Event Weights
- **Earnings, M&A, Product Launches**: 2.0x weight
- **Executive Changes**: 1.5x weight
- **Partnerships**: 1.3x weight

### Source Weights
- **Bloomberg, WSJ**: 1.5x weight
- **Reuters**: 1.4x weight
- **CNBC**: 1.3x weight

## 🔧 Next Steps

### Option 1: Use Your Own Data
1. Create a CSV file with columns: `headline`, `date`, `source`
2. Run: `python3 src/main.py backtest --data-file your_data.csv`

### Option 2: Full Backtesting
```bash
# Generate larger dataset
python3 src/main.py generate-data --num-articles 1000

# Run full backtest with FinBERT sentiment analysis
python3 src/main.py backtest --capital 5000 --confidence 0.7
```

### Option 3: Web Interface
```bash
python3 src/main.py ui
```

Features:
- Upload your own data or generate samples
- Interactive parameter tuning
- Real-time backtesting
- Performance visualizations
- Trade detail analysis

## 📁 File Structure

```
sniper_bot/
├── src/
│   ├── sniper_bot.py      # Full bot with FinBERT & backtesting
│   ├── simple_demo.py     # Lightweight demo (recommended start)
│   ├── data_generator.py  # Sample data creation
│   ├── streamlit_app.py   # Web interface
│   └── main.py           # Command-line interface
├── data/                 # Generated data files
├── outputs/              # Results and plots
└── configs/              # Configuration files
```

## 🎛️ Configuration

Edit `configs/bot_config.yaml` to customize:
- Portfolio settings (capital, max trades)
- Risk management (stop loss, take profit)
- Sentiment analysis parameters
- Event type weights

## 🐛 Troubleshooting

### Common Issues

**1. "ModuleNotFoundError"**
```bash
pip3 install -r requirements.txt
```

**2. "No trading signals generated"**
- Lower the confidence threshold: `--confidence 0.3`
- Check your data has event-driven keywords

**3. "FinBERT loading slowly"**
- First run downloads the model (~500MB)
- Use simple demo for quick testing

**4. "Streamlit not found"**
```bash
pip3 install streamlit
```

### Performance Tips

- **Start Small**: Use 100-500 articles for testing
- **Simple First**: Try `simple_demo.py` before full backtesting
- **Check Data**: Ensure headlines contain ticker symbols
- **Adjust Threshold**: Lower confidence threshold if no signals

## 📈 Example Results

A typical backtest might show:
- **Total Trades**: 127
- **Win Rate**: 53.5%
- **Total Return**: 12.34%
- **Sharpe Ratio**: 1.42
- **Max Drawdown**: -8.21%

## 🎓 Learning More

1. **Read the Code**: Start with `simple_demo.py`
2. **Experiment**: Try different confidence thresholds
3. **Customize**: Modify event weights and keywords
4. **Extend**: Add your own sentiment analysis methods

## 💡 Tips for Success

1. **Quality Data**: Better news data = better signals
2. **Event Focus**: Look for earnings, M&A, product launches
3. **Source Quality**: Bloomberg/WSJ articles get higher weights
4. **Risk Management**: Don't ignore stop losses and position sizing
5. **Backtesting**: Always test strategies before live trading

## 🆘 Need Help?

- **Check README.md**: Comprehensive documentation
- **Run Examples**: Start with provided demos
- **Review Code**: Well-commented and modular
- **GitHub Issues**: Report bugs or request features

---

**Happy Trading! 🎯📈**

*Remember: This is for educational purposes only. Always do your own research before making investment decisions.* 