#!/usr/bin/env python3
"""
Comprehensive Forex Trading App
Integrates signal generation, OANDA trading, and backtesting
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, time
import time as time_module
import logging
import pytz

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our modules
try:
    from forex_signal_generator import ForexSignalGenerator
    from oanda_trader import OANDATrader
    from forex_backtester import ForexBacktester
    MODULES_AVAILABLE = True
except ImportError as e:
    MODULES_AVAILABLE = False
    st.error(f"Required modules not available: {e}")

# Page config
st.set_page_config(
    page_title="James's Trading Bot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional CSS styling with mobile-first optimizations and FIXED CONTRAST
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Mobile-First Global Styles */
    html, body {
        margin: 0;
        padding: 0;
        overflow-x: hidden;
        -webkit-overflow-scrolling: touch;
        -webkit-user-select: none;
        -webkit-touch-callout: none;
        -webkit-tap-highlight-color: transparent;
    }
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        font-family: 'Inter', sans-serif;
        padding: 0;
    }
    
    .stApp {
        background: transparent;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    .stDecoration {visibility: hidden;}
    
    /* Mobile Container Optimization */
    .main .block-container {
        padding: 0.5rem;
        max-width: 100%;
        margin: 0;
    }
    
    /* Mobile-Optimized Header with BETTER CONTRAST */
    .trading-header {
        background: linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(255,255,255,0.95) 100%);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem 1rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.15);
        text-align: center;
        border: 2px solid rgba(255,255,255,0.4);
        position: sticky;
        top: 0.5rem;
        z-index: 100;
    }
    
    .trading-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .trading-subtitle {
        font-size: 1.1rem;
        color: #374151;
        font-weight: 600;
        margin: 0;
    }
    
    /* Mobile-First Card Styling with BETTER CONTRAST */
    .modern-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(255,255,255,0.95) 100%);
        backdrop-filter: blur(20px);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 15px 40px rgba(0,0,0,0.12);
        border: 2px solid rgba(255,255,255,0.4);
        transition: all 0.3s ease;
        color: #1f2937;
    }
    
    .modern-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 20px 50px rgba(0,0,0,0.18);
    }
    
    /* Mobile-Optimized Signal Cards with BETTER CONTRAST */
    .signal-card-buy {
        background: linear-gradient(135deg, rgba(236, 253, 245, 0.98) 0%, rgba(209, 250, 229, 0.95) 100%);
        border-left: 4px solid #10b981;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(16, 185, 129, 0.2);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        color: #064e3b;
        border: 2px solid rgba(16, 185, 129, 0.3);
    }
    
    .signal-card-sell {
        background: linear-gradient(135deg, rgba(254, 242, 242, 0.98) 0%, rgba(254, 202, 202, 0.95) 100%);
        border-left: 4px solid #ef4444;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(239, 68, 68, 0.2);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        color: #7f1d1d;
        border: 2px solid rgba(239, 68, 68, 0.3);
    }
    
    .signal-card-buy:active, .signal-card-sell:active {
        transform: scale(0.98);
    }
    
    /* Auto-execute badge - Mobile Optimized with BETTER CONTRAST */
    .auto-execute-badge {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 20px;
        display: inline-block;
        margin-bottom: 1rem;
        font-weight: 700;
        font-size: 0.9rem;
        letter-spacing: 0.05em;
        box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
        animation: pulse 2s infinite;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    
    /* Mobile-Optimized Metrics Cards with BETTER CONTRAST */
    .metric-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(255,255,255,0.95) 100%);
        backdrop-filter: blur(15px);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        border: 2px solid rgba(255,255,255,0.4);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        min-height: 100px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        color: #1f2937;
    }
    
    .metric-card:active {
        transform: scale(0.95);
    }
    
    .metric-title {
        font-size: 0.9rem;
        font-weight: 700;
        color: #374151;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        margin: 0;
        line-height: 1;
        color: #1f2937;
    }
    
    .metric-subtitle {
        font-size: 0.8rem;
        color: #6b7280;
        margin-top: 0.3rem;
        font-weight: 500;
    }
    
    /* Mobile-Optimized P&L Cards with BETTER CONTRAST */
    .pnl-profit {
        background: linear-gradient(135deg, rgba(236, 253, 245, 0.98) 0%, rgba(209, 250, 229, 0.95) 100%);
        border: 3px solid #10b981;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.2);
        min-height: 100px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        color: #064e3b;
    }
    
    .pnl-loss {
        background: linear-gradient(135deg, rgba(254, 242, 242, 0.98) 0%, rgba(254, 202, 202, 0.95) 100%);
        border: 3px solid #ef4444;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 8px 25px rgba(239, 68, 68, 0.2);
        min-height: 100px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        color: #7f1d1d;
    }
    
    .pnl-neutral {
        background: linear-gradient(135deg, rgba(248, 250, 252, 0.98) 0%, rgba(226, 232, 240, 0.95) 100%);
        border: 3px solid #64748b;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 8px 25px rgba(100, 116, 139, 0.2);
        min-height: 100px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        color: #334155;
    }
    
    /* Mobile-Optimized Button Styling with BETTER CONTRAST */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
        letter-spacing: 0.025em;
        min-height: 50px;
        width: 100%;
        -webkit-tap-highlight-color: transparent;
        touch-action: manipulation;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.5);
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
    }
    
    .stButton > button:active {
        transform: scale(0.95);
    }
    
    /* Mobile Market Status with BETTER CONTRAST */
    .market-open {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        font-weight: 700;
        font-size: 1rem;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
        margin-bottom: 1rem;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    
    .market-closed {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        font-weight: 700;
        font-size: 1rem;
        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
        margin-bottom: 1rem;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    
    /* Animations */
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.9; transform: scale(1.02); }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .slide-in {
        animation: slideIn 0.4s ease-out;
    }
    
    /* Mobile-First Responsive Design */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 0.25rem;
        }
        
        .trading-header {
            padding: 1.5rem 1rem;
            margin-bottom: 1rem;
            border-radius: 15px;
        }
        
        .trading-title {
            font-size: 2rem;
        }
        
        .trading-subtitle {
            font-size: 1rem;
        }
        
        .signal-card-buy, .signal-card-sell {
            padding: 1.2rem;
            margin: 0.8rem 0;
            border-radius: 12px;
        }
        
        .modern-card {
            padding: 1.2rem;
            margin: 0.8rem 0;
            border-radius: 12px;
        }
        
        .metric-card, .pnl-profit, .pnl-loss, .pnl-neutral {
            padding: 1rem;
            min-height: 80px;
        }
        
        .metric-value {
            font-size: 1.5rem;
        }
        
        .metric-title {
            font-size: 0.8rem;
        }
    }
    
    @media (max-width: 480px) {
        .main .block-container {
            padding: 0.1rem;
        }
        
        .trading-header {
            padding: 1rem 0.8rem;
            margin-bottom: 0.8rem;
        }
        
        .trading-title {
            font-size: 1.8rem;
        }
        
        .trading-subtitle {
            font-size: 0.9rem;
        }
        
        .signal-card-buy, .signal-card-sell, .modern-card {
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 10px;
        }
        
        .metric-card, .pnl-profit, .pnl-loss, .pnl-neutral {
            padding: 0.8rem;
            min-height: 70px;
        }
        
        .metric-value {
            font-size: 1.3rem;
        }
        
        .metric-title {
            font-size: 0.75rem;
        }
        
        .stButton > button {
            padding: 0.8rem 1rem;
            font-size: 0.9rem;
            min-height: 45px;
        }
    }
    
    /* Mobile Tab Styling with BETTER CONTRAST */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(255,255,255,0.2);
        border-radius: 12px;
        padding: 0.3rem;
        margin-bottom: 1rem;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        border: 2px solid rgba(255,255,255,0.3);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: rgba(255,255,255,0.9);
        font-weight: 700;
        padding: 0.8rem 1rem;
        transition: all 0.3s ease;
        white-space: nowrap;
        min-width: fit-content;
        -webkit-tap-highlight-color: transparent;
        touch-action: manipulation;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(255,255,255,0.3);
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        text-shadow: 0 1px 2px rgba(0,0,0,0.4);
    }
    
    /* Mobile Trade Status Indicators with BETTER CONTRAST */
    .trade-open, .trade-profit, .trade-loss {
        padding: 0.4rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 700;
        display: inline-block;
        margin: 0.2rem;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    
    .trade-open {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
    }
    
    .trade-profit {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    .trade-loss {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
    }
    
    /* Mobile Input Optimizations with BETTER CONTRAST */
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 2px solid rgba(255,255,255,0.4);
        background: rgba(255,255,255,0.95);
        min-height: 50px;
        color: #1f2937;
    }
    
    .stSlider > div > div {
        background: rgba(255,255,255,0.95);
        border-radius: 10px;
        padding: 1rem;
        border: 2px solid rgba(255,255,255,0.4);
    }
    
    .stNumberInput > div > div > input {
        border-radius: 10px;
        border: 2px solid rgba(255,255,255,0.4);
        background: rgba(255,255,255,0.95);
        min-height: 50px;
        font-size: 1rem;
        color: #1f2937;
    }
    
    /* Mobile Expander Styling with BETTER CONTRAST */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.2);
        border-radius: 10px;
        padding: 1rem;
        font-weight: 700;
        border: 2px solid rgba(255,255,255,0.3);
        color: white;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }
    
    /* Touch Optimizations */
    * {
        -webkit-tap-highlight-color: transparent;
        -webkit-touch-callout: none;
    }
    
    button, .stButton > button, [role="button"] {
        touch-action: manipulation;
        -webkit-user-select: none;
        user-select: none;
    }
    
    /* PWA Support */
    @media (display-mode: standalone) {
        .trading-header {
            padding-top: 2rem; /* Account for status bar */
        }
    }
    
    /* Streamlit specific text contrast fixes */
    .stMarkdown, .stText, p, div, span {
        color: #1f2937 !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #1f2937 !important;
    }
    
    /* Success/Error/Warning message contrast */
    .stSuccess {
        background: rgba(236, 253, 245, 0.95) !important;
        color: #064e3b !important;
        border: 2px solid #10b981 !important;
    }
    
    .stError {
        background: rgba(254, 242, 242, 0.95) !important;
        color: #7f1d1d !important;
        border: 2px solid #ef4444 !important;
    }
    
    .stWarning {
        background: rgba(255, 251, 235, 0.95) !important;
        color: #92400e !important;
        border: 2px solid #f59e0b !important;
    }
    
    .stInfo {
        background: rgba(239, 246, 255, 0.95) !important;
        color: #1e3a8a !important;
        border: 2px solid #3b82f6 !important;
    }
</style>
""", unsafe_allow_html=True)

# OANDA Configuration
OANDA_API_KEY = "fe92315bee29b117825fed529cf3fa99-173e927b8cdbb1fc244993e24e33fd93"
OANDA_ACCOUNT_ID = "101-004-31788297-001"

# Initialize components
if MODULES_AVAILABLE:
    signal_generator = ForexSignalGenerator()
    trader = OANDATrader(OANDA_API_KEY, OANDA_ACCOUNT_ID, environment="practice")
    backtester = ForexBacktester(initial_balance=1000.0)

