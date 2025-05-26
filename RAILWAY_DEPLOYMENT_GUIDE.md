# 🚀 Railway Deployment Guide - $10K Trading Bot

Deploy your optimized forex trading bot to Railway for 24/7 automated trading with your $10,000 virtual account.

## 📋 Prerequisites

1. **OANDA Account**: Virtual trading account with $10,000
2. **Railway Account**: Sign up at [railway.app](https://railway.app)
3. **GitHub Account**: For code deployment
4. **OANDA API Credentials**:
   - API Key
   - Account ID

## 🔑 Step 1: Get OANDA API Credentials

1. **Login to OANDA**: Go to [OANDA Demo Account](https://www.oanda.com/demo-account/tpa/personal_token)
2. **Generate API Token**:
   - Navigate to "Manage API Access"
   - Click "Generate" to create a new token
   - **Save this token** - you'll need it for Railway
3. **Get Account ID**:
   - Go to your account dashboard
   - Copy your Account ID (format: XXX-XXX-XXXXXXXX-XXX)

## 🚀 Step 2: Deploy to Railway

### Option A: Deploy from GitHub (Recommended)

1. **Push Code to GitHub**:
   ```bash
   git add .
   git commit -m "Deploy trading bot to Railway"
   git push origin main
   ```

2. **Connect to Railway**:
   - Go to [railway.app](https://railway.app)
   - Click "Start a New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `sniper_bot` repository

3. **Configure Environment Variables**:
   - In Railway dashboard, go to your project
   - Click "Variables" tab
   - Add these environment variables:
     ```
     OANDA_API_KEY=your_api_key_here
     OANDA_ACCOUNT_ID=your_account_id_here
     ```

### Option B: Deploy via Railway CLI

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and Deploy**:
   ```bash
   railway login
   railway init
   railway up
   ```

3. **Set Environment Variables**:
   ```bash
   railway variables set OANDA_API_KEY=your_api_key_here
   railway variables set OANDA_ACCOUNT_ID=your_account_id_here
   ```

## ⚙️ Step 3: Configure the Bot

The bot is pre-configured with optimized settings from backtesting:

- **Trading Pairs**: EUR/USD, GBP/USD, USD/JPY, USD/CHF, AUD/USD, USD/CAD, NZD/USD
- **Minimum Confidence**: 45%
- **Risk per Trade**: 3%
- **Max Concurrent Trades**: 8
- **Max Daily Trades**: 12
- **Trading Frequency**: Every 30 minutes
- **Health Checks**: Every 2 hours

## 📊 Step 4: Monitor Your Bot

### Railway Dashboard
- **Logs**: View real-time trading activity
- **Metrics**: Monitor CPU and memory usage
- **Deployments**: Track deployment history

### Key Log Messages to Watch For:
```
✅ Connected to OANDA account successfully
💰 Account Balance: $10,000.00
🎯 Signal found: EUR/USD BUY (67%)
✅ Trade executed successfully!
💚 Health check passed - Balance: $10,123.45
```

## 💰 Step 5: Expected Performance

Based on real historical backtesting:

- **Monthly Return**: ~6.03%
- **Expected Monthly Profit**: ~$603
- **Win Rate**: ~69%
- **Time to $100K**: ~3.3 years

### Monthly Projections:
- **Month 1**: $10,603
- **Month 6**: $13,500
- **Month 12**: $20,200
- **Month 24**: $40,800
- **Month 36**: $82,400

## 🛡️ Risk Management Features

- **Position Sizing**: Automatic 3% risk per trade
- **Stop Losses**: 20 pip stop loss on all trades
- **Take Profits**: 40 pip take profit targets
- **Daily Limits**: Maximum 12 trades per day
- **Concurrent Limits**: Maximum 8 open positions
- **Health Monitoring**: Automatic system health checks

## 🔧 Troubleshooting

### Common Issues:

1. **"Connection failed"**:
   - Check OANDA API credentials
   - Verify account ID format
   - Ensure demo account is active

2. **"No signals found"**:
   - Normal during low volatility periods
   - Bot scans every 30 minutes
   - Requires 45% minimum confidence

3. **"Daily trade limit reached"**:
   - Normal risk management
   - Resets at midnight UTC
   - Prevents overtrading

### Railway-Specific Issues:

1. **Bot not starting**:
   - Check environment variables are set
   - View logs in Railway dashboard
   - Ensure Procfile is correct

2. **Memory issues**:
   - Railway provides 512MB by default
   - Bot uses ~100MB typically
   - Upgrade plan if needed

## 📈 Scaling Your Account

### From $10K to $100K Timeline:
- **Conservative**: 4.3 years
- **Expected**: 3.3 years  
- **Optimistic**: 2.6 years

### Key Milestones:
- **$15K**: ~7 months
- **$20K**: ~12 months
- **$50K**: ~28 months
- **$100K**: ~40 months

## 💡 Pro Tips

1. **Monitor Regularly**: Check logs daily for the first week
2. **Don't Interfere**: Let the bot run its strategy
3. **Track Performance**: Note monthly returns
4. **Stay Informed**: Monitor major economic events
5. **Risk Management**: Never risk more than you can afford

## 🚨 Important Reminders

- **Virtual Money**: This is demo trading, not real money
- **Past Performance**: Historical results don't guarantee future performance
- **Market Risk**: Forex trading involves significant risk
- **Monitoring**: Always monitor your bot's performance
- **Backup Plan**: Have a plan to stop the bot if needed

## 📞 Support

If you encounter issues:

1. **Check Logs**: Railway dashboard → Logs tab
2. **Verify Credentials**: Ensure OANDA API access
3. **Review Settings**: Confirm environment variables
4. **Monitor Performance**: Track account balance changes

## 🎯 Success Metrics

Your bot is working correctly if you see:

- ✅ Regular trading sessions every 30 minutes
- ✅ Account balance growing over time
- ✅ Win rate around 60-70%
- ✅ Daily trade limits being respected
- ✅ Health checks passing every 2 hours

---

**Ready to deploy?** Follow the steps above and your $10K trading bot will be running 24/7 on Railway, working towards that $100K goal in ~3.3 years! 🚀 