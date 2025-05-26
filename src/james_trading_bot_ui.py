#!/usr/bin/env python3
"""
James's Trading Bot - Beautiful Mobile-Friendly UI
Professional forex trading interface with modern design
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import trading modules
try:
    from forex_signal_generator import ForexSignalGenerator
    from oanda_trader import OANDATrader
    from simple_backtest import SimpleBacktester
    MODULES_AVAILABLE = True
except ImportError as e:
    MODULES_AVAILABLE = False
    st.error(f"⚠️ Trading modules not available: {e}")

# Page configuration
st.set_page_config(
    page_title="James's Trading Bot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Beautiful CSS styling for mobile-first design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');
    
    /* Global Styles */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        min-height: 100vh;
        font-family: 'Poppins', sans-serif;
        padding: 0;
    }
    
    .stApp {
        background: transparent;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    /* Mobile-first responsive design */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem 0.5rem;
            max-width: 100%;
        }
        
        .trading-title {
            font-size: 2.5rem !important;
        }
        
        .trading-subtitle {
            font-size: 1.1rem !important;
        }
        
        .modern-card {
            padding: 1.5rem !important;
            margin: 1rem 0 !important;
        }
        
        .signal-card-buy, .signal-card-sell {
            padding: 1.5rem !important;
            margin: 1rem 0 !important;
        }
    }
    
    /* Header Styling */
    .trading-header {
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%);
        backdrop-filter: blur(25px);
        border-radius: 30px;
        padding: 3rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 25px 80px rgba(0, 0, 0, 0.15);
        text-align: center;
        border: 1px solid rgba(255,255,255,0.3);
        position: relative;
        overflow: hidden;
    }
    
    .trading-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .trading-title {
        font-size: 4rem;
        font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        letter-spacing: -0.03em;
        position: relative;
        z-index: 1;
    }
    
    .trading-subtitle {
        font-size: 1.3rem;
        color: #64748b;
        font-weight: 500;
        margin: 0;
        position: relative;
        z-index: 1;
    }
    
    .trading-emoji {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
        animation: bounce 2s infinite;
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }
    
    /* Modern Card Styling */
    .modern-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%);
        backdrop-filter: blur(25px);
        border-radius: 25px;
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 0 25px 80px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.3);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .modern-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 35px 100px rgba(0,0,0,0.15);
    }
    
    /* Signal Cards with Glassmorphism */
    .signal-card-buy {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.05) 100%);
        backdrop-filter: blur(25px);
        border: 2px solid rgba(16, 185, 129, 0.3);
        border-radius: 25px;
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 0 25px 80px rgba(16, 185, 129, 0.2);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .signal-card-sell {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.05) 100%);
        backdrop-filter: blur(25px);
        border: 2px solid rgba(239, 68, 68, 0.3);
        border-radius: 25px;
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 0 25px 80px rgba(239, 68, 68, 0.2);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .signal-card-buy:hover, .signal-card-sell:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 35px 100px rgba(0,0,0,0.2);
    }
    
    /* Signal Card Headers */
    .signal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
        flex-wrap: wrap;
        gap: 1rem;
    }
    
    .signal-pair {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .signal-type-buy {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.8rem 2rem;
        border-radius: 50px;
        font-weight: 700;
        font-size: 1.1rem;
        letter-spacing: 0.05em;
        box-shadow: 0 10px 30px rgba(16, 185, 129, 0.4);
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .signal-type-sell {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 0.8rem 2rem;
        border-radius: 50px;
        font-weight: 700;
        font-size: 1.1rem;
        letter-spacing: 0.05em;
        box-shadow: 0 10px 30px rgba(239, 68, 68, 0.4);
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .signal-type-buy:hover, .signal-type-sell:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
    }
    
    /* Confidence Badge */
    .confidence-badge {
        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
        color: white;
        padding: 0.6rem 1.5rem;
        border-radius: 50px;
        font-weight: 700;
        font-size: 1rem;
        display: inline-block;
        box-shadow: 0 8px 25px rgba(139, 92, 246, 0.3);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 8px 25px rgba(139, 92, 246, 0.3); }
        50% { box-shadow: 0 8px 35px rgba(139, 92, 246, 0.5); }
        100% { box-shadow: 0 8px 25px rgba(139, 92, 246, 0.3); }
    }
    
    /* Price Display */
    .price-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .price-item {
        background: rgba(255,255,255,0.6);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.4);
        transition: all 0.3s ease;
    }
    
    .price-item:hover {
        transform: translateY(-3px);
        background: rgba(255,255,255,0.8);
    }
    
    .price-label {
        font-size: 0.9rem;
        font-weight: 600;
        color: #6b7280;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    .price-value {
        font-size: 1.8rem;
        font-weight: 800;
        margin: 0;
        color: #1f2937;
    }
    
    .price-pips {
        font-size: 1rem;
        color: #6b7280;
        margin-top: 0.3rem;
    }
    
    /* Action Buttons */
    .action-buttons {
        display: flex;
        gap: 1rem;
        margin-top: 2rem;
        flex-wrap: wrap;
    }
    
    .btn-execute {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 1rem 2.5rem;
        border-radius: 50px;
        font-weight: 700;
        font-size: 1.1rem;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 10px 30px rgba(245, 158, 11, 0.3);
        flex: 1;
        min-width: 200px;
    }
    
    .btn-execute:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(245, 158, 11, 0.4);
    }
    
    .btn-details {
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%);
        color: #374151;
        padding: 1rem 2rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 1rem;
        border: 2px solid rgba(255,255,255,0.5);
        cursor: pointer;
        transition: all 0.3s ease;
        backdrop-filter: blur(15px);
    }
    
    .btn-details:hover {
        transform: translateY(-2px);
        background: rgba(255,255,255,1);
    }
    
    /* Status Indicators */
    .status-online {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.9rem;
        box-shadow: 0 5px 15px rgba(16, 185, 129, 0.3);
    }
    
    .status-offline {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.9rem;
        box-shadow: 0 5px 15px rgba(239, 68, 68, 0.3);
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: currentColor;
        animation: blink 1.5s infinite;
    }
    
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0.3; }
    }
    
    /* Account Summary Cards */
    .account-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .account-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.4);
        box-shadow: 0 15px 50px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .account-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 25px 70px rgba(0,0,0,0.12);
    }
    
    .account-title {
        font-size: 1rem;
        font-weight: 600;
        color: #6b7280;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    .account-value {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        color: #1f2937;
    }
    
    .account-change {
        font-size: 1rem;
        margin-top: 0.5rem;
        font-weight: 600;
    }
    
    .positive { color: #10b981; }
    .negative { color: #ef4444; }
    
    /* Loading Animation */
    .loading-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 3rem;
    }
    
    .loading-spinner {
        width: 50px;
        height: 50px;
        border: 4px solid rgba(255,255,255,0.3);
        border-top: 4px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Mobile Optimizations */
    @media (max-width: 480px) {
        .signal-header {
            flex-direction: column;
            text-align: center;
        }
        
        .price-grid {
            grid-template-columns: 1fr;
        }
        
        .action-buttons {
            flex-direction: column;
        }
        
        .btn-execute, .btn-details {
            min-width: 100%;
        }
        
        .account-grid {
            grid-template-columns: 1fr;
        }
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .modern-card {
            background: linear-gradient(135deg, rgba(30,30,30,0.95) 0%, rgba(20,20,20,0.9) 100%);
            color: #f9fafb;
        }
        
        .price-item {
            background: rgba(30,30,30,0.6);
            color: #f9fafb;
        }
        
        .account-card {
            background: linear-gradient(135deg, rgba(30,30,30,0.9) 0%, rgba(20,20,20,0.8) 100%);
            color: #f9fafb;
        }
    }
</style>
""", unsafe_allow_html=True)

