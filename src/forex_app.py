#!/usr/bin/env python3
"""
Simple Forex Trading Signal App
Clean, light UI focused on forex trading
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import os

# Import our forex bot
try:
    from forex_sniper_bot import ForexSniperBot
    FOREX_BOT_AVAILABLE = True
except ImportError:
    FOREX_BOT_AVAILABLE = False
    st.error("Forex bot not available. Please install oandapyV20: pip install oandapyV20")

# Page config
st.set_page_config(
    page_title="Forex Sniper",
    page_icon="💱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for light, clean design
st.markdown("""
<style>
    /* Main background */
    .main {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom containers */
    .forex-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #007bff;
    }
    
    .signal-card {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.1);
        border-left: 3px solid;
    }
    
    .buy-signal {
        border-left-color: #28a745;
    }
    
    .sell-signal {
        border-left-color: #dc3545;
    }
    
    /* Typography */
    .big-number {
        font-size: 2rem;
        font-weight: bold;
        color: #495057;
    }
    
    .currency-pair {
        font-size: 1.2rem;
        font-weight: 600;
        color: #343a40;
    }
    
    .price {
        font-family: 'Courier New', monospace;
        font-weight: bold;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(45deg, #007bff, #0056b3);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, #0056b3, #004085);
        transform: translateY(-1px);
    }
    
    /* Metrics */
    .metric-container {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 1px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def init_forex_bot():
    """Initialize forex bot if credentials are available."""
    api_key = os.getenv('OANDA_API_KEY')
    account_id = os.getenv('OANDA_ACCOUNT_ID')
    
    if not api_key or not account_id:
        return None, "Please set OANDA_API_KEY and OANDA_ACCOUNT_ID environment variables"
    
    try:
        bot = ForexSniperBot(api_key, account_id, environment="practice")
        return bot, None
    except Exception as e:
        return None, f"Error connecting to OANDA: {str(e)}"

def display_forex_prices(bot):
    """Display current forex prices."""
    st.markdown('<div class="forex-card">', unsafe_allow_html=True)
    st.subheader("💱 Live Forex Prices")
    
    major_pairs = ['EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CHF', 'AUD_USD', 'USD_CAD']
    
    cols = st.columns(3)
    
    for i, pair in enumerate(major_pairs):
        with cols[i % 3]:
            try:
                price_data = bot.get_current_price(pair)
                if price_data:
                    bid = price_data['bid']
                    ask = price_data['ask']
                    spread = price_data['spread']
                    
                    # Calculate spread in pips
                    pip_value = 0.01 if 'JPY' in pair else 0.0001
                    spread_pips = spread / pip_value
                    
                    st.markdown(f"""
                    <div class="metric-container">
                        <div class="currency-pair">{pair.replace('_', '/')}</div>
                        <div class="price">{bid:.5f} / {ask:.5f}</div>
                        <small>Spread: {spread_pips:.1f} pips</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"Failed to get {pair} price")
            except Exception as e:
                st.error(f"Error getting {pair}: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_account_info(bot):
    """Display account information."""
    try:
        account = bot.get_account_summary()
        if account:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Balance", f"${account.get('balance', 0):,.2f}")
            
            with col2:
                unrealized = account.get('unrealized_pl', 0)
                st.metric("Unrealized P/L", f"${unrealized:,.2f}", 
                         delta=f"{unrealized:+.2f}")
            
            with col3:
                st.metric("Open Trades", account.get('open_trades', 0))
            
            with col4:
                margin_used = account.get('margin_used', 0)
                st.metric("Margin Used", f"${margin_used:,.2f}")
    except Exception as e:
        st.error(f"Error getting account info: {str(e)}")

def display_forex_signals(bot):
    """Display forex trading signals."""
    st.markdown('<div class="forex-card">', unsafe_allow_html=True)
    st.subheader("📊 Forex Trading Signals")
    
    # Signal generation controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        confidence_threshold = st.slider(
            "Confidence Threshold", 
            min_value=0.1, 
            max_value=1.0, 
            value=0.3, 
            step=0.1,
            key="forex_confidence"
        )
    
    with col2:
        if st.button("🔄 Generate Signals", key="generate_forex"):
            with st.spinner("Generating forex signals..."):
                signals = bot.generate_forex_signals(confidence_threshold=confidence_threshold)
                st.session_state.forex_signals = signals
    
    with col3:
        if st.button("📈 Refresh Prices", key="refresh_prices"):
            st.rerun()
    
    # Display signals
    if hasattr(st.session_state, 'forex_signals') and st.session_state.forex_signals:
        signals = st.session_state.forex_signals
        
        st.write(f"**{len(signals)} Active Signals**")
        
        for signal in signals:
            signal_class = "buy-signal" if signal.signal_type == "BUY" else "sell-signal"
            
            # Calculate potential profit/loss
            pip_value = 0.01 if 'JPY' in signal.pair else 0.0001
            profit_pips = signal.pip_target
            risk_pips = signal.pip_stop
            risk_reward = profit_pips / risk_pips if risk_pips > 0 else 0
            
            st.markdown(f"""
            <div class="signal-card {signal_class}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{signal.pair.replace('_', '/')} {signal.signal_type}</strong><br>
                        <span class="price">Entry: {signal.entry_price:.5f}</span><br>
                        <small>Target: +{profit_pips} pips | Stop: -{risk_pips} pips | R/R: 1:{risk_reward:.1f}</small>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.1rem; font-weight: bold;">
                            {signal.confidence_score:.1%}
                        </div>
                        <small>Confidence</small>
                    </div>
                </div>
                <div style="margin-top: 0.5rem; font-size: 0.9rem; color: #6c757d;">
                    📰 {signal.headline[:80]}...
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"📈 Execute", key=f"execute_{signal.id}"):
                    # Here you would place the actual order
                    st.success(f"Order placed for {signal.pair} {signal.signal_type}")
            
            with col2:
                if st.button(f"ℹ️ Details", key=f"details_{signal.id}"):
                    with st.expander(f"{signal.pair} Signal Details", expanded=True):
                        st.write(f"**Full Headline:** {signal.headline}")
                        st.write(f"**Source:** {signal.source}")
                        st.write(f"**Sentiment Score:** {signal.sentiment_score:.3f}")
                        st.write(f"**Created:** {signal.created_at.strftime('%H:%M:%S')}")
                        st.write(f"**Expires:** {signal.expires_at.strftime('%H:%M:%S')}")
            
            with col3:
                if st.button(f"❌ Cancel", key=f"cancel_{signal.id}"):
                    # Remove signal from session state
                    st.session_state.forex_signals = [s for s in st.session_state.forex_signals if s.id != signal.id]
                    st.rerun()
    
    else:
        st.info("No active signals. Click 'Generate Signals' to create new forex trading opportunities.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_forex_news():
    """Display forex-related news."""
    st.markdown('<div class="forex-card">', unsafe_allow_html=True)
    st.subheader("📰 Forex Market News")
    
    # Placeholder for news - you could integrate with news APIs here
    news_items = [
        {
            'time': '14:30',
            'impact': 'High',
            'currency': 'USD',
            'event': 'Non-Farm Payrolls',
            'forecast': '180K',
            'previous': '175K'
        },
        {
            'time': '15:00',
            'impact': 'Medium',
            'currency': 'EUR',
            'event': 'ECB Interest Rate Decision',
            'forecast': '4.50%',
            'previous': '4.50%'
        },
        {
            'time': '16:30',
            'impact': 'Low',
            'currency': 'GBP',
            'event': 'UK Retail Sales',
            'forecast': '0.2%',
            'previous': '0.1%'
        }
    ]
    
    for news in news_items:
        impact_color = {
            'High': '#dc3545',
            'Medium': '#ffc107', 
            'Low': '#28a745'
        }.get(news['impact'], '#6c757d')
        
        st.markdown(f"""
        <div style="display: flex; align-items: center; padding: 0.5rem; margin: 0.25rem 0; 
                    background: white; border-radius: 6px; border-left: 3px solid {impact_color};">
            <div style="min-width: 60px; font-weight: bold;">{news['time']}</div>
            <div style="min-width: 40px; text-align: center; font-weight: bold; color: {impact_color};">
                {news['currency']}
            </div>
            <div style="flex: 1; margin-left: 1rem;">
                <strong>{news['event']}</strong><br>
                <small>Forecast: {news['forecast']} | Previous: {news['previous']}</small>
            </div>
            <div style="min-width: 60px; text-align: center; font-size: 0.8rem; 
                        color: {impact_color}; font-weight: bold;">
                {news['impact']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main app function."""
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0 1rem 0;">
        <h1 style="color: #343a40; margin-bottom: 0.5rem;">💱 Forex Sniper</h1>
        <p style="color: #6c757d; font-size: 1.1rem;">Simple & Clean Forex Trading Signals</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if forex bot is available
    if not FOREX_BOT_AVAILABLE:
        st.error("Forex bot not available. Please install dependencies.")
        st.code("pip install oandapyV20")
        return
    
    # Initialize bot
    bot, error = init_forex_bot()
    
    if error:
        st.warning("⚠️ OANDA Connection Required")
        st.info("""
        To use live forex data, you need:
        1. Free OANDA practice account: https://www.oanda.com/register/
        2. Set environment variables:
           - `OANDA_API_KEY`
           - `OANDA_ACCOUNT_ID`
        
        See `FOREX_SETUP_GUIDE.md` for detailed instructions.
        """)
        
        # Show demo mode
        st.markdown("---")
        st.subheader("🎮 Demo Mode")
        
        demo_signals = [
            {
                'pair': 'EUR/USD',
                'type': 'BUY',
                'entry': 1.08450,
                'target_pips': 30,
                'stop_pips': 15,
                'confidence': 0.75,
                'news': 'ECB hints at rate hike amid strong inflation data'
            },
            {
                'pair': 'GBP/USD',
                'type': 'SELL',
                'entry': 1.26820,
                'target_pips': 50,
                'stop_pips': 25,
                'confidence': 0.68,
                'news': 'UK GDP disappoints, BoE dovish stance expected'
            }
        ]
        
        for signal in demo_signals:
            signal_class = "buy-signal" if signal['type'] == "BUY" else "sell-signal"
            risk_reward = signal['target_pips'] / signal['stop_pips']
            
            st.markdown(f"""
            <div class="signal-card {signal_class}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{signal['pair']} {signal['type']}</strong><br>
                        <span class="price">Entry: {signal['entry']:.5f}</span><br>
                        <small>Target: +{signal['target_pips']} pips | Stop: -{signal['stop_pips']} pips | R/R: 1:{risk_reward:.1f}</small>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.1rem; font-weight: bold;">
                            {signal['confidence']:.1%}
                        </div>
                        <small>Confidence</small>
                    </div>
                </div>
                <div style="margin-top: 0.5rem; font-size: 0.9rem; color: #6c757d;">
                    📰 {signal['news']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        return
    
    # Main app with live data
    # Account info
    display_account_info(bot)
    
    # Live prices
    display_forex_prices(bot)
    
    # Trading signals
    display_forex_signals(bot)
    
    # Economic calendar/news
    display_forex_news()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6c757d; padding: 1rem;">
        <small>💡 Forex markets are open 24/5 | Always use proper risk management | Practice account recommended</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 