#!/usr/bin/env python3
"""
Professional Forex Trading App
Beautiful, clean UI with light colors and professional design
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import random
import numpy as np

# Page config
st.set_page_config(
    page_title="Forex Pro",
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

# Demo data for forex pairs
FOREX_PAIRS = {
    'EUR/USD': {'price': 1.0847, 'change': 0.0023, 'change_pct': 0.21},
    'GBP/USD': {'price': 1.2634, 'change': -0.0045, 'change_pct': -0.35},
    'USD/JPY': {'price': 149.82, 'change': 0.67, 'change_pct': 0.45},
    'USD/CHF': {'price': 0.8923, 'change': 0.0012, 'change_pct': 0.13},
    'AUD/USD': {'price': 0.6587, 'change': -0.0021, 'change_pct': -0.32},
    'USD/CAD': {'price': 1.3745, 'change': 0.0034, 'change_pct': 0.25},
}

# Demo signals
DEMO_SIGNALS = [
    {
        'pair': 'EUR/USD',
        'type': 'BUY',
        'entry': 1.0847,
        'target': 1.0920,
        'stop_loss': 1.0780,
        'confidence': 0.85,
        'pips_target': 73,
        'risk_reward': '1:2.1'
    },
    {
        'pair': 'GBP/USD',
        'type': 'SELL',
        'entry': 1.2634,
        'target': 1.2560,
        'stop_loss': 1.2700,
        'confidence': 0.78,
        'pips_target': 74,
        'risk_reward': '1:1.9'
    },
    {
        'pair': 'USD/JPY',
        'type': 'BUY',
        'entry': 149.82,
        'target': 150.50,
        'stop_loss': 149.20,
        'confidence': 0.72,
        'pips_target': 68,
        'risk_reward': '1:1.8'
    }
]

def render_header():
    """Render the main header"""
    st.markdown("""
    <div class="forex-header">
        <div class="forex-title">💎 Forex Pro</div>
        <div class="forex-subtitle">Professional Forex Trading Signals</div>
    </div>
    """, unsafe_allow_html=True)

def render_currency_pairs():
    """Render live currency pair prices"""
    st.markdown("### 📈 Live Currency Pairs")
    
    cols = st.columns(3)
    
    for i, (pair, data) in enumerate(FOREX_PAIRS.items()):
        with cols[i % 3]:
            change_class = "positive" if data['change'] > 0 else "negative"
            change_symbol = "+" if data['change'] > 0 else ""
            
            st.markdown(f"""
            <div class="currency-card">
                <div class="currency-pair">{pair}</div>
                <div class="currency-price">{data['price']:.4f}</div>
                <div class="currency-change {change_class}">
                    {change_symbol}{data['change']:.4f} ({change_symbol}{data['change_pct']:.2f}%)
                </div>
            </div>
            """, unsafe_allow_html=True)

def render_trading_signals():
    """Render trading signals"""
    st.markdown("### 🎯 Active Trading Signals")
    
    for signal in DEMO_SIGNALS:
        signal_class = "signal-buy" if signal['type'] == 'BUY' else "signal-sell"
        type_color = "#059669" if signal['type'] == 'BUY' else "#dc2626"
        
        st.markdown(f"""
        <div class="signal-card {signal_class}">
            <div class="signal-type" style="color: {type_color};">{signal['type']} SIGNAL</div>
            <div class="signal-pair">{signal['pair']}</div>
            
            <div class="signal-details">
                <div class="signal-detail">
                    <div class="signal-detail-label">Entry Price</div>
                    <div class="signal-detail-value">{signal['entry']:.4f}</div>
                </div>
                <div class="signal-detail">
                    <div class="signal-detail-label">Target</div>
                    <div class="signal-detail-value">{signal['target']:.4f}</div>
                </div>
                <div class="signal-detail">
                    <div class="signal-detail-label">Stop Loss</div>
                    <div class="signal-detail-value">{signal['stop_loss']:.4f}</div>
                </div>
                <div class="signal-detail">
                    <div class="signal-detail-label">Confidence</div>
                    <div class="signal-detail-value">{signal['confidence']:.0%}</div>
                </div>
                <div class="signal-detail">
                    <div class="signal-detail-label">Pips Target</div>
                    <div class="signal-detail-value">{signal['pips_target']}</div>
                </div>
                <div class="signal-detail">
                    <div class="signal-detail-label">Risk:Reward</div>
                    <div class="signal-detail-value">{signal['risk_reward']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_performance_metrics():
    """Render performance metrics"""
    st.markdown("### 📊 Performance Metrics")
    
    cols = st.columns(4)
    
    metrics = [
        {"label": "Win Rate", "value": "73%", "color": "#059669"},
        {"label": "Total Signals", "value": "127", "color": "#667eea"},
        {"label": "Avg Pips", "value": "+68", "color": "#059669"},
        {"label": "Risk Score", "value": "Low", "color": "#f59e0b"}
    ]
    
    for i, metric in enumerate(metrics):
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {metric['color']};">{metric['value']}</div>
                <div class="metric-label">{metric['label']}</div>
            </div>
            """, unsafe_allow_html=True)

def render_price_chart():
    """Render a sample price chart"""
    st.markdown("### 📈 EUR/USD Price Chart")
    
    # Generate sample data
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='H')
    prices = []
    base_price = 1.0800
    
    for i in range(len(dates)):
        price = base_price + np.random.normal(0, 0.002) + 0.0001 * np.sin(i * 0.1)
        prices.append(price)
        base_price = price
    
    df = pd.DataFrame({'Date': dates, 'Price': prices})
    
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
    """Main app function"""
    render_header()
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 Dashboard", "💱 Live Prices", "🎯 Signals", "📊 Analytics"])
    
    with tab1:
        st.markdown("### 🌟 Welcome to Forex Pro")
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.9); padding: 2rem; border-radius: 16px; margin: 1rem 0;">
            <h4 style="color: #1f2937; margin-bottom: 1rem;">Professional Forex Trading Platform</h4>
            <p style="color: #6b7280; font-size: 1.1rem; line-height: 1.6;">
                Get real-time forex signals powered by AI analysis of market news and technical indicators. 
                Our advanced algorithms analyze multiple data sources to provide high-confidence trading opportunities.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        render_performance_metrics()
        render_trading_signals()
    
    with tab2:
        render_currency_pairs()
        render_price_chart()
    
    with tab3:
        render_trading_signals()
        
        st.markdown("### ⚙️ Signal Settings")
        col1, col2 = st.columns(2)
        
        with col1:
            confidence_threshold = st.slider("Minimum Confidence", 0.5, 1.0, 0.7, 0.05)
            max_signals = st.slider("Max Daily Signals", 1, 10, 5)
        
        with col2:
            risk_level = st.selectbox("Risk Level", ["Low", "Medium", "High"])
            auto_trade = st.checkbox("Enable Auto Trading")
        
        if st.button("🔄 Refresh Signals"):
            st.success("Signals refreshed! New opportunities detected.")
    
    with tab4:
        render_performance_metrics()
        
        st.markdown("### 📈 Trading Performance")
        
        # Sample performance data
        performance_data = {
            'Date': pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D'),
            'Profit': np.cumsum(np.random.normal(50, 100, 31))
        }
        
        df_perf = pd.DataFrame(performance_data)
        
        fig = px.line(df_perf, x='Date', y='Profit', title='Cumulative Profit (USD)')
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#1f2937')
        )
        
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main() 