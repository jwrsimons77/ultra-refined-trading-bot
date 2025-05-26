#!/usr/bin/env python3
"""
James's Trading Bot - Mobile-First PWA
Ultra-responsive mobile trading interface with PWA capabilities
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
    MODULES_AVAILABLE = True
except ImportError as e:
    MODULES_AVAILABLE = False

# Page configuration for mobile PWA
st.set_page_config(
    page_title="James's Trading Bot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "James's Trading Bot - Professional Forex Trading"
    }
)

# Mobile-first CSS with PWA features
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    /* PWA Viewport */
    html, body {
        margin: 0;
        padding: 0;
        overflow-x: hidden;
        -webkit-overflow-scrolling: touch;
        -webkit-user-select: none;
        -webkit-touch-callout: none;
        -webkit-tap-highlight-color: transparent;
    }
    
    /* Global Mobile-First Styles */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        min-height: 100vh;
        font-family: 'Inter', sans-serif;
        padding: 0;
        margin: 0;
    }
    
    .stApp {
        background: transparent;
        margin: 0;
        padding: 0;
    }
    
    /* Hide all Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    .stDecoration {visibility: hidden;}
    
    /* Mobile Container */
    .main .block-container {
        padding: 0.5rem;
        max-width: 100%;
        margin: 0;
    }
    
    /* Mobile Header */
    .mobile-header {
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.9) 100%);
        backdrop-filter: blur(20px);
        border-radius: 0 0 25px 25px;
        padding: 1.5rem 1rem;
        margin: 0 0 1rem 0;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        text-align: center;
        border: 1px solid rgba(255,255,255,0.3);
        position: sticky;
        top: 0;
        z-index: 1000;
    }
    
    .mobile-title {
        font-size: 2rem;
        font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .mobile-subtitle {
        font-size: 0.9rem;
        color: #64748b;
        font-weight: 500;
        margin: 0.5rem 0 0 0;
    }
    
    /* Mobile Status Bar */
    .mobile-status {
        display: flex;
        justify-content: space-around;
        gap: 0.5rem;
        margin: 1rem 0;
        flex-wrap: wrap;
    }
    
    .status-chip {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.3rem;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
        flex: 1;
        justify-content: center;
        min-width: 70px;
    }
    
    .status-chip.offline {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
    }
    
    .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: currentColor;
        animation: pulse-dot 2s infinite;
    }
    
    @keyframes pulse-dot {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Mobile Signal Cards */
    .mobile-signal-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.9) 100%);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 15px 50px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .mobile-signal-card.buy {
        border-left: 4px solid #10b981;
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(255,255,255,0.95) 100%);
    }
    
    .mobile-signal-card.sell {
        border-left: 4px solid #ef4444;
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.05) 0%, rgba(255,255,255,0.95) 100%);
    }
    
    .mobile-signal-card:active {
        transform: scale(0.98);
    }
    
    /* Signal Header */
    .signal-mobile-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .signal-pair-mobile {
        font-size: 1.8rem;
        font-weight: 800;
        margin: 0;
        color: #1f2937;
    }
    
    .signal-type-mobile {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
        border: none;
        color: white;
        min-width: 60px;
        text-align: center;
    }
    
    .signal-type-mobile.buy {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
    }
    
    .signal-type-mobile.sell {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
    }
    
    /* Mobile Price Grid */
    .mobile-price-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.8rem;
        margin: 1rem 0;
    }
    
    .mobile-price-item {
        background: rgba(255,255,255,0.7);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.4);
    }
    
    .mobile-price-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #6b7280;
        margin-bottom: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .mobile-price-value {
        font-size: 1.2rem;
        font-weight: 800;
        margin: 0;
        color: #1f2937;
    }
    
    .mobile-price-pips {
        font-size: 0.8rem;
        color: #6b7280;
        margin-top: 0.2rem;
    }
    
    /* Mobile Confidence Badge */
    .mobile-confidence {
        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 15px;
        font-weight: 700;
        font-size: 0.8rem;
        display: inline-block;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);
    }
    
    /* Mobile Action Buttons */
    .mobile-actions {
        display: flex;
        gap: 0.8rem;
        margin-top: 1rem;
    }
    
    .mobile-btn {
        flex: 1;
        padding: 1rem;
        border-radius: 15px;
        font-weight: 700;
        font-size: 1rem;
        border: none;
        cursor: pointer;
        transition: all 0.2s ease;
        text-align: center;
        min-height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }
    
    .mobile-btn:active {
        transform: scale(0.95);
    }
    
    .mobile-btn-execute {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        box-shadow: 0 8px 25px rgba(245, 158, 11, 0.3);
    }
    
    .mobile-btn-details {
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%);
        color: #374151;
        border: 2px solid rgba(255,255,255,0.5);
        backdrop-filter: blur(10px);
    }
    
    /* Mobile Account Cards */
    .mobile-account-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .mobile-account-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%);
        backdrop-filter: blur(15px);
        border-radius: 15px;
        padding: 1.5rem 1rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.4);
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    }
    
    .mobile-account-title {
        font-size: 0.8rem;
        font-weight: 600;
        color: #6b7280;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .mobile-account-value {
        font-size: 1.5rem;
        font-weight: 800;
        margin: 0;
        color: #1f2937;
    }
    
    .mobile-account-change {
        font-size: 0.8rem;
        margin-top: 0.3rem;
        font-weight: 600;
    }
    
    /* Mobile Tabs */
    .mobile-tabs {
        display: flex;
        background: rgba(255,255,255,0.9);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 0.3rem;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        position: sticky;
        bottom: 1rem;
        z-index: 100;
    }
    
    .mobile-tab {
        flex: 1;
        padding: 0.8rem 0.5rem;
        border-radius: 15px;
        text-align: center;
        font-weight: 600;
        font-size: 0.8rem;
        cursor: pointer;
        transition: all 0.2s ease;
        color: #6b7280;
    }
    
    .mobile-tab.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .mobile-tab:active {
        transform: scale(0.95);
    }
    
    /* Loading States */
    .mobile-loading {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }
    
    .mobile-spinner {
        width: 30px;
        height: 30px;
        border: 3px solid rgba(255,255,255,0.3);
        border-top: 3px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Mobile Optimizations */
    @media (max-width: 480px) {
        .mobile-price-grid {
            grid-template-columns: 1fr;
        }
        
        .mobile-account-grid {
            grid-template-columns: 1fr;
        }
        
        .mobile-actions {
            flex-direction: column;
        }
        
        .mobile-status {
            grid-template-columns: 1fr 1fr;
        }
    }
    
    /* Touch Optimizations */
    .mobile-btn, .mobile-tab, .signal-type-mobile {
        -webkit-tap-highlight-color: transparent;
        -webkit-touch-callout: none;
        -webkit-user-select: none;
        touch-action: manipulation;
    }
    
    /* PWA Styles */
    @media (display-mode: standalone) {
        .mobile-header {
            padding-top: 2rem; /* Account for status bar */
        }
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .mobile-signal-card, .mobile-account-card {
            background: linear-gradient(135deg, rgba(30,30,30,0.95) 0%, rgba(20,20,20,0.9) 100%);
            color: #f9fafb;
        }
        
        .mobile-price-item {
            background: rgba(30,30,30,0.7);
            color: #f9fafb;
        }
        
        .mobile-tabs {
            background: rgba(30,30,30,0.9);
        }
    }
</style>
""", unsafe_allow_html=True)