def render_header():
    """Render the main header."""
    st.markdown("""
    <div class="trading-header">
        <div class="trading-title">🚀 James's Trading Bot</div>
        <div style="font-size: 1.2rem; color: #374151; font-weight: 600;">
            Automated Trading with OANDA • Risk Management • Live Alerts
        </div>
    </div>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=30)  # Cache account data for 30 seconds
def get_account_data():
    """Get account data only - no signal generation."""
    if not MODULES_AVAILABLE:
        return None, []
    
    try:
        account_summary = trader.get_account_summary()
        positions = trader.get_open_positions()
        return account_summary, positions
    except Exception as e:
        st.error(f"Error getting account data: {e}")
        return None, []

@st.cache_data(ttl=300)  # Cache signals for 5 minutes - only refresh when explicitly requested
def get_live_signals(min_confidence=0.25, force_refresh=False):
    """Get live forex signals - only fetch news when explicitly requested."""
    if not MODULES_AVAILABLE:
        return []
    
    try:
        # Force refresh of signal generator to use latest code
        import importlib
        import sys
        if 'forex_signal_generator' in sys.modules:
            importlib.reload(sys.modules['forex_signal_generator'])
        
        from forex_signal_generator import ForexSignalGenerator
        fresh_signal_generator = ForexSignalGenerator()
        
        signals = fresh_signal_generator.generate_forex_signals(
            max_signals=8,
            min_confidence=min_confidence
        )
        return signals
    except Exception as e:
        st.error(f"Error generating signals: {e}")
        return []

def calculate_trade_pnl(signal, position_size=1000):
    """Calculate potential profit and loss for a trade with proper leverage accounting."""
    # Calculate pip values correctly
    if 'JPY' in signal.pair:
        pip_value = 0.01
    else:
        pip_value = 0.0001
    
    # Calculate pips to target and stop loss - FIXED CALCULATION
    if signal.signal_type == "BUY":
        pips_to_target = (signal.target_price - signal.entry_price) / pip_value
        pips_to_stop = (signal.entry_price - signal.stop_loss) / pip_value
    else:  # SELL
        pips_to_target = (signal.entry_price - signal.target_price) / pip_value
        pips_to_stop = (signal.stop_loss - signal.entry_price) / pip_value
    
    # Calculate proper pip values based on position size and currency pair
    # Standard forex pip values for different position sizes:
    # - For major pairs (EUR/USD, GBP/USD, etc.): 1 pip = $0.0001 * position_size
    # - For JPY pairs: 1 pip = $0.01 * position_size / current_price
    
    if 'JPY' in signal.pair:
        # For JPY pairs, pip value depends on current price
        # Approximate pip value: (0.01 / current_price) * position_size
        pip_value_usd = (0.01 / signal.entry_price) * position_size
    else:
        # For major pairs: pip value = 0.0001 * position_size
        pip_value_usd = 0.0001 * position_size
    
    # Calculate actual P&L in USD
    potential_profit = pips_to_target * pip_value_usd
    potential_loss = pips_to_stop * pip_value_usd
    
    # Calculate margin required (this shows the leverage effect)
    # Typical margin requirements for 30:1 leverage: ~3.33% for majors, ~5% for minors
    margin_rates = {
        'EUR/USD': 0.0333, 'GBP/USD': 0.0333, 'USD/JPY': 0.0333,
        'USD/CHF': 0.0333, 'AUD/USD': 0.0333, 'USD/CAD': 0.0333,
        'NZD/USD': 0.05  # Higher margin for minor pairs (20:1 leverage)
    }
    
    margin_rate = margin_rates.get(signal.pair, 0.05)  # Default 5% (20:1 leverage)
    
    # Calculate margin required
    if signal.pair.startswith('USD/'):
        # USD is base currency
        margin_required = position_size * margin_rate
    else:
        # USD is quote currency
        margin_required = position_size * signal.entry_price * margin_rate
    
    # Calculate effective leverage
    notional_value = position_size * signal.entry_price if not signal.pair.startswith('USD/') else position_size
    effective_leverage = notional_value / margin_required if margin_required > 0 else 1
    
    return {
        'pips_to_target': round(pips_to_target, 1),
        'pips_to_stop': round(pips_to_stop, 1),
        'potential_profit': round(potential_profit, 2),
        'potential_loss': round(potential_loss, 2),
        'risk_reward_ratio': round(pips_to_target / pips_to_stop, 2) if pips_to_stop > 0 else 0,
        'margin_required': round(margin_required, 2),
        'effective_leverage': round(effective_leverage, 1),
        'notional_value': round(notional_value, 2)
    }

def calculate_position_size_from_risk(account_balance, risk_percentage, stop_loss_pips):
    """Calculate position size based on risk percentage with proper leverage accounting."""
    risk_amount = account_balance * (risk_percentage / 100)
    
    # Calculate position size based on actual pip values
    # This accounts for the fact that larger positions have proportionally larger pip values
    
    if stop_loss_pips > 0:
        # For major pairs: pip value = 0.0001 * position_size
        # So: risk_amount = stop_loss_pips * 0.0001 * position_size
        # Therefore: position_size = risk_amount / (stop_loss_pips * 0.0001)
        position_size = risk_amount / (stop_loss_pips * 0.0001)
        
        # Ensure reasonable position size limits
        min_position = 1000    # Minimum 1,000 units
        max_position = 100000  # Maximum 100,000 units (considering leverage)
        
        position_size = max(min_position, min(max_position, int(position_size)))
    else:
        position_size = 1000  # Default minimum
    
    return position_size

def render_live_signals(market_status):
    """Render live trading signals with detailed profit/loss information."""
    st.markdown("### 🎯 Live Trading Signals")
    
    # Initialize default values to prevent UnboundLocalError
    risk_percentage = 5
    position_size = 1000
    
    # Auto-execution status check
    auto_executed_trades = check_and_auto_execute_trades()
    
    # Signal settings with better accessibility
    col1, col2, col3 = st.columns(3)
    with col1:
        min_confidence = st.slider("Minimum Confidence", 0.10, 0.80, 0.25, 0.05, key="signal_confidence")
    with col2:
        # Enhanced position sizing options
        position_type = st.selectbox("Position Sizing", [
            "Fixed Units", 
            "Risk-Based (% of account)"
        ], key="position_type")
        
        if position_type == "Fixed Units":
            position_size = st.selectbox("Position Size", [1000, 2000, 5000, 10000], index=0, key="position_size")
            risk_percentage = 5  # Default for display
        else:
            risk_percentage = st.selectbox("Risk Percentage", [1, 2, 5, 10], index=2, key="risk_percentage")
            # For 10% of £1000 = £100 risk
            if risk_percentage == 10:
                st.info("💡 10% of £1000 = £100 maximum risk per trade")
            position_size = None
    with col3:
        auto_trade_enabled = st.checkbox("Auto-Trade High Confidence (≥75%)", key="auto_trade", 
                                       help="Automatically execute trades with 75%+ confidence when market is open")
        
        # Add cache clear button for testing
        if st.button("🔄 Refresh Signals", key="refresh_signals", help="Clear cache and get fresh signals"):
            # Clear only signal cache, not account cache
            get_live_signals.clear()
            st.rerun()
        
        # Add test button for demonstration
        if st.button("🧪 Test Mode (Low Threshold)", key="test_signals", help="Generate signals with 15% minimum confidence for testing"):
            # Clear only signal cache for testing
            get_live_signals.clear()
            # Force low confidence signals for testing
            test_signals = get_live_signals(min_confidence=0.15, force_refresh=True)
            if test_signals:
                st.success(f"🧪 **Test Mode:** Found {len(test_signals)} signals with 15% minimum confidence!")
                st.info("💡 This demonstrates signal generation functionality. In live trading, use higher confidence levels (50%+)")
            else:
                st.warning("🧪 **Test Mode:** No signals found even at 15% confidence. Market conditions may be neutral.")
        
        # Show market status in settings
        if market_status:
            if market_status['is_open'] and auto_trade_enabled:
                st.success("🟢 Auto-trading active")
            elif market_status['is_open'] and not auto_trade_enabled:
                st.info("🔵 Auto-trading disabled (market open)")
            elif not market_status['is_open'] and auto_trade_enabled:
                st.warning("🟡 Auto-trading enabled (market closed)")
            else:
                st.error("🔴 Auto-trading disabled (market closed)")
    
    signals = get_live_signals(min_confidence)
    
    if not signals:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border: 2px solid #f59e0b; border-radius: 20px; padding: 3rem; text-align: center; margin: 2rem 0;">
            <h3 style="color: #92400e; font-size: 2.2rem; margin-bottom: 1rem;">⚠️ No Signals Available</h3>
            <p style="color: #92400e; font-size: 1.6rem; margin-bottom: 1rem;">No signals meet the current confidence criteria (≥{min_confidence:.0%})</p>
            <p style="color: #92400e; font-size: 1.4rem; margin: 0;">💡 Try lowering the minimum confidence threshold to see more signals</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Separate signals by auto-execute eligibility
    auto_execute_signals = [s for s in signals if s.confidence >= 0.75]
    manual_signals = [s for s in signals if s.confidence < 0.75]
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); border: 3px solid #10b981; border-radius: 20px; padding: 2rem; text-align: center; margin-bottom: 3rem; box-shadow: 0 10px 40px rgba(16, 185, 129, 0.2);">
        <h3 style="color: #047857; font-size: 2.4rem; margin-bottom: 1rem;">✅ Found {len(signals)} Trading Signals</h3>
        <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
            <div style="background: rgba(255,255,255,0.8); padding: 1rem 2rem; border-radius: 15px;">
                <span style="color: #f59e0b; font-size: 1.6rem; font-weight: bold;">🤖 {len(auto_execute_signals)} Auto-Execute</span>
            </div>
            <div style="background: rgba(255,255,255,0.8); padding: 1rem 2rem; border-radius: 15px;">
                <span style="color: #3b82f6; font-size: 1.6rem; font-weight: bold;">👤 {len(manual_signals)} Manual Review</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display auto-execute signals first
    if auto_execute_signals:
        st.markdown("#### 🤖 Auto-Execute Signals (≥75% Confidence)")
        
        for i, signal in enumerate(auto_execute_signals):
            render_signal_card(signal, i, position_type, position_size, risk_percentage, auto_execute=True, market_status=market_status)
    
    # Display manual signals
    if manual_signals:
        st.markdown("#### 👤 Manual Review Signals")
        
        for i, signal in enumerate(manual_signals, start=len(auto_execute_signals)):
            render_signal_card(signal, i, position_type, position_size, risk_percentage, auto_execute=False, market_status=market_status)

def render_signal_card(signal, index, position_type, position_size, risk_percentage, auto_execute=False, market_status=None):
    """Render individual signal card with enhanced styling."""
    # Calculate position size based on selection
    if position_type == "Risk-Based (% of account)":
        # Estimate stop loss pips for risk calculation - FIXED CALCULATION
        if 'JPY' in signal.pair:
            stop_pips = abs(signal.entry_price - signal.stop_loss) / 0.01
        else:
            stop_pips = abs(signal.entry_price - signal.stop_loss) / 0.0001
        
        calculated_position_size = calculate_position_size_from_risk(1000, risk_percentage, stop_pips)
        display_position_size = calculated_position_size
        risk_info = f"Risk: {risk_percentage}% (£{1000 * risk_percentage / 100:.0f})"
    else:
        display_position_size = position_size
        risk_info = f"Fixed: {position_size:,} units"
    
    # Calculate profit/loss potential
    pnl_data = calculate_trade_pnl(signal, display_position_size)
    
    # Determine if market is open
    market_open = market_status and market_status.get('is_open', False) if market_status else False
    
    # Create a container for the signal
    with st.container():
        # Signal header
        signal_emoji = "🟢" if signal.signal_type == "BUY" else "🔴"
        
        # Auto-execute badge
        if auto_execute:
            st.info("🤖 **AUTO-EXECUTE ELIGIBLE** - High confidence signal")
        
        # Market closed warning
        if not market_open and auto_execute:
            st.warning("⚠️ **MARKET CLOSED** - Auto-execute disabled until market reopens")
        
        # Main signal info
        st.markdown(f"## {signal_emoji} {signal.signal_type} {signal.pair}")
        
        # Confidence display
        confidence_pct = signal.confidence * 100
        if confidence_pct >= 75:
            confidence_color = "🟢"
            confidence_text = "VERY HIGH"
        elif confidence_pct >= 60:
            confidence_color = "🟡"
            confidence_text = "HIGH"
        elif confidence_pct >= 45:
            confidence_color = "🟠"
            confidence_text = "MEDIUM"
        else:
            confidence_color = "🔴"
            confidence_text = "LOW"
        
        st.markdown(f"**Confidence:** {confidence_color} {confidence_pct:.1f}% ({confidence_text})")
        st.markdown(f"**Reason:** {signal.reason}")
        
        # Price levels
        st.markdown("### 📊 Price Levels")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Entry Price", f"{signal.entry_price:.5f}")
        with col2:
            st.metric("Target", f"{signal.target_price:.5f}", f"+{pnl_data['pips_to_target']:.1f} pips")
        with col3:
            st.metric("Stop Loss", f"{signal.stop_loss:.5f}", f"-{pnl_data['pips_to_stop']:.1f} pips")
        with col4:
            st.metric("Risk:Reward", f"1:{pnl_data['risk_reward_ratio']:.1f}")
        
        # Profit/Loss Calculation
        st.markdown("### 💰 Profit/Loss Calculation")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Position Size", f"{display_position_size:,} units", risk_info)
        with col2:
            st.metric("Potential Profit", f"£{pnl_data['potential_profit']:.2f}", f"+{pnl_data['pips_to_target']:.1f} pips")
        with col3:
            st.metric("Potential Loss", f"£{pnl_data['potential_loss']:.2f}", f"-{pnl_data['pips_to_stop']:.1f} pips")
        with col4:
            net_expectation = (pnl_data['potential_profit'] * 0.6) - (pnl_data['potential_loss'] * 0.4)
            st.metric("Expected Value", f"£{net_expectation:.2f}", "60% win rate")
        
        # Leverage & Margin Information
        st.markdown("### ⚡ Leverage & Margin")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Margin Required", f"£{pnl_data['margin_required']:.2f}", "Capital at risk")
        with col2:
            st.metric("Notional Value", f"£{pnl_data['notional_value']:.2f}", "Total position value")
        with col3:
            st.metric("Effective Leverage", f"{pnl_data['effective_leverage']:.1f}:1", "Amplification factor")
        with col4:
            margin_percentage = (pnl_data['margin_required'] / 1000) * 100  # Assuming $1000 account
            st.metric("Margin Usage", f"{margin_percentage:.1f}%", "Of account balance")
        
        # Trading Actions
        st.markdown("### 🎯 Trading Actions")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # DEBUG: Show which button logic is being used
            # st.write(f"**DEBUG:** Market Open = {market_open}, Auto Execute = {auto_execute}")
            
            if market_open:
                if auto_execute:
                    if st.button(f"🤖 Auto-Execute NOW", key=f"auto_execute_{index}", help="Execute automatically with current settings"):
                        execute_trade_with_details(signal, display_position_size, pnl_data, auto=True)
                else:
                    if st.button(f"🚀 Execute Trade", key=f"execute_{index}", help="Execute this trade immediately"):
                        execute_trade_with_details(signal, display_position_size, pnl_data)
            else:
                if auto_execute:
                    st.button(f"🚫 Market Closed", key=f"disabled_{index}", disabled=True, help="Auto-execute disabled - market is closed")
                else:
                    # Check if this signal is already queued BEFORE showing the button
                    already_queued = any(
                        p['signal'].pair == signal.pair and 
                        p['signal'].signal_type == signal.signal_type 
                        for p in st.session_state.get('pending_signals', [])
                    )
                    
                    if already_queued:
                        st.button(f"✅ Already Queued", key=f"queued_{index}", disabled=True, help="This trade is already queued for execution")
                        st.info(f"📋 **{signal.signal_type} {signal.pair}** is already queued for execution when market opens!")
                    else:
                        if st.button(f"📋 Queue for Execution", key=f"queue_{index}", help="Queue this trade for automatic execution when market opens"):
                            # Store for later execution when market opens
                            if 'pending_signals' not in st.session_state:
                                st.session_state.pending_signals = []
                            
                            # Double-check if this signal is already queued (race condition protection)
                            already_queued_check = any(
                                p['signal'].pair == signal.pair and 
                                p['signal'].signal_type == signal.signal_type 
                                for p in st.session_state.pending_signals
                            )
                            
                            if already_queued_check:
                                st.warning(f"⚠️ **{signal.signal_type} {signal.pair}** is already queued for execution!")
                            else:
                                st.session_state.pending_signals.append({
                                    'signal': signal,
                                    'position_size': display_position_size,
                                    'pnl_data': pnl_data,
                                    'timestamp': datetime.now()
                                })
                                
                                # Enhanced logging for pending trades
                                logger.info(f"""
🚀 TRADE QUEUED FOR EXECUTION 🚀

Pair: {signal.pair}
Action: {signal.signal_type}
Entry: {signal.entry_price:.5f}
Target: {signal.target_price:.5f}
Stop Loss: {signal.stop_loss:.5f}
Position Size: {display_position_size:,} units
Confidence: {signal.confidence:.1%}
Potential Profit: £{pnl_data['potential_profit']:.2f}
Potential Loss: £{pnl_data['potential_loss']:.2f}
Risk:Reward: 1:{pnl_data['risk_reward_ratio']:.1f}
Queued at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

STATUS: PENDING - Will execute when market opens (Sunday 22:00 UTC)
                                """)
                                
                                st.success(f"""
                                ✅ **Trade Successfully Queued!**
                                
                                📋 **Trade Details:**
                                • {signal.signal_type} {signal.pair} at {signal.entry_price:.5f}
                                • Position Size: {display_position_size:,} units
                                • Potential Profit: £{pnl_data['potential_profit']:.2f}
                                • Queued at: {datetime.now().strftime('%H:%M:%S')}
                                
                                🚀 **This trade will automatically execute when the market reopens!**
                                
                                💡 You can view and manage all pending trades at the top of the page when the market is closed.
                                """)
                                
                                # Log the queued trade
                                log_detailed_trade(signal, "QUEUED", display_position_size, pnl_data, "PENDING")
                                
                                # Force a rerun to update the UI
                                st.rerun()
        
        with col2:
            if st.button(f"📊 Detailed Analysis", key=f"analyze_{index}", help="View comprehensive analysis"):
                show_detailed_analysis(signal, pnl_data)
        
        with col3:
            if st.button(f"⚠️ Set Price Alert", key=f"alert_{index}", help="Set alert for entry price"):
                set_price_alert(signal)
        
        with col4:
            if st.button(f"📋 Copy Signal", key=f"copy_{index}", help="Copy signal details"):
                copy_signal_details(signal, pnl_data)
        
        st.divider()  # Clean separator between signals

def show_detailed_analysis(signal, pnl_data):
    """Show comprehensive signal analysis."""
    st.markdown("#### 📊 Detailed Signal Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Technical Analysis:**")
        st.write(f"• Technical Score: {signal.technical_score:.2f}/1.0")
        st.write(f"• News Sentiment: {signal.news_sentiment:.2f}")
        st.write(f"• Overall Confidence: {signal.confidence:.1%}")
        st.write(f"• Signal Strength: {'Strong' if signal.confidence > 0.7 else 'Moderate' if signal.confidence > 0.5 else 'Weak'}")
    
    with col2:
        st.markdown("**Risk Analysis:**")
        st.write(f"• Pips to Target: +{pnl_data['pips_to_target']:.1f}")
        st.write(f"• Pips to Stop: -{pnl_data['pips_to_stop']:.1f}")
        st.write(f"• Risk:Reward: 1:{pnl_data['risk_reward_ratio']:.1f}")
        st.write(f"• Risk Level: {'Low' if pnl_data['risk_reward_ratio'] > 2 else 'Moderate' if pnl_data['risk_reward_ratio'] > 1.5 else 'High'}")
    
    # Leverage & Margin Analysis
    st.markdown("**Leverage & Margin Analysis:**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"• Margin Required: £{pnl_data['margin_required']:.2f}")
        st.write(f"• Notional Value: £{pnl_data['notional_value']:.2f}")
        st.write(f"• Effective Leverage: {pnl_data['effective_leverage']:.1f}:1")
    
    with col2:
        margin_pct = (pnl_data['margin_required'] / 1000) * 100
        leverage_risk = "High" if pnl_data['effective_leverage'] > 50 else "Moderate" if pnl_data['effective_leverage'] > 30 else "Low"
        st.write(f"• Margin Usage: {margin_pct:.1f}% of account")
        st.write(f"• Leverage Risk: {leverage_risk}")
        st.write(f"• Capital Efficiency: {(pnl_data['notional_value'] / pnl_data['margin_required']):.1f}x")
    
    # Profit scenarios
    st.markdown("**Profit Scenarios:**")
    scenarios = [
        ("Conservative (50% to target)", pnl_data['potential_profit'] * 0.5),
        ("Target Hit (100%)", pnl_data['potential_profit']),
        ("Extended Move (150%)", pnl_data['potential_profit'] * 1.5),
    ]
    
    for scenario, profit in scenarios:
        st.write(f"• {scenario}: £{profit:.2f}")
    
    # Leverage impact explanation
    st.markdown("**💡 Leverage Impact:**")
    st.info(f"""
    **Understanding Your Leverage:**
    
    • **Position Value:** £{pnl_data['notional_value']:.2f} (total currency exposure)
    • **Margin Required:** £{pnl_data['margin_required']:.2f} (your capital at risk)
    • **Leverage:** {pnl_data['effective_leverage']:.1f}:1 (amplification factor)
    
    This means you control £{pnl_data['notional_value']:.2f} worth of currency with only £{pnl_data['margin_required']:.2f} of your capital. 
    Both profits and losses are amplified by the leverage factor.
    """)

def copy_signal_details(signal, pnl_data):
    """Copy signal details to clipboard (simulated)."""
    signal_text = f"""
🎯 FOREX SIGNAL
Pair: {signal.pair}
Action: {signal.signal_type}
Entry: {signal.entry_price:.5f}
Target: {signal.target_price:.5f} (+{pnl_data['pips_to_target']:.1f} pips)
Stop Loss: {signal.stop_loss:.5f} (-{pnl_data['pips_to_stop']:.1f} pips)
Confidence: {signal.confidence:.1%}
Risk:Reward: 1:{pnl_data['risk_reward_ratio']:.1f}
Potential Profit: ${pnl_data['potential_profit']:.2f}
Potential Loss: ${pnl_data['potential_loss']:.2f}
Reason: {signal.reason}
Time: {datetime.now().strftime('%H:%M:%S')}
    """
    
    st.success("📋 Signal details copied! (In a real app, this would copy to clipboard)")
    st.code(signal_text)

def log_detailed_trade(signal, order_id, position_size, pnl_data, status):
    """Log trade with detailed profit/loss information."""
    trade_log = {
        'timestamp': datetime.now(),
        'pair': signal.pair,
        'type': signal.signal_type,
        'confidence': signal.confidence,
        'entry_price': signal.entry_price,
        'target_price': signal.target_price,
        'stop_loss': signal.stop_loss,
        'position_size': position_size,
        'potential_profit': pnl_data['potential_profit'],
        'potential_loss': pnl_data['potential_loss'],
        'risk_reward_ratio': pnl_data['risk_reward_ratio'],
        'pips_to_target': pnl_data['pips_to_target'],
        'pips_to_stop': pnl_data['pips_to_stop'],
        'order_id': order_id,
        'status': status
    }
    
    # Store in session state
    if 'detailed_trade_log' not in st.session_state:
        st.session_state.detailed_trade_log = []
    st.session_state.detailed_trade_log.append(trade_log)

def send_detailed_trade_notification(signal, order_id, position_size, pnl_data):
    """Send detailed trade notification."""
    notification = f"""
🚨 TRADE EXECUTED 🚨

Pair: {signal.pair}
Action: {signal.signal_type}
Entry: {signal.entry_price:.5f}
Target: {signal.target_price:.5f}
Stop: {signal.stop_loss:.5f}
Position: {position_size:,} units
Confidence: {signal.confidence:.1%}

💰 PROFIT/LOSS POTENTIAL:
Max Profit: ${pnl_data['potential_profit']:.2f} (+{pnl_data['pips_to_target']:.1f} pips)
Max Loss: ${pnl_data['potential_loss']:.2f} (-{pnl_data['pips_to_stop']:.1f} pips)
Risk:Reward: 1:{pnl_data['risk_reward_ratio']:.1f}

Order ID: {order_id}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    logger.info(notification)
    st.info("📱 Detailed trade notification sent!")

def execute_trade_with_details(signal, position_size, pnl_data, auto=False):
    """Execute a trade with detailed logging and notifications."""
    try:
        with st.spinner(f"Executing {signal.signal_type} {signal.pair}..."):
            # Execute the trade using the trader
            order_id = trader.execute_signal(signal, manual_override=not auto)
            
            if order_id:
                # Log the successful trade
                log_detailed_trade(signal, order_id, position_size, pnl_data, "EXECUTED")
                
                # Store position-to-signal mapping for enhanced display
                if 'position_signal_mapping' not in st.session_state:
                    st.session_state.position_signal_mapping = {}
                
                # Create a unique key for this position
                position_key = f"{signal.pair}_{signal.signal_type}_{signal.entry_price:.5f}"
                st.session_state.position_signal_mapping[position_key] = {
                    'signal': signal,
                    'position_size': position_size,
                    'pnl_data': pnl_data,
                    'order_id': order_id,
                    'execution_time': datetime.now(),
                    'execution_type': "🤖 AUTO-EXECUTED" if auto else "🚀 MANUALLY EXECUTED"
                }
                
                # Send notification
                send_detailed_trade_notification(signal, order_id, position_size, pnl_data)
                
                # Show success message
                execution_type = "🤖 AUTO-EXECUTED" if auto else "🚀 MANUALLY EXECUTED"
                st.success(f"""
                ✅ **Trade Successfully Executed!**
                
                📊 **Trade Details:**
                • {execution_type}: {signal.signal_type} {signal.pair}
                • Entry Price: {signal.entry_price:.5f}
                • Position Size: {position_size:,} units
                • Order ID: {order_id}
                • Confidence: {signal.confidence:.1%}
                
                💰 **Profit/Loss Potential:**
                • Max Profit: £{pnl_data['potential_profit']:.2f} (+{pnl_data['pips_to_target']:.1f} pips)
                • Max Loss: £{pnl_data['potential_loss']:.2f} (-{pnl_data['pips_to_stop']:.1f} pips)
                • Risk:Reward Ratio: 1:{pnl_data['risk_reward_ratio']:.1f}
                
                🎯 **Next Steps:**
                • Monitor the trade in the "Open Trades" tab
                • Set alerts for target and stop loss levels
                • Consider position sizing for future trades
                """)
                
                # Enhanced logging
                logger.info(f"""
🎯 TRADE EXECUTION SUCCESSFUL 🎯

Execution Type: {execution_type}
Pair: {signal.pair}
Action: {signal.signal_type}
Entry: {signal.entry_price:.5f}
Target: {signal.target_price:.5f}
Stop Loss: {signal.stop_loss:.5f}
Position Size: {position_size:,} units
Confidence: {signal.confidence:.1%}
Order ID: {order_id}

PROFIT/LOSS ANALYSIS:
Potential Profit: £{pnl_data['potential_profit']:.2f} (+{pnl_data['pips_to_target']:.1f} pips)
Potential Loss: £{pnl_data['potential_loss']:.2f} (-{pnl_data['pips_to_stop']:.1f} pips)
Risk:Reward: 1:{pnl_data['risk_reward_ratio']:.1f}

Executed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Manual Override: {not auto}
                """)
                
                return order_id
            else:
                st.error(f"""
                ❌ **Trade Execution Failed**
                
                • Pair: {signal.pair}
                • Action: {signal.signal_type}
                • Entry: {signal.entry_price:.5f}
                
                **Possible reasons:**
                • Insufficient margin
                • Market is closed
                • Invalid price levels
                • OANDA API error
                
                **Next steps:**
                • Check account balance and margin
                • Verify market hours
                • Try again in a few moments
                """)
                
                logger.error(f"""
❌ TRADE EXECUTION FAILED ❌

Pair: {signal.pair}
Action: {signal.signal_type}
Entry: {signal.entry_price:.5f}
Position Size: {position_size:,} units
Confidence: {signal.confidence:.1%}
Manual Override: {not auto}
Failed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                """)
                
                return None
                
    except Exception as e:
        st.error(f"""
        ❌ **Execution Error**
        
        An error occurred while executing the trade:
        {str(e)}
        
        Please try again or contact support if the issue persists.
        """)
        
        logger.error(f"""
💥 TRADE EXECUTION ERROR 💥

Pair: {signal.pair}
Action: {signal.signal_type}
Error: {str(e)}
Manual Override: {not auto}
Error at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """)
        
        return None

def render_account_status():
    """Render enhanced OANDA account status with real-time updates and color-coded P&L."""
    st.markdown("### 💰 Account Status & Margin Management")
    
    if not MODULES_AVAILABLE:
        st.error("Account modules not available")
        return
    
    # Auto-refresh every 10 seconds
    if st.button("🔄 Refresh Account", key="refresh_account"):
        st.cache_data.clear()  # Clear cache to force refresh
        st.rerun()
    
    # Add auto-refresh info
    st.info("💡 **Live Account Data** - Account information updates automatically. Click refresh for latest data.")
    
    try:
        # Get comprehensive account summary using optimized cached function
        account_summary, positions = get_account_data()
        
        if not account_summary:
            st.error("❌ Unable to get account information")
            return
        
        # Main account metrics with enhanced styling
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Account Balance</div>
                <div class="metric-value" style="color: #3b82f6;">${account_summary['balance']:.2f}</div>
                <div class="metric-subtitle">Base balance</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Net Asset Value</div>
                <div class="metric-value" style="color: #10b981;">${account_summary['nav']:.2f}</div>
                <div class="metric-subtitle">Including P&L</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            unrealized_pl = account_summary['unrealized_pl']
            pl_color = "#10b981" if unrealized_pl >= 0 else "#ef4444"
            pl_sign = "+" if unrealized_pl >= 0 else ""
            pl_emoji = "📈" if unrealized_pl >= 0 else "📉"
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Unrealized P&L {pl_emoji}</div>
                <div class="metric-value" style="color: {pl_color};">{pl_sign}${unrealized_pl:.2f}</div>
                <div class="metric-subtitle">Live positions</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            trade_count = account_summary['open_trade_count']
            trade_color = "#f59e0b" if trade_count > 0 else "#6b7280"
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Open Trades</div>
                <div class="metric-value" style="color: {trade_color};">{trade_count}</div>
                <div class="metric-subtitle">Active positions</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Enhanced P&L Display
        if unrealized_pl != 0:
            if unrealized_pl > 0:
                st.success(f"🎉 **Profitable Positions!** You're up ${unrealized_pl:.2f} on open trades")
            else:
                st.error(f"⚠️ **Positions in Loss** You're down ${abs(unrealized_pl):.2f} on open trades")
        
        # Margin information with enhanced visuals
        st.markdown("#### 🛡️ Margin Management")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            margin_used = account_summary['margin_used']
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Margin Used</div>
                <div class="metric-value" style="color: #f59e0b;">${margin_used:.2f}</div>
                <div class="metric-subtitle">Capital locked</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            margin_available = account_summary['margin_available']
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Margin Available</div>
                <div class="metric-value" style="color: #10b981;">${margin_available:.2f}</div>
                <div class="metric-subtitle">Free to trade</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Calculate margin utilization percentage
            margin_utilization = (margin_used / account_summary['balance']) * 100 if account_summary['balance'] > 0 else 0
            utilization_color = "#10b981" if margin_utilization < 30 else "#f59e0b" if margin_utilization < 60 else "#ef4444"
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Margin Utilization</div>
                <div class="metric-value" style="color: {utilization_color};">{margin_utilization:.1f}%</div>
                <div class="metric-subtitle">Of balance used</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            # Safety buffer
            safety_buffer = max(50, account_summary['balance'] * 0.05)
            effective_available = margin_available - safety_buffer
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Effective Available</div>
                <div class="metric-value" style="color: #6366f1;">${effective_available:.2f}</div>
                <div class="metric-subtitle">After safety buffer</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Enhanced margin utilization progress bar
        st.markdown("**Margin Utilization Status:**")
        utilization_pct = min(margin_utilization / 100, 1.0)
        
        # Color coding for margin utilization
        if margin_utilization < 30:
            bar_color = "#059669"  # Green - Safe
            status_text = "🟢 **SAFE** - Low margin usage"
            status_detail = "You have plenty of margin available for new trades"
        elif margin_utilization < 60:
            bar_color = "#f59e0b"  # Yellow - Moderate
            status_text = "🟡 **MODERATE** - Watch margin levels"
            status_detail = "Consider position sizes carefully for new trades"
        elif margin_utilization < 80:
            bar_color = "#f97316"  # Orange - High
            status_text = "🟠 **HIGH** - Margin usage elevated"
            status_detail = "Limited capacity for additional positions"
        else:
            bar_color = "#dc2626"  # Red - Critical
            status_text = "🔴 **CRITICAL** - Very high margin usage"
            status_detail = "Consider closing some positions to reduce risk"
        
        st.progress(utilization_pct)
        st.markdown(f"**{status_text}** ({margin_utilization:.1f}% of balance)")
        st.caption(status_detail)
        
        # Show open positions with enhanced real-time P&L
        if positions:
            st.markdown("#### 📈 Live Open Positions")
            
            position_data = []
            total_unrealized = 0
            
            for pos in positions:
                instrument = pos['instrument'].replace('_', '/')
                long_units = float(pos['long']['units'])
                short_units = float(pos['short']['units'])
                
                if long_units > 0:
                    direction = "🟢 LONG"
                    units = long_units
                    unrealized = float(pos['long'].get('unrealizedPL', 0))
                    avg_price = float(pos['long'].get('averagePrice', 0))
                elif short_units < 0:
                    direction = "🔴 SHORT"
                    units = abs(short_units)
                    unrealized = float(pos['short'].get('unrealizedPL', 0))
                    avg_price = float(pos['short'].get('averagePrice', 0))
                else:
                    continue
                
                total_unrealized += unrealized
                
                # Color code P&L
                pl_color = "🟢" if unrealized >= 0 else "🔴"
                pl_sign = "+" if unrealized >= 0 else ""
                
                # Estimate margin used for this position
                estimated_margin = trader.calculate_margin_required(instrument.replace('/', '_'), int(units))
                
                position_data.append({
                    'Pair': instrument,
                    'Direction': direction,
                    'Units': f"{units:,.0f}",
                    'Avg Price': f"{avg_price:.5f}",
                    'Unrealized P&L': f"{pl_color} {pl_sign}${unrealized:.2f}",
                    'Est. Margin': f"${estimated_margin:.2f}"
                })
            
            if position_data:
                # Create a more visually appealing table
                df_positions = pd.DataFrame(position_data)
                st.dataframe(df_positions, use_container_width=True)
                
                # Position summary with color coding
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Positions", len(positions))
                
                with col2:
                    pl_delta = f"{'+' if total_unrealized >= 0 else ''}${total_unrealized:.2f}"
                    st.metric("Total Unrealized P&L", f"${total_unrealized:.2f}", delta=pl_delta)
                
                with col3:
                    roi = (total_unrealized / account_summary['balance']) * 100 if account_summary['balance'] > 0 else 0
                    roi_color = "normal" if roi >= 0 else "inverse"
                    st.metric("Portfolio ROI", f"{roi:+.2f}%")
                
                with col4:
                    # Calculate average position size
                    avg_position = sum([float(p['Units'].replace(',', '')) for p in position_data]) / len(position_data)
                    st.metric("Avg Position Size", f"{avg_position:,.0f} units")
                
                # Real-time P&L alerts
                if total_unrealized > 10:
                    st.success(f"🎉 **Great job!** Your positions are profitable by ${total_unrealized:.2f}")
                elif total_unrealized < -20:
                    st.warning(f"⚠️ **Monitor closely** - Positions are down ${abs(total_unrealized):.2f}")
        
        else:
            st.markdown("""
            <div class="modern-card" style="text-align: center; padding: 3rem;">
                <h3 style="color: #64748b; margin-bottom: 1rem;">📭 No Open Positions</h3>
                <p style="color: #64748b; margin: 0;">All positions are closed. Ready for new trading opportunities!</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Risk warnings with enhanced styling
        if margin_utilization > 80:
            st.error("🚨 **HIGH MARGIN UTILIZATION WARNING**: Consider closing some positions to reduce risk.")
        elif margin_utilization > 60:
            st.warning("⚠️ **MODERATE MARGIN USAGE**: Monitor positions closely and avoid over-leveraging.")
        elif effective_available < 50:
            st.warning("⚠️ **LOW AVAILABLE MARGIN**: Limited capacity for new trades.")
        
        # Account health summary with enhanced scoring
        st.markdown("#### 🏥 Account Health Score")
        
        health_score = 100
        health_issues = []
        
        if margin_utilization > 80:
            health_score -= 30
            health_issues.append("High margin utilization")
        elif margin_utilization > 60:
            health_score -= 15
            health_issues.append("Moderate margin utilization")
        
        if account_summary['balance'] < 500:
            health_score -= 20
            health_issues.append("Low account balance")
        
        if len(positions) >= 3:
            health_score -= 10
            health_issues.append("Maximum recommended positions reached")
        
        if unrealized_pl < -50:
            health_score -= 20
            health_issues.append("Significant unrealized losses")
        elif unrealized_pl < -20:
            health_score -= 10
            health_issues.append("Moderate unrealized losses")
        
        # Display health score with color coding
        if health_score >= 80:
            health_color = "#10b981"
            health_status = "Excellent"
            health_emoji = "🟢"
        elif health_score >= 60:
            health_color = "#f59e0b"
            health_status = "Good"
            health_emoji = "🟡"
        elif health_score >= 40:
            health_color = "#f97316"
            health_status = "Fair"
            health_emoji = "🟠"
        else:
            health_color = "#ef4444"
            health_status = "Poor"
            health_emoji = "🔴"
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.8) 100%); 
                    border-left: 6px solid {health_color}; border-radius: 15px; padding: 2rem; margin: 1rem 0;">
            <h4 style="color: {health_color}; margin: 0;">
                {health_emoji} Account Health Score: {health_score}/100 ({health_status})
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
        if health_issues:
            st.markdown("**Areas for improvement:**")
            for issue in health_issues:
                st.markdown(f"• {issue}")
        else:
            st.success("✅ **Perfect!** Your account is in excellent health with no issues detected.")
        
        # Add timestamp for last update
        from datetime import datetime
        st.caption(f"📊 Last updated: {datetime.now().strftime('%H:%M:%S')} - Data refreshes automatically")
        
    except Exception as e:
        st.error(f"Error getting account status: {e}")
        st.info("💡 Try refreshing the page or check your internet connection.")

def render_backtest_results():
    """Render backtesting results."""
    st.markdown("### 📈 Backtesting Analysis")
    
    if not MODULES_AVAILABLE:
        st.error("Backtesting modules not available")
        return
    
    # Get current market status for display
    current_market_status = get_market_status()
    
    # Enhanced backtest settings
    col1, col2, col3 = st.columns(3)
    with col1:
        backtest_period = st.selectbox("Backtest Period", [
            "1 Month", 
            "3 Months", 
            "6 Months", 
            "1 Year"
        ], index=0, key="backtest_period")
    with col2:
        confidence_levels = st.multiselect("Confidence Levels", 
                                         [0.15, 0.20, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75], 
                                         default=[0.20, 0.35, 0.55, 0.65], 
                                         key="confidence_levels",
                                         help="Lower confidence levels will show more trades")
    with col3:
        auto_execute_threshold = st.slider("Auto-Execute Threshold", 0.60, 0.90, 0.75, 0.05, 
                                         key="auto_execute_threshold",
                                         help="Trades above this confidence will auto-execute")
    
    # Add quick demo button
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Run Enhanced Backtest", key="run_backtest"):
            run_backtest_analysis(backtest_period, confidence_levels, auto_execute_threshold)
    
    with col2:
        if st.button("⚡ Quick Demo Backtest", key="demo_backtest", help="Run quick test with guaranteed trades"):
            st.info("🚀 Running demo backtest with low confidence levels to show functionality...")
            demo_confidence_levels = [0.10, 0.20, 0.30, 0.40, 0.50]
            run_backtest_analysis("1 Month", demo_confidence_levels, 0.40)

def run_backtest_analysis(backtest_period, confidence_levels, auto_execute_threshold):
    """Run the actual backtest analysis."""
    # Map period to days
    period_days = {
        "1 Month": 30,
        "3 Months": 90,
        "6 Months": 180,
        "1 Year": 365
    }
    
    days = period_days[backtest_period]
    
    with st.spinner(f"Running {backtest_period.lower()} backtest..."):
        # Create custom backtester with shorter period
        custom_backtester = ForexBacktester(initial_balance=1000.0)
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Show backtest parameters
        st.info(f"""
        **Backtest Parameters:**
        • Period: {backtest_period} ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})
        • Confidence Levels: {[f'{c:.0%}' for c in confidence_levels]}
        • Auto-Execute Threshold: {auto_execute_threshold:.0%}
        """)
        
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, confidence in enumerate(confidence_levels):
            status_text.text(f"Testing confidence level {confidence:.0%}...")
            progress_bar.progress((i + 1) / len(confidence_levels))
            
            # Run backtest for each confidence level using the correct method
            result = custom_backtester.backtest_confidence_threshold(
                confidence_threshold=confidence,
                start_date=start_date,
                end_date=end_date
            )
            results.append(result)
            
            # Show immediate feedback
            st.write(f"✅ {confidence:.0%} confidence: {result.total_trades} trades, {result.win_rate:.1%} win rate, {result.total_return:.1%} return")
        
        progress_bar.empty()
        status_text.empty()
        
        # Check if any results have trades
        total_trades_all = sum(r.total_trades for r in results)
        
        if total_trades_all == 0:
            st.warning(f"""
            ⚠️ **No trades were executed in the backtest!**
            
            This could be because:
            • Signal generator didn't produce signals meeting the confidence criteria
            • Historical data issues for the selected period
            • Confidence thresholds are too high
            
            **Suggestions:**
            • Try lowering confidence levels (add 0.15, 0.20)
            • Use a longer backtest period
            • Check if signals are being generated in the Live Signals tab
            """)
            
            # Show a quick test with very low confidence
            st.markdown("#### 🔍 Quick Test with Low Confidence (15%)")
            test_result = custom_backtester.backtest_confidence_threshold(
                confidence_threshold=0.15,
                start_date=start_date,
                end_date=end_date
            )
            st.write(f"Test result: {test_result.total_trades} trades at 15% confidence")
        
        # Create results DataFrame
        df_results = pd.DataFrame([
            {
                'Confidence': f"{r.confidence_threshold:.0%}",
                'Trades': r.total_trades,
                'Win Rate': f"{r.win_rate:.1%}" if r.total_trades > 0 else "N/A",
                'Return': f"{r.total_return:.1%}",
                'Final Balance': f"£{r.final_balance:.0f}",
                'Max Drawdown': f"{r.max_drawdown:.1%}" if r.total_trades > 0 else "N/A",
                'Profit Factor': f"{r.profit_factor:.2f}" if r.total_trades > 0 and r.profit_factor != float('inf') else "N/A",
                'Auto-Execute?': "✅ YES" if r.confidence_threshold >= auto_execute_threshold else "❌ NO"
            }
            for r in results
        ])
        
        st.markdown(f"#### 📊 {backtest_period} Backtest Results")
        st.dataframe(df_results, use_container_width=True)
        
        # Highlight auto-execute candidates
        auto_execute_results = [r for r in results if r.confidence_threshold >= auto_execute_threshold]
        
        if auto_execute_results:
            st.markdown("#### 🤖 Auto-Execute Analysis")
            best_auto = max(auto_execute_results, key=lambda x: x.total_return)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Best Auto-Execute Confidence", f"{best_auto.confidence_threshold:.0%}")
            with col2:
                st.metric("Expected Return", f"{best_auto.total_return:.1%}")
            with col3:
                st.metric("Win Rate", f"{best_auto.win_rate:.1%}")
            
            st.success(f"✅ Trades with ≥{auto_execute_threshold:.0%} confidence will auto-execute when market opens!")
        
        # Performance comparison chart
        if total_trades_all > 0:
            fig = go.Figure()
            
            # Add bars for each confidence level
            colors = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6', '#8b5cf6']
            for i, r in enumerate(results):
                color = colors[i % len(colors)]
                fig.add_trace(go.Bar(
                    x=[f"{r.confidence_threshold:.0%}"],
                    y=[r.total_return],
                    name=f"{r.confidence_threshold:.0%} Confidence",
                    marker_color=color,
                    text=f"{r.total_return:.1%}",
                    textposition='auto',
                ))
            
            # Highlight auto-execute threshold
            fig.add_vline(
                x=auto_execute_threshold - 0.05,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Auto-Execute Threshold ({auto_execute_threshold:.0%})"
            )
            
            fig.update_layout(
                title=f"{backtest_period} Returns by Confidence Level",
                xaxis_title="Confidence Threshold",
                yaxis_title="Total Return (%)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Market timing analysis (always show, not just when button is clicked)
    st.markdown("#### ⏰ Market Timing Analysis")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: {current_market_status['bg_color']}; border-radius: 10px;">
            <h4 style="color: {current_market_status['color']}; margin: 0;">Market Status</h4>
            <p style="font-size: 1.5rem; color: {current_market_status['color']}; margin: 0;">{current_market_status['message']}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        auto_status = "Active" if current_market_status['is_open'] else "Waiting for market open"
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: #f8fafc; border-radius: 10px;">
            <h4 style="color: #374151; margin: 0;">Auto-Execute</h4>
            <p style="font-size: 1.2rem; color: #374151; margin: 0;">{auto_status}</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        next_info = current_market_status.get('next_open', 'Market is open')
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: #fffbeb; border-radius: 10px;">
            <h4 style="color: #92400e; margin: 0;">Next Open</h4>
            <p style="font-size: 1.2rem; color: #92400e; margin: 0;">{next_info}</p>
        </div>
        """, unsafe_allow_html=True)

