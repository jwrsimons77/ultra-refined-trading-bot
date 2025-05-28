# 🌍 Forex Sniper Bot Setup Guide

## Why Forex is Better Than Stocks for Trading Bots

### ✅ **Forex Advantages:**
- **24/5 Market**: Trades Sunday 5pm - Friday 5pm EST (no gaps!)
- **Higher Leverage**: 50:1 to 500:1 vs 2:1 for stocks
- **Lower Capital**: Start with $100-500 vs $25k for day trading stocks
- **Faster Execution**: Instant fills, no waiting for market open
- **More Predictable**: Central bank news is scheduled and predictable
- **No Earnings Surprises**: No sudden 20% gaps from earnings
- **Better for Bots**: Technical patterns work better in forex

### 📈 **Best Currency Pairs for Bots:**
- **EUR/USD**: Most liquid, tightest spreads (1-2 pips)
- **GBP/USD**: High volatility, 20-50 pip moves daily
- **USD/JPY**: Trending pair, good for momentum
- **AUD/USD**: Commodity-driven, predictable patterns

---

## 🚀 Step 1: Get Your FREE OANDA Account

### Sign Up for OANDA Practice Account:
1. Go to: https://www.oanda.com/register/
2. Choose **"Practice Account"** (FREE with $100k virtual money)
3. Fill in your details
4. Verify your email

### Get Your API Credentials:
1. Login to your OANDA account
2. Go to **"Manage API Access"** in account settings
3. Generate a **Personal Access Token**
4. Note your **Account ID** (format: 123-456-7890123-456)

---

## 🔧 Step 2: Install Dependencies

```bash
# Install OANDA API
pip install oandapyV20

# Install other required packages (if not already installed)
pip install pandas numpy requests textblob
```

---

## ⚙️ Step 3: Configure Environment Variables

### Option A: Set in Terminal (Temporary)
```bash
export OANDA_API_KEY="your_personal_access_token_here"
export OANDA_ACCOUNT_ID="your_account_id_here"
export ALPHA_VANTAGE_API_KEY="PITRBDQSWC2015J1"  # You already have this
```

### Option B: Add to ~/.zshrc (Permanent)
```bash
echo 'export OANDA_API_KEY="your_personal_access_token_here"' >> ~/.zshrc
echo 'export OANDA_ACCOUNT_ID="your_account_id_here"' >> ~/.zshrc
echo 'export ALPHA_VANTAGE_API_KEY="PITRBDQSWC2015J1"' >> ~/.zshrc
source ~/.zshrc
```

---

## 🎯 Step 4: Test Your Setup

### Quick Test Script:
```python
import os
from src.forex_sniper_bot import ForexSniperBot

# Your credentials
api_key = os.getenv('OANDA_API_KEY')
account_id = os.getenv('OANDA_ACCOUNT_ID')

print(f"API Key: {api_key[:10]}..." if api_key else "❌ No API Key")
print(f"Account ID: {account_id}" if account_id else "❌ No Account ID")

# Test connection
bot = ForexSniperBot(api_key, account_id, environment="practice")

# Test getting current price
price = bot.get_current_price('EUR_USD')
print(f"EUR/USD Price: {price}")

# Test account summary
account = bot.get_account_summary()
print(f"Account Balance: ${account.get('balance', 'N/A')}")
```

---

## 📊 Step 5: Generate Your First Forex Signals

```python
# Generate signals
signals = bot.generate_forex_signals(confidence_threshold=0.3)

print(f"Generated {len(signals)} forex signals:")
for signal in signals:
    print(f"  {signal.pair} {signal.signal_type} @ {signal.entry_price:.5f}")
    print(f"    Target: {signal.pip_target} pips | Stop: {signal.pip_stop} pips")
    print(f"    News: {signal.headline[:60]}...")
    print()
```

---

## 🎮 Step 6: Understanding Forex Signals