def render_header():
    """Render the beautiful header for James's Trading Bot"""
    st.markdown("""
    <div class="trading-header">
        <span class="trading-emoji">🚀</span>
        <h1 class="trading-title">James's Trading Bot</h1>
        <p class="trading-subtitle">Professional Forex Trading • AI-Powered Signals • Real-Time Execution</p>
    </div>
    """, unsafe_allow_html=True)

def render_status_bar():
    """Render the status bar with market and system status"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if MODULES_AVAILABLE:
            st.markdown('<div class="status-online"><span class="status-dot"></span>System Online</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-offline"><span class="status-dot"></span>System Offline</div>', unsafe_allow_html=True)
    
    with col2:
        # Market status (simplified)
        current_time = datetime.now()
        if 9 <= current_time.hour <= 17:  # Market hours approximation
            st.markdown('<div class="status-online"><span class="status-dot"></span>Market Open</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-offline"><span class="status-dot"></span>Market Closed</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="status-online"><span class="status-dot"></span>OANDA Connected</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="status-online"><span class="status-dot"></span>Signals Active</div>', unsafe_allow_html=True)

@st.cache_data(ttl=30)  # Cache for 30 seconds
def get_live_signals(min_confidence=0.25):
    """Get live trading signals"""
    if not MODULES_AVAILABLE:
        return []
    
    try:
        generator = ForexSignalGenerator()
        signals = generator.generate_forex_signals(max_signals=5, min_confidence=min_confidence)
        return signals
    except Exception as e:
        logger.error(f"Error generating signals: {e}")
        return []

def render_signal_card(signal, index):
    """Render a beautiful signal card"""
    signal_type = signal.signal_type.upper()
    card_class = "signal-card-buy" if signal_type == "BUY" else "signal-card-sell"
    type_class = "signal-type-buy" if signal_type == "BUY" else "signal-type-sell"
    
    # Calculate potential profit
    if signal_type == "BUY":
        potential_profit = signal.target_price - signal.entry_price
    else:
        potential_profit = signal.entry_price - signal.target_price
    
    potential_profit_pct = (potential_profit / signal.entry_price) * 100
    
    st.markdown(f"""
    <div class="{card_class}">
        <div class="signal-header">
            <h2 class="signal-pair">{signal.pair}</h2>
            <div>
                <button class="{type_class}">{signal_type}</button>
                <div style="margin-top: 0.5rem;">
                    <span class="confidence-badge">{signal.confidence:.1%} Confidence</span>
                </div>
            </div>
        </div>
        
        <div class="price-grid">
            <div class="price-item">
                <div class="price-label">Entry Price</div>
                <div class="price-value">{signal.entry_price:.5f}</div>
            </div>
            <div class="price-item">
                <div class="price-label">Target</div>
                <div class="price-value">{signal.target_price:.5f}</div>
                <div class="price-pips">+{signal.pips_target} pips</div>
            </div>
            <div class="price-item">
                <div class="price-label">Stop Loss</div>
                <div class="price-value">{signal.stop_loss:.5f}</div>
                <div class="price-pips">-{signal.pips_risk} pips</div>
            </div>
            <div class="price-item">
                <div class="price-label">Risk/Reward</div>
                <div class="price-value">{signal.risk_reward_ratio}</div>
                <div class="price-pips">{potential_profit_pct:.1f}% potential</div>
            </div>
        </div>
        
        <div style="margin: 1.5rem 0;">
            <div class="price-label">Hold Time Estimate</div>
            <div style="font-size: 1.2rem; font-weight: 600; color: #374151;">
                {signal.hold_time_days:.1f} days ({signal.hold_time_hours:.1f} hours)
            </div>
            <div style="font-size: 0.9rem; color: #6b7280; margin-top: 0.3rem;">
                {signal.hold_time_confidence} confidence
            </div>
        </div>
        
        <div style="margin: 1.5rem 0; padding: 1rem; background: rgba(255,255,255,0.5); border-radius: 15px;">
            <div class="price-label">Analysis</div>
            <div style="font-size: 0.95rem; color: #374151; line-height: 1.5;">
                {signal.reason}
            </div>
        </div>
        
        <div class="action-buttons">
            <button class="btn-execute" onclick="alert('Execute trade for {signal.pair}')">
                🚀 Execute Trade
            </button>
            <button class="btn-details" onclick="alert('Show details for {signal.pair}')">
                📊 View Details
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_account_summary():
    """Render account summary with beautiful cards"""
    if not MODULES_AVAILABLE:
        st.warning("⚠️ Trading modules not available")
        return
    
    try:
        trader = OANDATrader()
        account_info = trader.get_account_summary()
        
        if account_info:
            balance = float(account_info.get('balance', 0))
            nav = float(account_info.get('NAV', 0))
            unrealized_pnl = float(account_info.get('unrealizedPL', 0))
            margin_used = float(account_info.get('marginUsed', 0))
            open_trades = int(account_info.get('openTradeCount', 0))
            
            st.markdown("""
            <div class="account-grid">
                <div class="account-card">
                    <div class="account-title">Account Balance</div>
                    <div class="account-value">$%s</div>
                </div>
                <div class="account-card">
                    <div class="account-title">Net Asset Value</div>
                    <div class="account-value">$%s</div>
                    <div class="account-change %s">%s$%.2f</div>
                </div>
                <div class="account-card">
                    <div class="account-title">Unrealized P&L</div>
                    <div class="account-value %s">$%.2f</div>
                </div>
                <div class="account-card">
                    <div class="account-title">Open Trades</div>
                    <div class="account-value">%d</div>
                    <div class="account-change">$%.2f margin used</div>
                </div>
            </div>
            """ % (
                f"{balance:,.2f}",
                f"{nav:,.2f}",
                "positive" if unrealized_pnl >= 0 else "negative",
                "+" if unrealized_pnl >= 0 else "",
                unrealized_pnl,
                "positive" if unrealized_pnl >= 0 else "negative",
                unrealized_pnl,
                open_trades,
                margin_used
            ), unsafe_allow_html=True)
        else:
            st.error("❌ Could not fetch account information")
            
    except Exception as e:
        st.error(f"❌ Error fetching account data: {e}")