def check_and_auto_execute_trades():
    """Check for high-confidence signals and auto-execute when market is open."""
    if not MODULES_AVAILABLE:
        return
    
    # Check if market is open
    from datetime import datetime, time
    import pytz
    
    utc_now = datetime.now(pytz.UTC)
    current_time = utc_now.time()
    
    # Major forex market hours (UTC)
    london_open = time(8, 0)
    london_close = time(17, 0)
    ny_open = time(13, 0)
    ny_close = time(22, 0)
    
    market_open = (london_open <= current_time <= london_close) or (ny_open <= current_time <= ny_close)
    
    if not market_open:
        return
    
    # Get current signals
    signals = get_live_signals(min_confidence=0.75)  # High confidence only
    
    auto_executed = []
    for signal in signals:
        if signal.confidence >= 0.75:  # Auto-execute threshold
            try:
                # Calculate position size (5% risk) - FIXED CALCULATION
                if 'JPY' in signal.pair:
                    stop_pips = abs(signal.entry_price - signal.stop_loss) / 0.01
                else:
                    stop_pips = abs(signal.entry_price - signal.stop_loss) / 0.0001
                
                position_size = calculate_position_size_from_risk(1000, 5, stop_pips)
                pnl_data = calculate_trade_pnl(signal, position_size)
                
                # Execute the trade
                order_id = trader.execute_signal(signal)
                
                if order_id:
                    auto_executed.append({
                        'pair': signal.pair,
                        'type': signal.signal_type,
                        'confidence': signal.confidence,
                        'order_id': order_id,
                        'position_size': position_size,
                        'potential_profit': pnl_data['potential_profit'],
                        'potential_loss': pnl_data['potential_loss']
                    })
                    
                    # Log the auto-execution
                    log_detailed_trade(signal, order_id, position_size, pnl_data, "AUTO_EXECUTED")
                    
                    # Store position-to-signal mapping for enhanced display
                    if 'position_signal_mapping' not in st.session_state:
                        st.session_state.position_signal_mapping = {}
                    
                    # Create a unique key for this position
                    position_key = f"{signal.pair}_{signal.signal_type}_{signal.entry_price:.5f}"
                    st.session_state.position_signal_mapping[position_key] = {
                        'signal': signal,
                        'position_size': position_size,
                        'pnl_data': pnl_data,
                        'order_id': order_id,
                        'execution_time': datetime.now(),
                        'execution_type': "🤖 AUTO-EXECUTED"
                    }
                    
            except Exception as e:
                st.error(f"Auto-execution failed for {signal.pair}: {e}")
    
    # Display auto-executed trades
    if auto_executed:
        st.markdown("#### 🤖 Auto-Executed Trades")
        
        for trade in auto_executed:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); color: white; padding: 1.5rem; border-radius: 12px; margin: 1rem 0;">
                <h4 style="margin: 0; font-size: 1.4rem;">✅ AUTO-EXECUTED: {trade['type']} {trade['pair']}</h4>
                <p style="margin: 0.5rem 0; font-size: 1.1rem;">
                    <strong>Confidence:</strong> {trade['confidence']:.1%} | 
                    <strong>Position:</strong> {trade['position_size']:,} units | 
                    <strong>Order ID:</strong> {trade['order_id']}
                </p>
                <p style="margin: 0; font-size: 1rem;">
                    <strong>Potential:</strong> +£{trade['potential_profit']:.2f} / -£{trade['potential_loss']:.2f}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.success(f"🎯 Successfully auto-executed {len(auto_executed)} high-confidence trades!")
    
    return auto_executed

