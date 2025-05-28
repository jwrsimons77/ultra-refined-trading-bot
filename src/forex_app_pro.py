#!/usr/bin/env python3
"""
Professional Forex Trading App
Beautiful, modern UI with clean design
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import os

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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Main container */
    .main-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* Header */
    .app-header {
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem 0;
    }
    
    .app-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .app-subtitle {
        font-size: 1.2rem;
        color: #6c757d;
        font-weight: 400;
    }
    
    /* Cards */
    .pro-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.3s ease;
    }
    
    .pro-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.12);
    }
    
    /* Price cards */
    .price-card {
        background: linear-gradient(135deg, #f8f9fa, #ffffff);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        border: 1px solid #e9ecef;
        transition: all 0.3s ease;
    }
    
    .price-card:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .currency-pair {
        font-size: 1.1rem;
        font-weight: 600;
        color: #495057;
        margin-bottom: 0.5rem;
    }
    
    .price-display {
        font-family: 'SF Mono', 'Monaco', 'Inconsolata', monospace;
        font-size: 1rem;
        font-weight: 500;
        color: #212529;
        margin-bottom: 0.3rem;
    }
    
    .spread-info {
        font-size: 0.85rem;
        color: #6c757d;
    }
    
    /* Signal cards */
    .signal-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.8rem 0;
        border-left: 4px solid;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .signal-card:hover {
        transform: translateX(4px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    .signal-buy {
        border-left-color: #28a745;
        background: linear-gradient(135deg, #ffffff, #f8fff9);
    }
    
    .signal-sell {
        border-left-color: #dc3545;
        background: linear-gradient(135deg, #ffffff, #fff8f8);
    }
    
    .signal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .signal-pair {
        font-size: 1.3rem;
        font-weight: 600;
        color: #212529;
    }
    
    .signal-type {
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .signal-buy-badge {
        background: #28a745;
        color: white;
    }
    
    .signal-sell-badge {
        background: #dc3545;
        color: white;
    }
    
    .signal-details {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .signal-metric {
        text-align: center;
    }
    
    .signal-metric-label {
        font-size: 0.8rem;
        color: #6c757d;
        text-transform: uppercase;
        font-weight: 500;
        margin-bottom: 0.2rem;
    }
    
    .signal-metric-value {
        font-size: 1.1rem;
        font-weight: 600;
        color: #212529;
    }
    
    .confidence-score {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 600;
        text-align: center;
        min-width: 80px;
    }
    
    /* Buttons */
    .pro-button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.7rem 1.5rem;
        font-weight: 500;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
        display: inline-block;
    }
    
    .pro-button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.7rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* Metrics */
    .metric-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        flex: 1;
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e9ecef;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #212529;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        font-weight: 500;
    }
    
    /* News section */
    .news-item {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .news-item:hover {
        transform: translateX(2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .news-high { border-left-color: #dc3545; }
    .news-medium { border-left-color: #ffc107; }
    .news-low { border-left-color: #28a745; }
    
    .news-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .news-time {
        font-weight: 600;
        color: #495057;
        min-width: 60px;
    }
    
    .news-currency {
        background: #f8f9fa;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
        min-width: 40px;
        text-align: center;
    }
    
    .news-impact {
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .impact-high { background: #dc3545; color: white; }
    .impact-medium { background: #ffc107; color: #212529; }
    .impact-low { background: #28a745; color: white; }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-container {
            margin: 0.5rem;
            padding: 1rem;
        }
        
        .app-title {
            font-size: 2rem;
        }
        
        .signal-details {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .metric-row {
            flex-direction: column;
        }
    }
</style>
""", unsafe_allow_html=True)

def create_demo_data():
    """Create professional demo data."""
    return {
        'prices': [
            {'pair': 'EUR/USD', 'bid': 1.08420, 'ask': 1.08435, 'spread': 1.5},
            {'pair': 'GBP/USD', 'bid': 1.26815, 'ask': 1.26832, 'spread': 1.7},
            {'pair': 'USD/JPY', 'bid': 149.842, 'ask': 149.856, 'spread': 1.4},
            {'pair': 'USD/CHF', 'bid': 0.89245, 'ask': 0.89258, 'spread': 1.3},
            {'pair': 'AUD/USD', 'bid': 0.66128, 'ask': 0.66142, 'spread': 1.4},
            {'pair': 'USD/CAD', 'bid': 1.39567, 'ask': 1.39582, 'spread': 1.5},
        ],
        'signals': [
            {
                'pair': 'EUR/USD',
                'type': 'BUY',
                'entry': 1.08435,
                'target': 1.08735,
                'stop': 1.08285,
                'target_pips': 30,
                'stop_pips': 15,
                'confidence': 0.78,
                'news': 'ECB officials signal potential rate hike amid persistent inflation concerns'
            },
            {
                'pair': 'GBP/USD',
                'type': 'SELL',
                'entry': 1.26815,
                'target': 1.26315,
                'stop': 1.27065,
                'target_pips': 50,
                'stop_pips': 25,
                'confidence': 0.72,
                'news': 'UK GDP growth disappoints, BoE dovish stance expected in upcoming meeting'
            },
            {
                'pair': 'USD/JPY',
                'type': 'BUY',
                'entry': 149.856,
                'target': 150.456,
                'stop': 149.456,
                'target_pips': 60,
                'stop_pips': 40,
                'confidence': 0.85,
                'news': 'Fed officials maintain hawkish rhetoric, supporting USD strength against JPY'
            }
        ],
        'news': [
            {'time': '14:30', 'currency': 'USD', 'event': 'Non-Farm Payrolls', 'impact': 'High', 'forecast': '185K', 'previous': '180K'},
            {'time': '15:00', 'currency': 'EUR', 'event': 'ECB Interest Rate Decision', 'impact': 'High', 'forecast': '4.50%', 'previous': '4.50%'},
            {'time': '16:30', 'currency': 'GBP', 'event': 'UK Retail Sales', 'impact': 'Medium', 'forecast': '0.3%', 'previous': '0.1%'},
            {'time': '18:00', 'currency': 'CAD', 'event': 'BoC Rate Statement', 'impact': 'Medium', 'forecast': '5.00%', 'previous': '5.00%'},
            {'time': '20:00', 'currency': 'AUD', 'event': 'RBA Meeting Minutes', 'impact': 'Low', 'forecast': '-', 'previous': '-'},
        ]
    }