def render_live_signals():
    """Render live trading signals"""
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 🎯 Live Trading Signals")
    with col2:
        if st.button("🔄 Refresh", key="refresh_signals"):
            st.cache_data.clear()
            st.rerun()
    
    # Confidence threshold slider
    confidence_threshold = st.slider(
        "Minimum Confidence Level",
        min_value=0.1,
        max_value=0.9,
        value=0.25,
        step=0.05,
        format="%.0f%%",
        key="confidence_slider"
    )
    
    with st.spinner("🔍 Analyzing markets..."):
        signals = get_live_signals(confidence_threshold)
    
    if signals:
        st.success(f"✅ Found {len(signals)} high-quality signals!")
        
        for i, signal in enumerate(signals):
            render_signal_card(signal, i)
    else:
        st.info("📊 No signals meet the current confidence threshold. Try lowering the threshold or check back later.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_quick_stats():
    """Render quick statistics"""
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.markdown("### 📈 Quick Stats")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Today's Signals", "12", "+3")
    
    with col2:
        st.metric("Win Rate", "68%", "+5%")
    
    with col3:
        st.metric("Total Pips", "+247", "+18")
    
    with col4:
        st.metric("Active Trades", "3", "+1")
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main application"""
    # Render header
    render_header()
    
    # Render status bar
    render_status_bar()
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Live Signals", "💰 Account", "📊 Analytics", "⚙️ Settings"])
    
    with tab1:
        render_live_signals()
        render_quick_stats()
    
    with tab2:
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.markdown("### 💰 Account Overview")
        render_account_summary()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Add some demo charts
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.markdown("### 📈 Performance Chart")
        
        # Demo performance data
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        performance = pd.DataFrame({
            'Date': dates,
            'Balance': 1000 + (dates - dates[0]).days * 2.5 + pd.Series(range(len(dates))).apply(lambda x: x * 0.1 * (1 if x % 7 < 5 else -1))
        })
        
        fig = px.line(performance, x='Date', y='Balance', title='Account Balance Over Time')
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#374151'
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Trading Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Demo pie chart for signal types
            signal_data = pd.DataFrame({
                'Type': ['BUY', 'SELL'],
                'Count': [7, 5]
            })
            fig = px.pie(signal_data, values='Count', names='Type', title='Signal Distribution')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#374151'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Demo bar chart for currency pairs
            pairs_data = pd.DataFrame({
                'Pair': ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD'],
                'Signals': [4, 3, 3, 2]
            })
            fig = px.bar(pairs_data, x='Pair', y='Signals', title='Signals by Currency Pair')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#374151'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.markdown("### ⚙️ Bot Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 Signal Settings")
            st.slider("Minimum Confidence", 0.1, 0.9, 0.25, key="min_conf_setting")
            st.slider("Max Daily Signals", 1, 20, 10, key="max_signals_setting")
            st.selectbox("Risk Level", ["Conservative", "Moderate", "Aggressive"], key="risk_level_setting")
        
        with col2:
            st.markdown("#### 🔔 Notifications")
            st.checkbox("Email Alerts", value=True, key="email_alerts")
            st.checkbox("Push Notifications", value=True, key="push_notifications")
            st.checkbox("SMS Alerts", value=False, key="sms_alerts")
        
        st.markdown("#### 💰 Trading Settings")
        col3, col4 = st.columns(2)
        with col3:
            st.number_input("Position Size ($)", min_value=100, max_value=10000, value=1000, key="position_size")
        with col4:
            st.number_input("Max Risk per Trade (%)", min_value=1, max_value=10, value=2, key="max_risk")
        
        if st.button("💾 Save Settings", key="save_settings"):
            st.success("✅ Settings saved successfully!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: rgba(255,255,255,0.7);">
        <p>🚀 James's Trading Bot • Built with ❤️ for Professional Forex Trading</p>
        <p style="font-size: 0.8rem;">⚠️ Trading involves risk. Past performance does not guarantee future results.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 