def render_trade_log():
    """Render trade execution log."""
    st.markdown("### 📋 Trade Log")
    
    if 'detailed_trade_log' in st.session_state and st.session_state.detailed_trade_log:
        df_log = pd.DataFrame(st.session_state.detailed_trade_log)
        st.dataframe(df_log, use_container_width=True)
    else:
        st.info("No trades executed yet.")

def set_price_alert(signal):
    """Set a price alert for the signal."""
    st.markdown("#### ⚠️ Price Alert Configuration")
    
    # Check if alert already exists for this pair
    existing_alerts = st.session_state.get('alerts', [])
    existing_alert = next((alert for alert in existing_alerts if alert['pair'] == signal.pair), None)
    
    if existing_alert:
        st.warning(f"⚠️ Alert already exists for {signal.pair} at {existing_alert['price']:.5f}")
        if st.button("🗑️ Remove Existing Alert", key=f"remove_alert_{signal.pair}"):
            st.session_state.alerts = [alert for alert in existing_alerts if alert['pair'] != signal.pair]
            st.success(f"✅ Removed alert for {signal.pair}")
            st.rerun()
        return
    
    # Alert configuration
    col1, col2 = st.columns(2)
    
    with col1:
        alert_type = st.selectbox("Alert Type", [
            "Entry Price Alert",
            "Target Price Alert", 
            "Stop Loss Alert",
            "Custom Price Alert"
        ], key=f"alert_type_{signal.pair}")
    
    with col2:
        if alert_type == "Entry Price Alert":
            alert_price = signal.entry_price
        elif alert_type == "Target Price Alert":
            alert_price = signal.target_price
        elif alert_type == "Stop Loss Alert":
            alert_price = signal.stop_loss
        else:
            alert_price = st.number_input("Custom Price", value=signal.entry_price, format="%.5f", key=f"custom_price_{signal.pair}")
    
    st.info(f"""
    **Alert Configuration:**
    • Pair: {signal.pair}
    • Alert Price: {alert_price:.5f}
    • Current Entry: {signal.entry_price:.5f}
    • Type: {alert_type}
    """)
    
    if st.button("🔔 Set Alert", key=f"set_alert_{signal.pair}"):
        # Store alert
        if 'alerts' not in st.session_state:
            st.session_state.alerts = []
        
        alert_data = {
            'pair': signal.pair,
            'price': alert_price,
            'type': alert_type,
            'signal_type': signal.signal_type,
            'confidence': signal.confidence,
            'timestamp': datetime.now(),
            'triggered': False
        }
        
        st.session_state.alerts.append(alert_data)
        
        # Log the alert
        logger.info(f"""
🔔 PRICE ALERT SET 🔔

Pair: {signal.pair}
Alert Price: {alert_price:.5f}
Alert Type: {alert_type}
Signal: {signal.signal_type}
Confidence: {signal.confidence:.1%}
Set at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """)
        
        st.success(f"""
        ✅ **Price Alert Set Successfully!**
        
        🔔 **Alert Details:**
        • {signal.pair} at {alert_price:.5f}
        • Type: {alert_type}
        • Will notify when price reaches target
        
        💡 You can view all alerts in the Trade Log tab.
        """)
        
        st.rerun()
    
    # Show existing alerts
    if existing_alerts:
        st.markdown("#### 📋 Your Active Alerts")
        for i, alert in enumerate(existing_alerts):
            status = "🔴 Triggered" if alert.get('triggered', False) else "🟢 Active"
            st.write(f"• {alert['pair']} at {alert['price']:.5f} ({alert['type']}) - {status}")