def render_header():
    """Render professional header."""
    st.markdown("""
    <div class="app-header">
        <div class="app-title">💎 Forex Pro</div>
        <div class="app-subtitle">Professional Trading Signals & Market Analysis</div>
    </div>
    """, unsafe_allow_html=True)

def render_metrics():
    """Render key metrics."""
    st.markdown("""
    <div class="metric-row">
        <div class="metric-card">
            <div class="metric-value">$100,000</div>
            <div class="metric-label">Account Balance</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">+$2,450</div>
            <div class="metric-label">Today's P/L</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">5</div>
            <div class="metric-label">Active Signals</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">78%</div>
            <div class="metric-label">Win Rate</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_live_prices(data):
    """Render live forex prices."""
    st.markdown('<div class="pro-card">', unsafe_allow_html=True)
    st.markdown("### 💱 Live Market Prices")
    
    cols = st.columns(3)
    for i, price in enumerate(data['prices']):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="price-card">
                <div class="currency-pair">{price['pair']}</div>
                <div class="price-display">{price['bid']:.5f} / {price['ask']:.5f}</div>
                <div class="spread-info">Spread: {price['spread']} pips</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_trading_signals(data):
    """Render trading signals."""
    st.markdown('<div class="pro-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Premium Trading Signals")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        confidence_threshold = st.slider("Confidence Threshold", 0.1, 1.0, 0.7, 0.1, key="confidence_slider")
    with col2:
        if st.button("🔄 Refresh Signals", key="refresh_signals"):
            st.rerun()
    
    for signal in data['signals']:
        if signal['confidence'] >= confidence_threshold:
            signal_class = "signal-buy" if signal['type'] == "BUY" else "signal-sell"
            badge_class = "signal-buy-badge" if signal['type'] == "BUY" else "signal-sell-badge"
            risk_reward = signal['target_pips'] / signal['stop_pips']
            
            st.markdown(f"""
            <div class="signal-card {signal_class}">
                <div class="signal-header">
                    <div class="signal-pair">{signal['pair']}</div>
                    <div class="signal-type {badge_class}">{signal['type']}</div>
                </div>
                
                <div class="signal-details">
                    <div class="signal-metric">
                        <div class="signal-metric-label">Entry</div>
                        <div class="signal-metric-value">{signal['entry']:.5f}</div>
                    </div>
                    <div class="signal-metric">
                        <div class="signal-metric-label">Target</div>
                        <div class="signal-metric-value">+{signal['target_pips']} pips</div>
                    </div>
                    <div class="signal-metric">
                        <div class="signal-metric-label">Stop</div>
                        <div class="signal-metric-value">-{signal['stop_pips']} pips</div>
                    </div>
                    <div class="signal-metric">
                        <div class="signal-metric-label">R/R</div>
                        <div class="signal-metric-value">1:{risk_reward:.1f}</div>
                    </div>
                    <div class="signal-metric">
                        <div class="confidence-score">{signal['confidence']:.0%}</div>
                    </div>
                </div>
                
                <div style="font-size: 0.9rem; color: #6c757d; margin-bottom: 1rem;">
                    📰 {signal['news']}
                </div>
                
                <div style="display: flex; gap: 0.5rem;">
                    <button class="pro-button">📈 Execute Trade</button>
                    <button class="pro-button" style="background: #6c757d;">ℹ️ Details</button>
                    <button class="pro-button" style="background: #dc3545;">❌ Dismiss</button>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_economic_calendar(data):
    """Render economic calendar."""
    st.markdown('<div class="pro-card">', unsafe_allow_html=True)
    st.markdown("### 📅 Economic Calendar")
    
    for news in data['news']:
        impact_class = f"impact-{news['impact'].lower()}"
        news_class = f"news-{news['impact'].lower()}"
        
        st.markdown(f"""
        <div class="news-item {news_class}">
            <div class="news-header">
                <div class="news-time">{news['time']}</div>
                <div class="news-currency">{news['currency']}</div>
                <div class="news-impact {impact_class}">{news['impact']}</div>
                <div style="flex: 1; font-weight: 600;">{news['event']}</div>
            </div>
            <div style="font-size: 0.85rem; color: #6c757d;">
                Forecast: {news['forecast']} | Previous: {news['previous']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_footer():
    """Render footer."""
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; color: #6c757d;">
        <div style="margin-bottom: 1rem;">
            <strong>💎 Forex Pro</strong> - Professional Trading Platform
        </div>
        <div style="font-size: 0.9rem;">
            🌍 24/5 Markets • 📊 Real-time Analysis • 🔒 Secure Trading • 📱 Mobile Optimized
        </div>
        <div style="font-size: 0.8rem; margin-top: 0.5rem;">
            Risk Warning: Trading forex involves substantial risk and may not be suitable for all investors.
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application."""
    # Create main container
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Get demo data
    data = create_demo_data()
    
    # Render sections
    render_header()
    render_metrics()
    render_live_prices(data)
    render_trading_signals(data)
    render_economic_calendar(data)
    render_footer()
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main() 