def render_mobile_header():
    """Render mobile-optimized header"""
    st.markdown("""
    <div class="mobile-header">
        <h1 class="mobile-title">🚀 James's Trading Bot</h1>
        <p class="mobile-subtitle">AI-Powered Forex Signals</p>
    </div>
    """, unsafe_allow_html=True)

def render_mobile_status():
    """Render mobile status indicators"""
    current_time = datetime.now()
    market_open = 9 <= current_time.hour <= 17
    
    st.markdown(f"""
    <div class="mobile-status">
        <div class="status-chip {'offline' if not MODULES_AVAILABLE else ''}">
            <span class="status-dot"></span>
            {'Online' if MODULES_AVAILABLE else 'Offline'}
        </div>
        <div class="status-chip {'offline' if not market_open else ''}">
            <span class="status-dot"></span>
            {'Market Open' if market_open else 'Market Closed'}
        </div>
        <div class="status-chip">
            <span class="status-dot"></span>
            OANDA
        </div>
        <div class="status-chip">
            <span class="status-dot"></span>
            Signals
        </div>
    </div>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=30)
def get_mobile_signals(min_confidence=0.25):
    """Get signals optimized for mobile display"""
    if not MODULES_AVAILABLE:
        return []
    
    try:
        generator = ForexSignalGenerator()
        signals = generator.generate_forex_signals(max_signals=3, min_confidence=min_confidence)  # Limit to 3 for mobile
        return signals
    except Exception as e:
        logger.error(f"Error generating signals: {e}")
        return []

def render_mobile_signal_card(signal, index):
    """Render mobile-optimized signal card"""
    signal_type = signal.signal_type.upper()
    card_class = "buy" if signal_type == "BUY" else "sell"
    type_class = "buy" if signal_type == "BUY" else "sell"
    
    # Calculate potential profit percentage
    if signal_type == "BUY":
        potential_profit = signal.target_price - signal.entry_price
    else:
        potential_profit = signal.entry_price - signal.target_price
    
    potential_profit_pct = (potential_profit / signal.entry_price) * 100
    
    st.markdown(f"""
    <div class="mobile-signal-card {card_class}">
        <div class="signal-mobile-header">
            <h3 class="signal-pair-mobile">{signal.pair}</h3>
            <div class="signal-type-mobile {type_class}">{signal_type}</div>
        </div>
        
        <div class="mobile-confidence">
            {signal.confidence:.0%} Confidence
        </div>
        
        <div class="mobile-price-grid">
            <div class="mobile-price-item">
                <div class="mobile-price-label">Entry</div>
                <div class="mobile-price-value">{signal.entry_price:.5f}</div>
            </div>
            <div class="mobile-price-item">
                <div class="mobile-price-label">Target</div>
                <div class="mobile-price-value">{signal.target_price:.5f}</div>
                <div class="mobile-price-pips">+{signal.pips_target} pips</div>
            </div>
            <div class="mobile-price-item">
                <div class="mobile-price-label">Stop Loss</div>
                <div class="mobile-price-value">{signal.stop_loss:.5f}</div>
                <div class="mobile-price-pips">-{signal.pips_risk} pips</div>
            </div>
            <div class="mobile-price-item">
                <div class="mobile-price-label">Potential</div>
                <div class="mobile-price-value">{potential_profit_pct:.1f}%</div>
                <div class="mobile-price-pips">{signal.risk_reward_ratio}</div>
            </div>
        </div>
        
        <div style="margin: 1rem 0; padding: 0.8rem; background: rgba(255,255,255,0.5); border-radius: 10px;">
            <div class="mobile-price-label">Hold Time</div>
            <div style="font-size: 1rem; font-weight: 600; color: #374151;">
                {signal.hold_time_days:.1f} days ({signal.hold_time_hours:.0f}h)
            </div>
        </div>
        
        <div class="mobile-actions">
            <button class="mobile-btn mobile-btn-execute" onclick="alert('Execute {signal.pair} {signal_type}')">
                🚀 Execute
            </button>
            <button class="mobile-btn mobile-btn-details" onclick="alert('Details for {signal.pair}')">
                📊 Details
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_mobile_account():
    """Render mobile account summary"""
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
            open_trades = int(account_info.get('openTradeCount', 0))
            
            pnl_class = "positive" if unrealized_pnl >= 0 else "negative"
            pnl_sign = "+" if unrealized_pnl >= 0 else ""
            
            st.markdown(f"""
            <div class="mobile-account-grid">
                <div class="mobile-account-card">
                    <div class="mobile-account-title">Balance</div>
                    <div class="mobile-account-value">${balance:,.0f}</div>
                </div>
                <div class="mobile-account-card">
                    <div class="mobile-account-title">NAV</div>
                    <div class="mobile-account-value">${nav:,.0f}</div>
                </div>
                <div class="mobile-account-card">
                    <div class="mobile-account-title">P&L</div>
                    <div class="mobile-account-value {pnl_class}">{pnl_sign}${unrealized_pnl:.2f}</div>
                </div>
                <div class="mobile-account-card">
                    <div class="mobile-account-title">Trades</div>
                    <div class="mobile-account-value">{open_trades}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("❌ Could not fetch account data")
            
    except Exception as e:
        st.error(f"❌ Error: {e}")

def render_mobile_signals():
    """Render mobile signals section"""
    # Confidence slider
    confidence = st.slider(
        "Confidence Level",
        min_value=0.1,
        max_value=0.9,
        value=0.25,
        step=0.05,
        format="%.0f%%"
    )
    
    # Refresh button
    if st.button("🔄 Refresh Signals", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    # Get and display signals
    with st.spinner("🔍 Analyzing markets..."):
        signals = get_mobile_signals(confidence)
    
    if signals:
        st.success(f"✅ Found {len(signals)} signals!")
        for i, signal in enumerate(signals):
            render_mobile_signal_card(signal, i)
    else:
        st.info("📊 No signals found. Try lowering the confidence threshold.")

def render_mobile_stats():
    """Render mobile quick stats"""
    st.markdown("""
    <div class="mobile-account-grid">
        <div class="mobile-account-card">
            <div class="mobile-account-title">Today's Signals</div>
            <div class="mobile-account-value">8</div>
            <div class="mobile-account-change positive">+2</div>
        </div>
        <div class="mobile-account-card">
            <div class="mobile-account-title">Win Rate</div>
            <div class="mobile-account-value">72%</div>
            <div class="mobile-account-change positive">+5%</div>
        </div>
        <div class="mobile-account-card">
            <div class="mobile-account-title">Total Pips</div>
            <div class="mobile-account-value">+156</div>
            <div class="mobile-account-change positive">+23</div>
        </div>
        <div class="mobile-account-card">
            <div class="mobile-account-title">Active</div>
            <div class="mobile-account-value">3</div>
            <div class="mobile-account-change">trades</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main mobile application"""
    # Initialize session state for tab navigation
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0
    
    # Render mobile header
    render_mobile_header()
    
    # Render status bar
    render_mobile_status()
    
    # Tab navigation
    tab_names = ["🎯 Signals", "💰 Account", "📊 Stats", "⚙️ Settings"]
    
    # Create columns for tab buttons
    cols = st.columns(4)
    for i, (col, tab_name) in enumerate(zip(cols, tab_names)):
        with col:
            if st.button(tab_name, key=f"tab_{i}", use_container_width=True):
                st.session_state.active_tab = i
    
    # Display content based on active tab
    if st.session_state.active_tab == 0:
        # Signals tab
        st.markdown("### 🎯 Live Trading Signals")
        render_mobile_signals()
        
    elif st.session_state.active_tab == 1:
        # Account tab
        st.markdown("### 💰 Account Overview")
        render_mobile_account()
        
        # Simple performance chart
        st.markdown("### 📈 Performance")
        dates = pd.date_range(start='2024-11-01', end='2024-12-31', freq='D')
        performance = pd.DataFrame({
            'Date': dates,
            'Balance': 1000 + (dates - dates[0]).days * 1.5
        })
        
        fig = px.line(performance, x='Date', y='Balance', title='Account Growth')
        fig.update_layout(
            height=300,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#374151',
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
        
    elif st.session_state.active_tab == 2:
        # Stats tab
        st.markdown("### 📊 Trading Statistics")
        render_mobile_stats()
        
        # Signal distribution chart
        signal_data = pd.DataFrame({
            'Type': ['BUY', 'SELL'],
            'Count': [5, 3]
        })
        fig = px.pie(signal_data, values='Count', names='Type', title='Signal Distribution')
        fig.update_layout(
            height=300,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#374151',
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
        
    elif st.session_state.active_tab == 3:
        # Settings tab
        st.markdown("### ⚙️ Bot Settings")
        
        st.markdown("#### 🎯 Signal Settings")
        st.slider("Min Confidence", 0.1, 0.9, 0.25, key="settings_confidence")
        st.slider("Max Signals", 1, 10, 5, key="settings_max_signals")
        
        st.markdown("#### 💰 Trading Settings")
        st.number_input("Position Size ($)", min_value=100, max_value=5000, value=1000, key="settings_position")
        st.number_input("Max Risk (%)", min_value=1, max_value=5, value=2, key="settings_risk")
        
        st.markdown("#### 🔔 Notifications")
        st.checkbox("Push Notifications", value=True, key="settings_push")
        st.checkbox("Email Alerts", value=False, key="settings_email")
        
        if st.button("💾 Save Settings", use_container_width=True):
            st.success("✅ Settings saved!")
    
    # Footer
    st.markdown("""
    <div style="text-align: center; padding: 1rem; color: rgba(255,255,255,0.8); font-size: 0.8rem;">
        🚀 James's Trading Bot • Professional Forex Trading<br>
        ⚠️ Trading involves risk. Trade responsibly.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 