def render_open_trades():
    """Render open trades monitoring with manual close functionality."""
    st.markdown("### 📊 Open Trades Monitor")
    
    if not MODULES_AVAILABLE:
        st.error("Trading modules not available")
        return
    
    try:
        # Get open positions
        positions = trader.get_open_positions()
        account_summary = trader.get_account_summary()
        
        if not positions:
            st.markdown("""
            <div class="modern-card slide-in" style="text-align: center;">
                <h3 style="color: #64748b; font-size: 2rem; margin-bottom: 1rem;">📭 No Open Trades</h3>
                <p style="color: #64748b; font-size: 1.2rem; margin: 0;">All positions are closed. Ready for new opportunities!</p>
            </div>
            """, unsafe_allow_html=True)
            return
        
        # Summary metrics
        total_unrealized = sum([
            float(pos.get('long', {}).get('unrealizedPL', 0)) + 
            float(pos.get('short', {}).get('unrealizedPL', 0)) 
            for pos in positions
        ])
        
        total_margin_used = account_summary.get('margin_used', 0)
        
        # Display summary cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Open Positions</div>
                <div class="metric-value" style="color: #3b82f6;">{len(positions)}</div>
                <div class="metric-subtitle">Active trades</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            pnl_color = "#10b981" if total_unrealized >= 0 else "#ef4444"
            pnl_sign = "+" if total_unrealized >= 0 else ""
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Total P&L</div>
                <div class="metric-value" style="color: {pnl_color};">{pnl_sign}£{total_unrealized:.2f}</div>
                <div class="metric-subtitle">Unrealized</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Margin Used</div>
                <div class="metric-value" style="color: #f59e0b;">£{total_margin_used:.2f}</div>
                <div class="metric-subtitle">Of £{account_summary.get('balance', 1000):.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            margin_pct = (total_margin_used / account_summary.get('balance', 1000)) * 100
            margin_color = "#10b981" if margin_pct < 30 else "#f59e0b" if margin_pct < 60 else "#ef4444"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Margin Usage</div>
                <div class="metric-value" style="color: {margin_color};">{margin_pct:.1f}%</div>
                <div class="metric-subtitle">Risk level</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Individual position cards
        st.markdown("#### 🎯 Individual Positions")
        
        for i, position in enumerate(positions):
            render_position_card(position, i)
            
    except Exception as e:
        st.error(f"Error loading open trades: {e}")

def render_position_card(position, index):
    """Render individual position card with close functionality and enhanced signal data."""
    instrument = position['instrument'].replace('_', '/')
    
    # Determine position details
    long_units = float(position['long']['units'])
    short_units = float(position['short']['units'])
    
    if long_units > 0:
        direction = "BUY"
        units = long_units
        unrealized = float(position['long'].get('unrealizedPL', 0))
        avg_price = float(position['long'].get('averagePrice', 0))
        direction_color = "#10b981"
        direction_bg = "linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%)"
        direction_emoji = "🟢"
    elif short_units < 0:
        direction = "SELL"
        units = abs(short_units)
        unrealized = float(position['short'].get('unrealizedPL', 0))
        avg_price = float(position['short'].get('averagePrice', 0))
        direction_color = "#ef4444"
        direction_bg = "linear-gradient(135deg, #fef2f2 0%, #fecaca 100%)"
        direction_emoji = "🔴"
    else:
        return  # No position
    
    # Calculate current price and movement
    try:
        current_price = trader.get_current_price(instrument.replace('/', '_'))
        if current_price:
            price_change = current_price - avg_price
            price_change_pct = (price_change / avg_price) * 100 if avg_price > 0 else 0
        else:
            current_price = avg_price
            price_change = 0
            price_change_pct = 0
    except:
        current_price = avg_price
        price_change = 0
        price_change_pct = 0
    
    # Try to find original signal data for this position
    original_signal = None
    target_price = None
    stop_loss = None
    pips_to_target = None
    pips_to_stop = None
    
    # First, try the position-to-signal mapping (most accurate)
    if 'position_signal_mapping' in st.session_state:
        # Try different possible keys for this position
        possible_keys = [
            f"{instrument}_{direction}_{avg_price:.5f}",
            f"{instrument}_{direction}_{avg_price:.4f}",
            f"{instrument}_{direction}_{avg_price:.3f}"
        ]
        
        for key in possible_keys:
            if key in st.session_state.position_signal_mapping:
                mapping_data = st.session_state.position_signal_mapping[key]
                signal = mapping_data['signal']
                original_signal = {
                    'pair': signal.pair,
                    'type': signal.signal_type,
                    'confidence': signal.confidence,
                    'entry_price': signal.entry_price,
                    'target_price': signal.target_price,
                    'stop_loss': signal.stop_loss,
                    'pips_to_target': mapping_data['pnl_data']['pips_to_target'],
                    'pips_to_stop': mapping_data['pnl_data']['pips_to_stop'],
                    'status': 'EXECUTED',
                    'execution_type': mapping_data['execution_type'],
                    'order_id': mapping_data['order_id']
                }
                target_price = signal.target_price
                stop_loss = signal.stop_loss
                pips_to_target = mapping_data['pnl_data']['pips_to_target']
                pips_to_stop = mapping_data['pnl_data']['pips_to_stop']
                break
    
    # Fallback: Look for the original signal in trade log
    if not original_signal and 'detailed_trade_log' in st.session_state:
        for trade in st.session_state.detailed_trade_log:
            if (trade['pair'] == instrument and 
                trade['type'] == direction and 
                trade['status'] in ['EXECUTED', 'AUTO_EXECUTED'] and
                abs(trade['entry_price'] - avg_price) < 0.0001):  # Match entry price
                original_signal = trade
                target_price = trade['target_price']
                stop_loss = trade['stop_loss']
                pips_to_target = trade['pips_to_target']
                pips_to_stop = trade['pips_to_stop']
                break
    
    # If no original signal found, estimate target and stop based on typical patterns
    if not original_signal:
        # Calculate pip value for this pair
        if 'JPY' in instrument:
            pip_value = 0.01
        else:
            pip_value = 0.0001
        
        # Estimate typical targets (30-50 pips for target, 20-30 pips for stop)
        if direction == "BUY":
            target_price = avg_price + (40 * pip_value)  # 40 pips target
            stop_loss = avg_price - (25 * pip_value)     # 25 pips stop
            pips_to_target = 40
            pips_to_stop = 25
        else:  # SELL
            target_price = avg_price - (40 * pip_value)  # 40 pips target
            stop_loss = avg_price + (25 * pip_value)     # 25 pips stop
            pips_to_target = 40
            pips_to_stop = 25
    
    # Calculate current distance to target and stop
    if target_price and stop_loss:
        if 'JPY' in instrument:
            pip_value = 0.01
        else:
            pip_value = 0.0001
        
        if direction == "BUY":
            current_pips_to_target = (target_price - current_price) / pip_value
            current_pips_to_stop = (current_price - stop_loss) / pip_value
        else:  # SELL
            current_pips_to_target = (current_price - target_price) / pip_value
            current_pips_to_stop = (stop_loss - current_price) / pip_value
        
        # Calculate progress towards target
        total_distance = pips_to_target + pips_to_stop if pips_to_target and pips_to_stop else 65
        progress_pips = pips_to_stop - current_pips_to_stop if current_pips_to_stop else 0
        progress_pct = (progress_pips / total_distance) * 100 if total_distance > 0 else 0
        progress_pct = max(0, min(100, progress_pct))  # Clamp between 0-100%
    else:
        current_pips_to_target = 0
        current_pips_to_stop = 0
        progress_pct = 0
    
    # Estimate margin used
    estimated_margin = trader.calculate_margin_required(instrument.replace('/', '_'), int(units))
    
    # P&L styling
    pnl_color = "#10b981" if unrealized >= 0 else "#ef4444"
    pnl_sign = "+" if unrealized >= 0 else ""
    pnl_class = "trade-profit" if unrealized >= 0 else "trade-loss"
    
    # Position card header
    st.markdown(f"""
    <div class="modern-card slide-in" style="background: {direction_bg}; border-left: 6px solid {direction_color}; padding: 2rem; border-radius: 20px; margin: 2rem 0;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
            <h3 style="color: {direction_color}; font-size: 2rem; margin: 0;">
                {direction_emoji} {direction} {instrument}
            </h3>
            <div class="{pnl_class}" style="padding: 0.5rem 1rem; border-radius: 20px; font-weight: 600;">
                {pnl_sign}£{unrealized:.2f}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Position metrics using Streamlit columns
    st.markdown("#### 📊 Position Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Position Size", f"{units:,.0f} units")
    
    with col2:
        st.metric("Entry Price", f"{avg_price:.5f}", "entrance")
    
    with col3:
        price_delta = f"{'+' if price_change >= 0 else ''}{price_change_pct:.2f}%"
        st.metric("Current Price", f"{current_price:.5f}", price_delta)
    
    with col4:
        st.metric("Margin Used", f"£{estimated_margin:.0f}", "estimated")
    
    # Enhanced Target & Stop Loss Section
    if target_price and stop_loss:
        st.markdown("#### 🎯 Target & Stop Analysis")
        
        # Determine if we're closer to target or stop
        target_distance = abs(current_pips_to_target)
        stop_distance = abs(current_pips_to_stop)
        
        if current_pips_to_target > 0:
            target_status = f"🎯 {current_pips_to_target:.1f} pips to target"
            target_color = "#10b981"
        else:
            target_status = f"✅ Target exceeded by {abs(current_pips_to_target):.1f} pips!"
            target_color = "#059669"
        
        if current_pips_to_stop > 0:
            stop_status = f"🛡️ {current_pips_to_stop:.1f} pips above stop"
            stop_color = "#10b981"
        else:
            stop_status = f"⚠️ {abs(current_pips_to_stop):.1f} pips below stop!"
            stop_color = "#ef4444"
        
        # Progress bar color
        if progress_pct >= 70:
            progress_color = "#10b981"  # Green - close to target
        elif progress_pct >= 30:
            progress_color = "#f59e0b"  # Yellow - making progress
        else:
            progress_color = "#ef4444"  # Red - closer to stop
        
        # Target & Stop metrics using Streamlit columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Target Price", f"{target_price:.5f}", target_status)
        
        with col2:
            st.metric("Stop Loss", f"{stop_loss:.5f}", stop_status)
        
        with col3:
            st.metric("Progress to Target", f"{progress_pct:.1f}%", "of total distance")
        
        with col4:
            if pips_to_target and pips_to_stop and pips_to_stop > 0:
                risk_reward = pips_to_target / pips_to_stop
                st.metric("Risk:Reward", f"1:{risk_reward:.1f}", "original setup")
            else:
                st.metric("Risk:Reward", "N/A", "data unavailable")
        
        # Progress bar
        st.markdown("**Progress to Target:**")
        progress_normalized = progress_pct / 100
        st.progress(progress_normalized)
        
        # Price levels
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**Stop Loss:** {stop_loss:.5f}")
        with col2:
            st.markdown(f"**Current:** {current_price:.5f}")
        with col3:
            st.markdown(f"**Target:** {target_price:.5f}")
    
    # Signal source information
    st.markdown("#### 📊 Signal Information")
    if original_signal:
        confidence = original_signal.get('confidence', 0)
        confidence_pct = confidence * 100 if confidence <= 1 else confidence
        execution_type = original_signal.get('execution_type', 'EXECUTED')
        order_id = original_signal.get('order_id', 'N/A')
        
        st.success("📊 **Original Signal Data Found**")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Confidence:** {confidence_pct:.1f}%")
            st.write(f"**Entry:** {original_signal['entry_price']:.5f}")
        with col2:
            st.write(f"**Target Pips:** +{original_signal['pips_to_target']:.0f}")
            st.write(f"**Stop Pips:** -{original_signal['pips_to_stop']:.0f}")
        with col3:
            st.write(f"**Execution:** {execution_type}")
            st.write(f"**Order ID:** {order_id}")
    else:
        st.warning("⚠️ **Estimated Targets**")
        st.info(f"""
        Original signal data not found. Showing estimated targets based on typical {instrument} patterns.
        
        **Estimated:** 40 pips target, 25 pips stop loss (1:1.6 risk/reward)
        """)
    
    # Action buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button(f"🚨 Close Position", key=f"close_{index}", help="Close this position immediately"):
            close_position(instrument, direction, units)
    
    with col2:
        if st.button(f"📊 Position Details", key=f"details_{index}", help="View detailed position information"):
            show_position_details(position, instrument, direction, units)
    
    with col3:
        if st.button(f"⚠️ Set Stop Loss", key=f"stop_{index}", help="Modify stop loss"):
            set_stop_loss(instrument, direction)
    
    with col4:
        if st.button(f"🎯 Set Take Profit", key=f"profit_{index}", help="Modify take profit"):
            set_take_profit(instrument, direction)

def close_position(instrument, direction, units):
    """Close a position manually."""
    try:
        with st.spinner(f"Closing {direction} position for {instrument}..."):
            # Create opposite order to close position
            opposite_direction = "SELL" if direction == "BUY" else "BUY"
            
            # Use OANDA's position close endpoint
            order_id = trader.close_position(instrument.replace('/', '_'))
            
            if order_id:
                st.success(f"""
                ✅ **Position Closed Successfully!**
                
                • Pair: {instrument}
                • Direction: {direction}
                • Units: {units:,.0f}
                • Order ID: {order_id}
                """)
                
                # Log the manual close
                st.session_state.manual_closes = st.session_state.get('manual_closes', [])
                st.session_state.manual_closes.append({
                    'timestamp': datetime.now(),
                    'instrument': instrument,
                    'direction': direction,
                    'units': units,
                    'order_id': order_id,
                    'reason': 'MANUAL_CLOSE'
                })
                
                # Refresh the page to update positions
                st.rerun()
            else:
                st.error("❌ Failed to close position. Please try again or contact support.")
                
    except Exception as e:
        st.error(f"Error closing position: {e}")

def show_position_details(position, instrument, direction, units):
    """Show detailed position information."""
    st.markdown("#### 📊 Position Details")
    
    # Create detailed info
    details = {
        'Instrument': instrument,
        'Direction': direction,
        'Units': f"{units:,.0f}",
        'Unrealized P&L': f"£{float(position.get('long' if direction == 'BUY' else 'short', {}).get('unrealizedPL', 0)):.2f}",
        'Average Price': f"{float(position.get('long' if direction == 'BUY' else 'short', {}).get('averagePrice', 0)):.5f}",
        'Trade IDs': ', '.join(position.get('long' if direction == 'BUY' else 'short', {}).get('tradeIDs', [])),
    }
    
    # Display as formatted table
    for key, value in details.items():
        st.write(f"**{key}:** {value}")

def set_stop_loss(instrument, direction):
    """Set or modify stop loss."""
    st.markdown("#### ⚠️ Set Stop Loss")
    
    current_price = trader.get_current_price(instrument.replace('/', '_'))
    
    if direction == "BUY":
        suggested_stop = current_price * 0.99  # 1% below current
        st.write(f"Current price: {current_price:.5f}")
        stop_price = st.number_input("Stop Loss Price", value=suggested_stop, format="%.5f", key=f"stop_{instrument}")
    else:
        suggested_stop = current_price * 1.01  # 1% above current
        st.write(f"Current price: {current_price:.5f}")
        stop_price = st.number_input("Stop Loss Price", value=suggested_stop, format="%.5f", key=f"stop_{instrument}")
    
    if st.button("Set Stop Loss"):
        st.info(f"Stop loss would be set at {stop_price:.5f} (Feature coming soon)")

def set_take_profit(instrument, direction):
    """Set or modify take profit."""
    st.markdown("#### 🎯 Set Take Profit")
    
    current_price = trader.get_current_price(instrument.replace('/', '_'))
    
    if direction == "BUY":
        suggested_profit = current_price * 1.02  # 2% above current
        st.write(f"Current price: {current_price:.5f}")
        profit_price = st.number_input("Take Profit Price", value=suggested_profit, format="%.5f", key=f"profit_{instrument}")
    else:
        suggested_profit = current_price * 0.98  # 2% below current
        st.write(f"Current price: {current_price:.5f}")
        profit_price = st.number_input("Take Profit Price", value=suggested_profit, format="%.5f", key=f"profit_{instrument}")
    
    if st.button("Set Take Profit"):
        st.info(f"Take profit would be set at {profit_price:.5f} (Feature coming soon)")

def get_market_status():
    """Get current market status with session detection."""
    from datetime import datetime, time
    import pytz
    
    # Get current UTC time
    utc_now = datetime.now(pytz.UTC)
    current_time = utc_now.time()
    current_weekday = utc_now.weekday()  # 0=Monday, 6=Sunday
    
    # Forex market hours (UTC)
    # Market opens Sunday 22:00 UTC and closes Friday 22:00 UTC
    
    # Check if it's weekend (market closed)
    if current_weekday == 5:  # Saturday
        if current_time >= time(22, 0):  # After Friday 22:00 UTC
            # Market closed for weekend
            next_open = "Sunday 22:00 UTC"
            hours_until_open = (6 - current_weekday) * 24 + (22 - current_time.hour)
            return {
                'is_open': False,
                'status': 'CLOSED',
                'message': 'Market Closed',
                'detail': 'Weekend - Market closed',
                'next_open': next_open,
                'time_until_open': f"{hours_until_open:.0f} hours",
                'color': 'white',
                'bg_color': '#ef4444'
            }
    elif current_weekday == 6:  # Sunday
        if current_time < time(22, 0):  # Before Sunday 22:00 UTC
            # Market still closed
            hours_until_open = 22 - current_time.hour
            return {
                'is_open': False,
                'status': 'CLOSED',
                'message': 'Market Closed',
                'detail': 'Weekend - Opens Sunday 22:00 UTC',
                'next_open': 'Sunday 22:00 UTC',
                'time_until_open': f"{hours_until_open:.0f} hours",
                'color': 'white',
                'bg_color': '#ef4444'
            }
    elif current_weekday == 5 and current_time >= time(22, 0):  # Friday after 22:00 UTC
        # Market closed for weekend
        return {
            'is_open': False,
            'status': 'CLOSED',
            'message': 'Market Closed',
            'detail': 'Weekend - Reopens Sunday 22:00 UTC',
            'next_open': 'Sunday 22:00 UTC',
            'time_until_open': '48+ hours',
            'color': 'white',
            'bg_color': '#ef4444'
        }
    
    # Market is open during weekdays (Monday-Friday) and Sunday after 22:00
    # Determine active sessions
    sessions = []
    
    # Sydney: 22:00-07:00 UTC
    if time(22, 0) <= current_time or current_time <= time(7, 0):
        sessions.append("Sydney")
    
    # Tokyo: 00:00-09:00 UTC
    if time(0, 0) <= current_time <= time(9, 0):
        sessions.append("Tokyo")
    
    # London: 08:00-17:00 UTC
    if time(8, 0) <= current_time <= time(17, 0):
        sessions.append("London")
    
    # New York: 13:00-22:00 UTC
    if time(13, 0) <= current_time <= time(22, 0):
        sessions.append("New York")
    
    # Determine market activity level
    if "London" in sessions and "New York" in sessions:
        activity = "High Liquidity"
        detail = "London + New York overlap"
        bg_color = '#10b981'
    elif "London" in sessions or "New York" in sessions:
        activity = "Good Liquidity"
        detail = f"{sessions[0]} session active"
        bg_color = '#10b981'
    elif sessions:
        activity = "Moderate Liquidity"
        detail = f"{sessions[0]} session active"
        bg_color = '#f59e0b'
    else:
        activity = "Low Liquidity"
        detail = "Between major sessions"
        bg_color = '#f59e0b'
    
    return {
        'is_open': True,
        'status': 'OPEN',
        'message': 'Market Open',
        'detail': detail,
        'sessions': sessions,
        'activity': activity,
        'next_open': 'Market is open',
        'time_until_open': 'N/A',
        'color': 'white',
        'bg_color': bg_color
    }

def render_market_status():
    """Render market status banner."""
    market_status = get_market_status()
    
    # Check for pending trades
    pending_count = 0
    if 'pending_signals' in st.session_state:
        pending_count = len(st.session_state.pending_signals)
    
    # Create status banner using Streamlit components
    if market_status['is_open']:
        # Market is open
        status_text = f"🟢 {market_status['message']} - {market_status['activity']}"
        detail_text = f"{market_status['detail']} • Active Sessions: {', '.join(market_status.get('sessions', ['None']))}"
        
        if pending_count > 0:
            detail_text += f" • {pending_count} pending trade{'s' if pending_count != 1 else ''} will execute shortly!"
        
        st.success(f"""
        **{status_text}**
        
        {detail_text}
        """)
    else:
        # Market is closed
        status_text = f"🔴 {market_status['message']}"
        detail_text = f"{market_status['detail']} • Next Open: {market_status['next_open']} ({market_status['time_until_open']})"
        
        st.error(f"""
        **{status_text}**
        
        {detail_text}
        """)
        
        # Show pending trades notice if any
        if pending_count > 0:
            st.info(f"""
            📋 **{pending_count} trade{'s' if pending_count != 1 else ''} queued for execution when market opens**
            
            These trades will automatically execute when the forex market reopens on Sunday at 22:00 UTC.
            """)
    
    return market_status

def check_and_execute_pending_trades(market_status):
    """Check for pending trades and execute them when market opens."""
    if not market_status or not market_status.get('is_open', False):
        # Log pending trades when market is closed
        if 'pending_signals' in st.session_state and st.session_state.pending_signals:
            logger.info(f"""
📋 PENDING TRADES STATUS (Market Closed) 📋

Total pending trades: {len(st.session_state.pending_signals)}

Pending trades waiting for execution:""")
            for i, pending_trade in enumerate(st.session_state.pending_signals, 1):
                signal = pending_trade['signal']
                position_size = pending_trade['position_size']
                pnl_data = pending_trade['pnl_data']
                timestamp = pending_trade['timestamp']
                time_diff = datetime.now() - timestamp
                
                logger.info(f"""
{i}. {signal.signal_type} {signal.pair}
   Entry: {signal.entry_price:.5f}
   Target: {signal.target_price:.5f}
   Stop: {signal.stop_loss:.5f}
   Size: {position_size:,} units
   Confidence: {signal.confidence:.1%}
   Potential P&L: +£{pnl_data['potential_profit']:.2f} / -£{pnl_data['potential_loss']:.2f}
   Queued: {timestamp.strftime('%H:%M:%S')} ({time_diff.total_seconds()/60:.0f} min ago)
""")
            logger.info("⏳ Waiting for market to open (Sunday 22:00 UTC) to execute these trades...")
        return
    
    if 'pending_signals' not in st.session_state or not st.session_state.pending_signals:
        return
    
    pending_trades = st.session_state.pending_signals.copy()
    executed_count = 0
    
    logger.info(f"""
🚀 MARKET OPENED - EXECUTING PENDING TRADES 🚀

Found {len(pending_trades)} pending trades to execute...
""")
    
    st.markdown("### 🚀 Executing Pending Trades")
    
    for i, pending_trade in enumerate(pending_trades):
        signal = pending_trade['signal']
        position_size = pending_trade['position_size']
        pnl_data = pending_trade['pnl_data']
        timestamp = pending_trade['timestamp']
        
        # Check if trade is still valid (not too old)
        time_diff = datetime.now() - timestamp
        if time_diff.total_seconds() > 3600:  # 1 hour old
            logger.warning(f"⏰ Skipping old pending trade: {signal.signal_type} {signal.pair} (queued {time_diff.total_seconds()/60:.0f} minutes ago)")
            st.warning(f"⏰ Skipping old pending trade: {signal.signal_type} {signal.pair} (queued {time_diff.total_seconds()/60:.0f} minutes ago)")
            continue
        
        logger.info(f"🔄 Executing pending trade {i+1}/{len(pending_trades)}: {signal.signal_type} {signal.pair} at {signal.entry_price:.5f}")
        st.info(f"🔄 Executing pending trade: {signal.signal_type} {signal.pair} at {signal.entry_price:.5f}")
        
        try:
            # Execute the trade
            execute_trade_with_details(signal, position_size, pnl_data, auto=True)
            executed_count += 1
            logger.info(f"✅ Successfully executed pending trade: {signal.signal_type} {signal.pair}")
            
        except Exception as e:
            logger.error(f"❌ Failed to execute pending trade {signal.pair}: {e}")
            st.error(f"❌ Failed to execute pending trade {signal.pair}: {e}")
    
    # Clear executed trades from pending list
    if executed_count > 0:
        st.session_state.pending_signals = []
        st.success(f"✅ Successfully executed {executed_count} pending trades!")
    
    return executed_count

def show_pending_trades():
    """Display pending trades waiting for market to open."""
    if 'pending_signals' not in st.session_state or not st.session_state.pending_signals:
        return
    
    st.markdown("### ⏳ Pending Trades (Market Closed)")
    
    for i, pending_trade in enumerate(st.session_state.pending_signals):
        signal = pending_trade['signal']
        position_size = pending_trade['position_size']
        pnl_data = pending_trade['pnl_data']
        timestamp = pending_trade['timestamp']
        
        time_diff = datetime.now() - timestamp
        
        with st.expander(f"📋 {signal.signal_type} {signal.pair} - Queued {time_diff.total_seconds()/60:.0f} min ago"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Entry:** {signal.entry_price:.5f}")
                st.write(f"**Target:** {signal.target_price:.5f}")
                st.write(f"**Stop Loss:** {signal.stop_loss:.5f}")
            
            with col2:
                st.write(f"**Position Size:** {position_size:,} units")
                st.write(f"**Potential Profit:** £{pnl_data['potential_profit']:.2f}")
                st.write(f"**Potential Loss:** £{pnl_data['potential_loss']:.2f}")
            
            with col3:
                st.write(f"**Confidence:** {signal.confidence:.1%}")
                st.write(f"**Queued:** {timestamp.strftime('%H:%M:%S')}")
                
                if st.button(f"❌ Cancel", key=f"cancel_pending_{i}"):
                    st.session_state.pending_signals.pop(i)
                    st.rerun()

def main():
    """Main app function."""
    render_header()
    
    # Add market status banner
    market_status = render_market_status()
    
    # Check for pending trades when market opens
    if market_status and market_status.get('is_open', False):
        executed_count = check_and_execute_pending_trades(market_status)
        if executed_count and executed_count > 0:
            st.balloons()
    
    # Show pending trades if market is closed and there are pending trades
    if market_status and not market_status.get('is_open', False):
        show_pending_trades()
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Live Signals", 
        "📊 Open Trades",
        "💰 Account", 
        "📈 Backtest", 
        "📋 Trade Log"
    ])
    
    with tab1:
        # Pass market status to signals rendering
        render_live_signals(market_status)
    
    with tab2:
        render_open_trades()
    
    with tab3:
        render_account_status()
    
    with tab4:
        render_backtest_results()
    
    with tab5:
        render_trade_log()

if __name__ == "__main__":
    main() 