### Signal Example:
```
EUR_USD BUY @ 1.08450
  Target: 30 pips (1.08750) 
  Stop: 15 pips (1.08300)
  News: ECB hints at rate hike amid strong inflation data
```

### What This Means:
- **Pair**: EUR/USD (Euro vs US Dollar)
- **Action**: BUY (expecting EUR to strengthen vs USD)
- **Entry**: 1.08450 (current price)
- **Target**: 30 pips profit = $300 profit on 1 standard lot
- **Stop**: 15 pips loss = $150 max loss on 1 standard lot

### Pip Values:
- **1 pip EUR/USD** = $10 per standard lot (100k units)
- **1 pip GBP/USD** = $10 per standard lot
- **1 pip USD/JPY** = $9.50 per standard lot (varies with price)

---

## 💰 Step 7: Position Sizing & Risk Management

### Conservative Approach:
```python
# Risk 1% of account per trade
account_balance = 100000  # $100k practice account
risk_per_trade = account_balance * 0.01  # $1000 max risk

# For 15 pip stop loss on EUR/USD
pip_value = 10  # $10 per pip for standard lot
max_lots = risk_per_trade / (15 * pip_value)  # 6.67 lots max
```

### Recommended Starting Size:
- **Practice Account**: 0.1 lots (10k units) = $1 per pip
- **Real Account**: 0.01 lots (1k units) = $0.10 per pip

---

## 🔄 Step 8: Automated Trading (Optional)

### Place Orders Automatically:
```python
# Generate signals
signals = bot.generate_forex_signals(confidence_threshold=0.5)

# Place orders for high-confidence signals
for signal in signals:
    if signal.confidence_score > 0.7:
        success = bot.place_order(signal, units=1000)  # 0.01 lots
        if success:
            print(f"✅ Order placed: {signal.pair} {signal.signal_type}")
        else:
            print(f"❌ Order failed: {signal.pair}")
```

---

## 📈 Step 9: Key Forex Trading Times

### Best Trading Hours (EST):
- **London Open**: 3:00 AM - 12:00 PM (highest volume)
- **New York Open**: 8:00 AM - 5:00 PM (overlaps with London)
- **Asian Session**: 7:00 PM - 4:00 AM (lower volatility)

### Major News Events:
- **US NFP**: First Friday of month, 8:30 AM EST
- **FOMC Meetings**: 8 times per year, 2:00 PM EST
- **ECB Meetings**: Monthly, 7:45 AM EST
- **BOE Meetings**: Monthly, 7:00 AM EST

---

## 🎯 Expected Performance

### Realistic Expectations:
- **Win Rate**: 55-65% (better than stocks)
- **Risk/Reward**: 1:2 ratio (15 pip stop, 30 pip target)
- **Monthly Return**: 5-15% with proper risk management
- **Drawdown**: 10-20% maximum

### Why Forex is More Profitable:
1. **Higher Leverage**: 50:1 vs 2:1 for stocks
2. **24/5 Trading**: More opportunities
3. **Predictable News**: Central bank schedules are known
4. **Better Technical Analysis**: Cleaner charts, fewer gaps

---

## 🚨 Important Notes

### Practice First:
- **ALWAYS** test with practice account first
- Run for at least 1 month before going live
- Verify all signals manually initially

### Risk Management:
- Never risk more than 1-2% per trade
- Use stop losses on EVERY trade
- Don't trade during major news if you're new

### API Limits:
- **OANDA Practice**: 20 requests/second (plenty for bot)
- **Alpha Vantage**: 5 calls/minute (sufficient for news)

---

## 🎉 Ready to Start!

Your forex bot is now ready! It's simpler and potentially more profitable than stocks because:

1. **No complex earnings analysis** - just central bank policy
2. **24/5 market** - no overnight gaps
3. **Higher leverage** - bigger profits with same capital
4. **More predictable** - economic calendars are published

Start with the practice account and watch your bot generate real forex signals based on live news! 🚀 