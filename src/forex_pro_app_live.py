#!/usr/bin/env python3
"""
Professional Forex Trading App with Live OANDA Data
Beautiful, clean UI with real-time forex data from OANDA
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import random
import numpy as np
import requests
import json

# Import our new signal generator
try:
    from forex_signal_generator import ForexSignalGenerator
    SIGNAL_GENERATOR_AVAILABLE = True
except ImportError:
    SIGNAL_GENERATOR_AVAILABLE = False
    st.error("Signal generator not available")

# OANDA Configuration
OANDA_API_KEY = "fe92315bee29b117825fed529cf3fa99-173e927b8cdbb1fc244993e24e33fd93"
OANDA_ACCOUNT_ID = "101-004-31788297-001"
OANDA_ENVIRONMENT = "practice"
OANDA_BASE_URL = "https://api-fxpractice.oanda.com"

# Initialize signal generator
if SIGNAL_GENERATOR_AVAILABLE:
    signal_generator = ForexSignalGenerator(oanda_api_key=OANDA_API_KEY)

# Page config
st.set_page_config(
    page_title="Forex Pro Live",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional CSS styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom header */
    .forex-header {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
    }
    
    .forex-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .forex-subtitle {
        font-size: 1.2rem;
        color: #6b7280;
        font-weight: 400;
    }
    
    /* Currency pair cards */
    .currency-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.3);
        transition: all 0.3s ease;
    }
    
    .currency-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
    }
    
    .currency-pair {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    
    .currency-price {
        font-size: 2rem;
        font-weight: 700;
        color: #059669;
        margin-bottom: 0.5rem;
    }
    
    .currency-change {
        font-size: 1rem;
        font-weight: 500;
    }
    
    .positive { color: #059669; }
    .negative { color: #dc2626; }
    
    /* Signal cards */
    .signal-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border-left: 4px solid;
        transition: all 0.3s ease;
    }
    
    .signal-buy {
        border-left-color: #059669;
        background: linear-gradient(135deg, rgba(5, 150, 105, 0.05) 0%, rgba(255, 255, 255, 0.95) 100%);
    }
    
    .signal-sell {
        border-left-color: #dc2626;
        background: linear-gradient(135deg, rgba(220, 38, 38, 0.05) 0%, rgba(255, 255, 255, 0.95) 100%);
    }
    
    .signal-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
    }
    
    .signal-type {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .signal-pair {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 1rem;
    }
    
    .signal-details {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .signal-detail {
        text-align: center;
        padding: 0.5rem;
        background: rgba(255, 255, 255, 0.5);
        border-radius: 8px;
    }
    
    .signal-detail-label {
        font-size: 0.8rem;
        color: #6b7280;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .signal-detail-value {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1f2937;
        margin-top: 0.2rem;
    }
    
    /* Status indicators */
    .status-connected {
        color: #059669;
        font-weight: 600;
    }
    
    .status-disconnected {
        color: #dc2626;
        font-weight: 600;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Metrics */
    .metric-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 1rem;
        color: #6b7280;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 16px;
        padding: 0.5rem;
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 12px;
        color: #6b7280;
        font-weight: 600;
        padding: 1rem 2rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=30)  # Cache for 30 seconds
def get_oanda_prices():
    """Get live forex prices from OANDA."""
    try:
        headers = {
            "Authorization": f"Bearer {OANDA_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Major forex pairs
        instruments = "EUR_USD,GBP_USD,USD_JPY,USD_CHF,AUD_USD,USD_CAD"
        url = f"{OANDA_BASE_URL}/v3/accounts/{OANDA_ACCOUNT_ID}/pricing"
        params = {"instruments": instruments}
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            prices = {}
            
            for price in data.get('prices', []):
                instrument = price['instrument']
                bid = float(price['bids'][0]['price'])
                ask = float(price['asks'][0]['price'])
                mid = (bid + ask) / 2
                spread = ask - bid
                
                # Convert instrument name for display
                pair_name = instrument.replace('_', '/')
                
                prices[pair_name] = {
                    'price': mid,
                    'bid': bid,
                    'ask': ask,
                    'spread': spread,
                    'change': random.uniform(-0.01, 0.01),  # Simulated change for demo
                    'change_pct': random.uniform(-1.0, 1.0)  # Simulated percentage change
                }
            
            return prices, True
        else:
            return None, False
            
    except Exception as e:
        st.error(f"Error fetching OANDA prices: {str(e)}")
        return None, False

@st.cache_data(ttl=60)  # Cache for 60 seconds
def get_account_info():
    """Get OANDA account information."""
    try:
        headers = {
            "Authorization": f"Bearer {OANDA_API_KEY}",
            "Content-Type": "application/json"
        }
        
        url = f"{OANDA_BASE_URL}/v3/accounts/{OANDA_ACCOUNT_ID}/summary"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            account = data.get('account', {})
            return {
                'balance': float(account.get('balance', 0)),
                'nav': float(account.get('NAV', 0)),
                'margin_used': float(account.get('marginUsed', 0)),
                'margin_available': float(account.get('marginAvailable', 0)),
                'currency': account.get('currency', 'USD'),
                'open_trades': account.get('openTradeCount', 0),
                'open_positions': account.get('openPositionCount', 0)
            }, True
        else:
            return None, False
            
    except Exception as e:
        st.error(f"Error fetching account info: {str(e)}")
        return None, False

# Replace the DEMO_SIGNALS with a function to get live signals
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_live_forex_signals():
    """Get live forex signals from the signal generator."""
    if not SIGNAL_GENERATOR_AVAILABLE:
        # Fallback demo signals
        return [
            {
                'pair': 'EUR/USD',
                'type': 'BUY',
                'entry': 1.0847,
                'target': 1.0920,
                'stop_loss': 1.0780,
                'confidence': 0.85,
                'pips_target': 73,
                'risk_reward': '1:2.1',
                'reason': 'Demo signal - ECB hawkish stance'
            }
        ]
    
    try:
        # Get real signals from generator
        signals = signal_generator.generate_forex_signals(max_signals=5, min_confidence=0.25)
        
        # Convert to dict format for compatibility
        signal_dicts = []
        for signal in signals:
            signal_dicts.append({
                'pair': signal.pair,
                'type': signal.signal_type,
                'entry': signal.entry_price,
                'target': signal.target_price,
                'stop_loss': signal.stop_loss,
                'confidence': signal.confidence,
                'pips_target': signal.pips_target,
                'risk_reward': signal.risk_reward_ratio,
                'reason': signal.reason,
                'news_sentiment': signal.news_sentiment,
                'technical_score': signal.technical_score
            })
        
        return signal_dicts
        
    except Exception as e:
        st.error(f"Error generating signals: {e}")
        return []

def render_header():
    """Render the main header with connection status."""
    # Test connection
    _, oanda_connected = get_oanda_prices()
    _, account_connected = get_account_info()
    
    connection_status = "🟢 Connected" if (oanda_connected and account_connected) else "🔴 Disconnected"
    status_class = "status-connected" if (oanda_connected and account_connected) else "status-disconnected"
    
    st.markdown(f"""
    <div class="forex-header">
        <div class="forex-title">💎 Forex Pro Live</div>
        <div class="forex-subtitle">Professional Forex Trading with Live OANDA Data</div>
        <div style="margin-top: 1rem;">
            <span class="{status_class}">OANDA API: {connection_status}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_live_currency_pairs():
    """Render live currency pair prices from OANDA."""
    st.markdown("### 📈 Live Currency Pairs (OANDA)")
    
    prices, connected = get_oanda_prices()
    
    if connected and prices:
        cols = st.columns(3)
        
        for i, (pair, data) in enumerate(prices.items()):
            with cols[i % 3]:
                change_class = "positive" if data['change'] > 0 else "negative"
                change_symbol = "+" if data['change'] > 0 else ""
                
                st.markdown(f"""
                <div class="currency-card">
                    <div class="currency-pair">{pair}</div>
                    <div class="currency-price">{data['price']:.5f}</div>
                    <div class="currency-change {change_class}">
                        Spread: {data['spread']:.5f} | Bid: {data['bid']:.5f} | Ask: {data['ask']:.5f}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.error("❌ Unable to fetch live prices from OANDA. Using demo mode.")
        # Fallback to demo data
        render_demo_currency_pairs()

def render_demo_currency_pairs():
    """Render demo currency pairs as fallback."""
    demo_pairs = {
        'EUR/USD': {'price': 1.0847, 'change': 0.0023, 'change_pct': 0.21},
        'GBP/USD': {'price': 1.2634, 'change': -0.0045, 'change_pct': -0.35},
        'USD/JPY': {'price': 149.82, 'change': 0.67, 'change_pct': 0.45},
        'USD/CHF': {'price': 0.8923, 'change': 0.0012, 'change_pct': 0.13},
        'AUD/USD': {'price': 0.6587, 'change': -0.0021, 'change_pct': -0.32},
        'USD/CAD': {'price': 1.3745, 'change': 0.0034, 'change_pct': 0.25},
    }
    
    cols = st.columns(3)
    
    for i, (pair, data) in enumerate(demo_pairs.items()):
        with cols[i % 3]:
            change_class = "positive" if data['change'] > 0 else "negative"
            change_symbol = "+" if data['change'] > 0 else ""
            
            st.markdown(f"""
            <div class="currency-card">
                <div class="currency-pair">{pair} (Demo)</div>
                <div class="currency-price">{data['price']:.4f}</div>
                <div class="currency-change {change_class}">
                    {change_symbol}{data['change']:.4f} ({change_symbol}{data['change_pct']:.2f}%)
                </div>
            </div>
            """, unsafe_allow_html=True)

def render_account_info():
    """Render OANDA account information."""
    st.markdown("### 💰 Account Information")
    
    account_info, connected = get_account_info()
    
    if connected and account_info:
        cols = st.columns(4)
        
        metrics = [
            {"label": "Balance", "value": f"{account_info['balance']:.2f} {account_info['currency']}", "color": "#059669"},
            {"label": "NAV", "value": f"{account_info['nav']:.2f} {account_info['currency']}", "color": "#667eea"},
            {"label": "Margin Available", "value": f"{account_info['margin_available']:.2f} {account_info['currency']}", "color": "#059669"},
            {"label": "Open Trades", "value": str(account_info['open_trades']), "color": "#f59e0b"}
        ]
        
        for i, metric in enumerate(metrics):
            with cols[i]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: {metric['color']};">{metric['value']}</div>
                    <div class="metric-label">{metric['label']}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.error("❌ Unable to fetch account information from OANDA.")

def render_trading_signals():
    """Render live trading signals."""
    st.markdown("### 🎯 Live Trading Signals")
    
    # Get live signals
    signals = get_live_forex_signals()
    
    if not signals:
        st.warning("⚠️ No signals generated at this time. Market conditions may not meet criteria.")
        return
    
    st.success(f"✅ Generated {len(signals)} live trading signals")
    
    for i, signal in enumerate(signals):
        # Use Streamlit columns for better layout
        with st.container():
            # Signal header
            signal_emoji = "🟢" if signal['type'] == 'BUY' else "🔴"
            st.markdown(f"## {signal_emoji} {signal['type']} {signal['pair']}")
            
            # Main signal info in columns
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Entry Price", f"{signal['entry']:.5f}")
                st.metric("Confidence", f"{signal['confidence']:.0%}")
            
            with col2:
                st.metric("Target", f"{signal['target']:.5f}")
                st.metric("Pips Target", f"{signal['pips_target']}")
            
            with col3:
                st.metric("Stop Loss", f"{signal['stop_loss']:.5f}")
                st.metric("Risk:Reward", signal['risk_reward'])
            
            # Additional info
            if 'news_sentiment' in signal and 'technical_score' in signal:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("News Sentiment", f"{signal['news_sentiment']:.2f}")
                with col2:
                    st.metric("Technical Score", f"{signal['technical_score']:.2f}")
            
            # Analysis reason
            st.info(f"**Analysis:** {signal['reason']}")
            
            # Add some spacing
            st.markdown("---")

def render_price_chart():
    """Render a sample price chart with live data if available."""
    st.markdown("### 📈 EUR/USD Live Chart")
    
    prices, connected = get_oanda_prices()
    
    if connected and prices and 'EUR/USD' in prices:
        current_price = prices['EUR/USD']['price']
        st.success(f"🟢 Live Price: {current_price:.5f}")
    else:
        current_price = 1.0847
        st.warning("📊 Demo Chart (Live data unavailable)")
    
    # Generate sample data around current price
    dates = pd.date_range(start=datetime.now() - timedelta(days=7), end=datetime.now(), freq='h')
    prices_data = []
    base_price = current_price - 0.01
    
    for i in range(len(dates)):
        price = base_price + np.random.normal(0, 0.002) + 0.0001 * np.sin(i * 0.1)
        prices_data.append(price)
        base_price = price * 0.999 + current_price * 0.001  # Drift towards current price
    
    df = pd.DataFrame({'Date': dates, 'Price': prices_data})
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Price'],
        mode='lines',
        name='EUR/USD',
        line=dict(color='#667eea', width=2)
    ))
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#1f2937'),
        xaxis=dict(gridcolor='rgba(107, 114, 128, 0.2)'),
        yaxis=dict(gridcolor='rgba(107, 114, 128, 0.2)'),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def main():
    """Main app function."""
    render_header()
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 Dashboard", "💱 Live Prices", "🎯 Signals", "📊 Analytics"])
    
    with tab1:
        st.markdown("### 🌟 Welcome to Forex Pro Live")
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.9); padding: 2rem; border-radius: 16px; margin: 1rem 0;">
            <h4 style="color: #1f2937; margin-bottom: 1rem;">Live OANDA Integration</h4>
            <p style="color: #6b7280; font-size: 1.1rem; line-height: 1.6;">
                Connected to your OANDA practice account for real-time forex data, live pricing, 
                and account information. Experience professional forex trading with live market data.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        render_account_info()
        render_trading_signals()
    
    with tab2:
        render_live_currency_pairs()
        render_price_chart()
    
    with tab3:
        render_trading_signals()
        
        st.markdown("### ⚙️ Signal Settings")
        col1, col2 = st.columns(2)
        
        with col1:
            confidence_threshold = st.slider("Minimum Confidence", 0.2, 0.9, 0.25, 0.05, key="confidence_slider")
            max_signals = st.slider("Max Signals", 1, 10, 5, key="max_signals_slider")
        
        with col2:
            risk_level = st.selectbox("Risk Level", ["Conservative", "Moderate", "Aggressive"], key="risk_level_select")
            auto_refresh = st.checkbox("Auto Refresh (5 min)", value=True, key="auto_refresh_checkbox")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Refresh Signals", key="refresh_signals_button"):
                # Clear cache to force refresh
                get_live_forex_signals.clear()
                st.success("✅ Signals refreshed!")
                st.rerun()
        
        with col2:
            if st.button("📊 Generate New Analysis", key="new_analysis_button"):
                if SIGNAL_GENERATOR_AVAILABLE:
                    with st.spinner("Analyzing markets..."):
                        new_signals = signal_generator.generate_forex_signals(
                            max_signals=max_signals, 
                            min_confidence=confidence_threshold
                        )
                    st.success(f"Generated {len(new_signals)} new signals!")
                else:
                    st.error("Signal generator not available")
        
        with col3:
            if st.button("💾 Export Signals", key="export_signals_button"):
                signals = get_live_forex_signals()
                if signals:
                    # Convert to DataFrame for export
                    df = pd.DataFrame(signals)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"forex_signals_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No signals to export")
    
    with tab4:
        render_account_info()
        
        st.markdown("### 📈 Trading Performance")
        
        # Sample performance data
        performance_data = {
            'Date': pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D'),
            'Profit': np.cumsum(np.random.normal(50, 100, 31))
        }
        
        df_perf = pd.DataFrame(performance_data)
        
        fig = px.line(df_perf, x='Date', y='Profit', title='Cumulative Profit (GBP)')
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#1f2937')
        )
        
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main() 