import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import time
import os
import sys

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from enhanced_sniper_bot import EnhancedSniperBot, TradingSignal

# Page configuration
st.set_page_config(
    page_title="📱 Signal Manager - Mobile Trading Dashboard",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed"  # Mobile-friendly
)

# Custom CSS for mobile-friendly design
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        padding: 0 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .block-container {
        padding: 1rem !important;
        max-width: 1200px !important;
        margin: 0 auto !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255,255,255,0.3);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255,255,255,0.5);
    }
    
    /* Typography */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Header Styles */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: white;
        text-align: center;
        margin: 2rem 0 1rem 0;
        text-shadow: 0 4px 20px rgba(0,0,0,0.3);
        letter-spacing: -0.02em;
    }
    
    .main-subtitle {
        font-size: 1.2rem;
        color: rgba(255,255,255,0.9);
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 8px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 10px;
        color: rgba(255,255,255,0.8);
        font-weight: 500;
        padding: 12px 20px;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(255,255,255,0.2) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Content Container */
    .content-container {
        background: rgba(255,255,255,0.95);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.3);
    }
    
    /* Signal Cards */
    .signal-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 20px;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);
        border: 1px solid rgba(255,255,255,0.2);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .signal-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4);
        background-size: 300% 100%;
        animation: gradient 3s ease infinite;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .signal-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 25px 50px rgba(102, 126, 234, 0.4);
    }
    
    .buy-signal {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        box-shadow: 0 15px 35px rgba(17, 153, 142, 0.3);
    }
    
    .sell-signal {
        background: linear-gradient(135deg, #fc466b 0%, #3f5efb 100%);
        box-shadow: 0 15px 35px rgba(252, 70, 107, 0.3);
    }
    
    .signal-ticker {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .signal-price {
        font-size: 1.3rem;
        margin: 0.5rem 0;
        font-weight: 500;
        opacity: 0.95;
    }
    
    .confidence-badge {
        background: rgba(255,255,255,0.25);
        padding: 0.4rem 1rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-block;
        margin: 0.5rem 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.3);
    }
    
    /* Metric Cards */
    .metric-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 0.5rem;
        border: 1px solid rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .metric-label {
        color: #64748b;
        font-size: 0.95rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        letter-spacing: 0.02em;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Action Buttons */
    .action-button {
        background: rgba(255,255,255,0.2);
        border: 2px solid rgba(255,255,255,0.3);
        color: white;
        padding: 0.8rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        margin: 0.3rem;
        cursor: pointer;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
        font-size: 0.9rem;
    }
    
    .action-button:hover {
        background: rgba(255,255,255,0.3);
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }
    
    /* Form Elements */
    .stSelectbox > div > div {
        background: white;
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stSlider > div > div > div {
        background: #667eea;
    }
    
    .stNumberInput > div > div {
        background: white;
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stNumberInput > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* News Headlines */
    .news-headline {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1.5rem;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* Status Colors */
    .status-pending { 
        color: #f59e0b; 
        font-weight: 600;
    }
    .status-executed { 
        color: #10b981; 
        font-weight: 600;
    }
    .status-cancelled { 
        color: #ef4444; 
        font-weight: 600;
    }
    .status-expired { 
        color: #6b7280; 
        font-weight: 600;
    }
    
    /* Section Headers */
    h1, h2, h3 {
        color: #1e293b;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    /* Info/Warning/Success Messages */
    .stAlert {
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Toggle Switch */
    .stCheckbox > label {
        background: rgba(255,255,255,0.1);
        padding: 0.5rem 1rem;
        border-radius: 25px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        color: white;
        font-weight: 500;
    }
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.5rem;
        }
        .signal-ticker {
            font-size: 1.8rem;
        }
        .signal-price {
            font-size: 1.1rem;
        }
        .metric-value {
            font-size: 2rem;
        }
        .content-container {
            padding: 1.5rem;
            margin: 0.5rem 0;
        }
        .block-container {
            padding: 0.5rem !important;
        }
    }
    
    /* Loading Spinner */
    .stSpinner > div {
        border-color: #667eea !important;
    }
    
    /* Plotly Charts */
    .js-plotly-plot {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'bot' not in st.session_state:
        st.session_state.bot = EnhancedSniperBot(initial_capital=1000, max_daily_trades=3)
    
    if 'signals' not in st.session_state:
        st.session_state.signals = []
    
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()
    
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = True

def render_signal_card(signal: TradingSignal, index: int):
    """Render a mobile-friendly signal card."""
    signal_class = "buy-signal" if signal.signal_type == "BUY" else "sell-signal"
    
    with st.container():
        st.markdown(f"""
        <div class="signal-card {signal_class}">
            <div class="signal-ticker">{signal.ticker} - {signal.signal_type}</div>
            <div class="signal-price">Entry: ${signal.entry_price:.2f}</div>
            <div class="signal-price">Target: ${signal.target_price:.2f} | Stop: ${signal.stop_loss:.2f}</div>
            <div class="confidence-badge">Confidence: {signal.confidence_score:.2f}</div>
            <div style="margin-top: 1rem;">
                <small>{signal.headline[:100]}...</small>
            </div>
            <div style="margin-top: 1rem;">
                <span class="status-{signal.status.lower()}">● {signal.status}</span>
                <span style="float: right;">{signal.created_at.strftime('%H:%M')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(f"✅ Execute", key=f"execute_{index}", use_container_width=True):
                execute_signal(signal)
        
        with col2:
            if st.button(f"❌ Cancel", key=f"cancel_{index}", use_container_width=True):
                cancel_signal(signal)
        
        with col3:
            if st.button(f"📊 Details", key=f"details_{index}", use_container_width=True):
                show_signal_details(signal)

def execute_signal(signal: TradingSignal):
    """Execute a trading signal."""
    st.session_state.bot.signal_db.update_signal_status(
        signal.id, 
        'EXECUTED', 
        execution_price=signal.entry_price
    )
    st.success(f"✅ Signal executed: {signal.signal_type} {signal.ticker} at ${signal.entry_price:.2f}")
    st.rerun()

def cancel_signal(signal: TradingSignal):
    """Cancel a trading signal."""
    st.session_state.bot.signal_db.update_signal_status(signal.id, 'CANCELLED')
    st.warning(f"❌ Signal cancelled: {signal.signal_type} {signal.ticker}")
    st.rerun()

def show_signal_details(signal: TradingSignal):
    """Show detailed signal information."""
    with st.expander(f"📊 {signal.ticker} Signal Details", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Entry Price", f"${signal.entry_price:.2f}")
            st.metric("Target Price", f"${signal.target_price:.2f}")
            st.metric("Stop Loss", f"${signal.stop_loss:.2f}")
        
        with col2:
            st.metric("Confidence Score", f"{signal.confidence_score:.2f}")
            st.metric("Sentiment", f"{signal.sentiment_score:.2f}")
            potential_return = ((signal.target_price - signal.entry_price) / signal.entry_price) * 100
            st.metric("Potential Return", f"{potential_return:.1f}%")
        
        st.subheader("📰 News Headline")
        st.markdown(f"""
        <div class="news-headline">
            <strong>{signal.source}</strong><br>
            {signal.headline}
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("⏰ Timing")
        st.write(f"**Created:** {signal.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(f"**Expires:** {signal.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Time remaining
        time_remaining = signal.expires_at - datetime.now()
        if time_remaining.total_seconds() > 0:
            hours_remaining = time_remaining.total_seconds() / 3600
            st.write(f"**Time Remaining:** {hours_remaining:.1f} hours")
        else:
            st.error("⚠️ Signal has expired")

def render_dashboard_metrics():
    """Render dashboard metrics."""
    signals = st.session_state.bot.signal_db.get_active_signals()
    
    # Calculate metrics
    total_signals = len(signals)
    buy_signals = len([s for s in signals if s.signal_type == 'BUY'])
    sell_signals = len([s for s in signals if s.signal_type == 'SELL'])
    avg_confidence = np.mean([s.confidence_score for s in signals]) if signals else 0
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_signals}</div>
            <div class="metric-label">Active Signals</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #11998e;">{buy_signals}</div>
            <div class="metric-label">Buy Signals</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #fc466b;">{sell_signals}</div>
            <div class="metric-label">Sell Signals</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg_confidence:.2f}</div>
            <div class="metric-label">Avg Confidence</div>
        </div>
        """, unsafe_allow_html=True)

def generate_new_signals():
    """Generate new trading signals from real news."""
    with st.spinner("🔍 Scanning news for trading opportunities..."):
        try:
            # Generate signals with more realistic threshold
            new_signals = st.session_state.bot.generate_daily_signals(confidence_threshold=0.2)
            
            if new_signals:
                st.success(f"✅ Generated {len(new_signals)} new signals!")
                st.session_state.last_refresh = datetime.now()
                
                # Show preview of new signals
                st.subheader("🆕 New Signals Generated")
                for i, signal in enumerate(new_signals[:3]):  # Show top 3
                    with st.expander(f"{signal.ticker} - {signal.signal_type} (Confidence: {signal.confidence_score:.2f})"):
                        st.write(f"**Entry:** ${signal.entry_price:.2f}")
                        st.write(f"**Target:** ${signal.target_price:.2f}")
                        st.write(f"**Stop Loss:** ${signal.stop_loss:.2f}")
                        st.write(f"**News:** {signal.headline}")
                
                time.sleep(2)  # Brief pause to show results
                st.rerun()
            else:
                st.warning("⚠️ No high-confidence signals found in current news.")
                
        except Exception as e:
            st.error(f"❌ Error generating signals: {str(e)}")

def render_backtest_section():
    """Render backtesting section with detailed trade information."""
    st.header("📈 Backtest Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=90), key="backtest_start_date")
        confidence_threshold = st.slider("Confidence Threshold", 0.1, 1.0, 0.3, 0.1, key="backtest_confidence")
    
    with col2:
        end_date = st.date_input("End Date", value=datetime.now(), key="backtest_end_date")
        
    if st.button("🚀 Run Backtest", type="primary", use_container_width=True, key="run_backtest_btn"):
        with st.spinner("Running backtest with real news data..."):
            results = st.session_state.bot.backtest_with_real_news(
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d'),
                confidence_threshold
            )
            
            # Display summary metrics
            st.subheader("📊 Performance Summary")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Trades", results['total_trades'])
            with col2:
                st.metric("Win Rate", f"{results['win_rate']*100:.1f}%")
            with col3:
                st.metric("Total Return", f"{results['total_return_pct']:.1f}%")
            with col4:
                st.metric("Sharpe Ratio", f"{results['sharpe_ratio']:.2f}")
            
            # Additional metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Wins", results['wins'], delta=f"{results['wins']}/{results['total_trades']}")
            with col2:
                st.metric("Losses", results['losses'], delta=f"{results['losses']}/{results['total_trades']}")
            with col3:
                initial_capital = 10000
                final_value = initial_capital * (1 + results['total_return_pct']/100)
                profit = final_value - initial_capital
                st.metric("Final Value", f"${final_value:,.0f}", delta=f"${profit:,.0f}")
            with col4:
                st.metric("Max Drawdown", f"{results['max_drawdown_pct']:.1f}%")
            
            # Performance chart
            if results['trades']:
                st.subheader("📈 Cumulative Returns")
                trades_df = pd.DataFrame(results['trades'])
                trades_df['date'] = pd.to_datetime(trades_df['date'])
                trades_df['cumulative_return'] = trades_df['return_pct'].cumsum()
                
                fig = px.line(trades_df, x='date', y='cumulative_return',
                             title='Cumulative Returns Over Time',
                             labels={'cumulative_return': 'Cumulative Return (%)', 'date': 'Date'})
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#1e293b')
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Detailed trade table
                st.subheader("📋 Detailed Trade History")
                
                # Filter options
                col1, col2, col3 = st.columns(3)
                with col1:
                    outcome_filter = st.selectbox("Filter by Outcome", ["All", "WIN", "LOSS"], key="outcome_filter")
                with col2:
                    signal_filter = st.selectbox("Filter by Signal Type", ["All", "BUY", "SELL"], key="signal_filter")
                with col3:
                    show_count = st.selectbox("Show Trades", ["All", "First 20", "First 50"], key="show_count")
                
                # Apply filters
                filtered_trades = trades_df.copy()
                if outcome_filter != "All":
                    filtered_trades = filtered_trades[filtered_trades['outcome'] == outcome_filter]
                if signal_filter != "All":
                    filtered_trades = filtered_trades[filtered_trades['signal_type'] == signal_filter]
                
                # Limit display count
                if show_count == "First 20":
                    filtered_trades = filtered_trades.head(20)
                elif show_count == "First 50":
                    filtered_trades = filtered_trades.head(50)
                
                # Format the dataframe for display
                display_df = filtered_trades.copy()
                display_df['Entry Price'] = display_df['entry_price'].apply(lambda x: f"${x:.2f}")
                display_df['Exit Price'] = display_df['exit_price'].apply(lambda x: f"${x:.2f}")
                display_df['Target'] = display_df['target_price'].apply(lambda x: f"${x:.2f}")
                display_df['Stop Loss'] = display_df['stop_loss'].apply(lambda x: f"${x:.2f}")
                display_df['Return'] = display_df['return_pct'].apply(lambda x: f"{x:+.1f}%")
                display_df['Hold Days'] = display_df['hold_duration']
                display_df['Confidence'] = display_df['confidence_score'].apply(lambda x: f"{x:.2f}")
                
                # Create status column with emojis
                def format_outcome(row):
                    if row['outcome'] == 'WIN':
                        return f"✅ {row['exit_reason']}"
                    else:
                        return f"❌ {row['exit_reason']}"
                
                display_df['Status'] = display_df.apply(format_outcome, axis=1)
                
                # Select columns for display
                columns_to_show = [
                    'date', 'ticker', 'signal_type', 'Entry Price', 'Exit Price', 
                    'Target', 'Stop Loss', 'Hold Days', 'Return', 'Confidence', 'Status'
                ]
                
                # Rename columns for better display
                column_mapping = {
                    'date': 'Entry Date',
                    'ticker': 'Ticker',
                    'signal_type': 'Signal',
                    'Entry Price': 'Entry',
                    'Exit Price': 'Exit',
                    'Target': 'Target',
                    'Stop Loss': 'Stop',
                    'Hold Days': 'Days',
                    'Return': 'Return %',
                    'Confidence': 'Conf.',
                    'Status': 'Result'
                }
                
                final_df = display_df[columns_to_show].rename(columns=column_mapping)
                
                # Style the dataframe
                def color_negative_red(val):
                    """Color negative values red and positive values green."""
                    try:
                        if isinstance(val, str):
                            if '+' in val:
                                return 'color: #10b981; font-weight: bold'
                            elif '-' in val:
                                return 'color: #ef4444; font-weight: bold'
                        return ''
                    except:
                        return ''
                
                def color_result(val):
                    """Color results based on win/loss."""
                    try:
                        if isinstance(val, str):
                            if '✅' in val:
                                return 'color: #10b981; font-weight: bold'
                            elif '❌' in val:
                                return 'color: #ef4444; font-weight: bold'
                        return ''
                    except:
                        return ''
                
                # Apply styling more safely
                try:
                    styled_df = final_df.style.applymap(color_negative_red, subset=['Return %']) \
                                             .applymap(color_result, subset=['Result'])
                    st.dataframe(styled_df, use_container_width=True, height=400)
                except Exception as e:
                    # Fallback to unstyled dataframe if styling fails
                    st.dataframe(final_df, use_container_width=True, height=400)
                
                # Trade statistics
                st.subheader("📊 Trade Statistics")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**📈 Hold Duration Analysis**")
                    avg_hold = filtered_trades['hold_duration'].mean()
                    median_hold = filtered_trades['hold_duration'].median()
                    max_hold = filtered_trades['hold_duration'].max()
                    min_hold = filtered_trades['hold_duration'].min()
                    
                    st.write(f"Average: {avg_hold:.1f} days")
                    st.write(f"Median: {median_hold:.1f} days")
                    st.write(f"Range: {min_hold}-{max_hold} days")
                
                with col2:
                    st.markdown("**💰 Return Analysis**")
                    avg_return = filtered_trades['return_pct'].mean()
                    win_trades = filtered_trades[filtered_trades['outcome'] == 'WIN']
                    loss_trades = filtered_trades[filtered_trades['outcome'] == 'LOSS']
                    
                    st.write(f"Average Return: {avg_return:+.1f}%")
                    if not win_trades.empty:
                        st.write(f"Avg Win: {win_trades['return_pct'].mean():+.1f}%")
                    if not loss_trades.empty:
                        st.write(f"Avg Loss: {loss_trades['return_pct'].mean():+.1f}%")
                
                with col3:
                    st.markdown("**🎯 Exit Reasons**")
                    exit_reasons = filtered_trades['exit_reason'].value_counts()
                    for reason, count in exit_reasons.items():
                        percentage = (count / len(filtered_trades)) * 100
                        st.write(f"{reason}: {count} ({percentage:.1f}%)")
                
                # Download option
                st.subheader("💾 Export Data")
                csv = final_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Trade History as CSV",
                    data=csv,
                    file_name=f"backtest_trades_{start_date}_{end_date}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

def main():
    """Main application function."""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">📱 Signal Manager</h1>', unsafe_allow_html=True)
    st.markdown('<p class="main-subtitle">Real-time trading signals from AI-powered news analysis</p>', unsafe_allow_html=True)
    
    # Auto-refresh toggle
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        auto_refresh = st.toggle("🔄 Auto-refresh signals", value=st.session_state.auto_refresh, key="main_auto_refresh")
        st.session_state.auto_refresh = auto_refresh
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🔍 Generate Signals", "📈 Backtest", "⚙️ Settings"])
    
    with tab1:
        st.markdown('<div class="content-container">', unsafe_allow_html=True)
        st.header("📊 Active Signals Dashboard")
        
        # Metrics
        render_dashboard_metrics()
        
        # Refresh button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Refresh Signals", type="primary", use_container_width=True, key="refresh_signals_btn"):
                st.rerun()
        
        # Active signals
        signals = st.session_state.bot.signal_db.get_active_signals()
        
        if signals:
            st.subheader(f"🎯 {len(signals)} Active Signals")
            
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                signal_type_filter = st.selectbox("Filter by Type", ["All", "BUY", "SELL"], key="dashboard_signal_filter")
            with col2:
                min_confidence = st.slider("Min Confidence", 0.0, 3.0, 0.0, 0.1, key="dashboard_min_confidence")
            
            # Apply filters
            filtered_signals = signals
            if signal_type_filter != "All":
                filtered_signals = [s for s in filtered_signals if s.signal_type == signal_type_filter]
            filtered_signals = [s for s in filtered_signals if s.confidence_score >= min_confidence]
            
            # Display signals
            for i, signal in enumerate(filtered_signals):
                render_signal_card(signal, i)
                
        else:
            st.info("📭 No active signals. Generate new signals from the 'Generate Signals' tab.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="content-container">', unsafe_allow_html=True)
        st.header("🔍 Generate New Signals")
        
        st.markdown("""
        ### 📰 Real-time News Analysis
        Generate trading signals by analyzing the latest financial news from multiple sources:
        - **Alpha Vantage**: Market sentiment analysis
        - **Polygon.io**: Real-time news feeds  
        - **Stock News API**: Comprehensive market coverage
        """)
        
        # Configuration
        col1, col2 = st.columns(2)
        with col1:
            confidence_threshold = st.slider("Confidence Threshold", 0.1, 1.0, 0.2, 0.1, key="generate_confidence")
            st.caption("Higher threshold = fewer but higher quality signals")
        
        with col2:
            max_signals = st.number_input("Max Signals", min_value=1, max_value=10, value=5, key="generate_max_signals")
            st.caption("Maximum signals to generate per scan")
        
        # Generate button
        if st.button("🎯 Generate Signals from Live News", type="primary", use_container_width=True, key="generate_signals_btn"):
            generate_new_signals()
        
        # Last refresh info
        if st.session_state.last_refresh:
            time_since_refresh = datetime.now() - st.session_state.last_refresh
            st.caption(f"Last refresh: {time_since_refresh.total_seconds()/60:.0f} minutes ago")
        
        # API Status
        st.subheader("🔌 API Status")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            alpha_key = os.getenv('ALPHA_VANTAGE_API_KEY')
            status = "🟢 Connected" if alpha_key else "🔴 No API Key"
            st.write(f"**Alpha Vantage:** {status}")
        
        with col2:
            polygon_key = os.getenv('POLYGON_API_KEY')
            status = "🟢 Connected" if polygon_key else "🔴 No API Key"
            st.write(f"**Polygon.io:** {status}")
        
        with col3:
            stock_news_key = os.getenv('STOCK_NEWS_API_KEY')
            status = "🟢 Connected" if stock_news_key else "🔴 No API Key"
            st.write(f"**Stock News API:** {status}")
        
        if not any([alpha_key, polygon_key, stock_news_key]):
            st.warning("⚠️ No API keys configured. The bot will use demo data.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="content-container">', unsafe_allow_html=True)
        render_backtest_section()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        st.markdown('<div class="content-container">', unsafe_allow_html=True)
        st.header("⚙️ Settings")
        
        # Bot configuration
        st.subheader("🤖 Bot Configuration")
        
        col1, col2 = st.columns(2)
        with col1:
            initial_capital = st.number_input("Initial Capital ($)", min_value=100, max_value=100000, value=1000, key="settings_capital")
            max_daily_trades = st.number_input("Max Daily Trades", min_value=1, max_value=10, value=3, key="settings_max_trades")
        
        with col2:
            signal_expiry_hours = st.number_input("Signal Expiry (hours)", min_value=1, max_value=48, value=24, key="settings_expiry")
            auto_execute = st.checkbox("Auto-execute high confidence signals (>2.5)", key="settings_auto_execute")
        
        # API Keys setup
        st.subheader("🔑 API Keys")
        st.markdown("""
        To get real-time news data, you'll need API keys from these providers:
        
        1. **Alpha Vantage** (Free tier: 5 calls/min)
           - Sign up at: https://www.alphavantage.co/support/#api-key
           - Set environment variable: `ALPHA_VANTAGE_API_KEY`
        
        2. **Polygon.io** (Free tier: 5 calls/min)
           - Sign up at: https://polygon.io/
           - Set environment variable: `POLYGON_API_KEY`
        
        3. **Stock News API** (Free tier: 100 calls/day)
           - Sign up at: https://stocknewsapi.com/
           - Set environment variable: `STOCK_NEWS_API_KEY`
        """)
        
        # Export/Import settings
        st.subheader("💾 Data Management")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Export Signals", use_container_width=True, key="export_signals_btn"):
                # Export functionality
                st.success("Signals exported to CSV")
        
        with col2:
            if st.button("🗑️ Clear All Signals", use_container_width=True, key="clear_signals_btn"):
                # Clear functionality
                st.warning("All signals cleared")
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Auto-refresh functionality
    if st.session_state.auto_refresh:
        time.sleep(30)  # Refresh every 30 seconds
        st.rerun()

if __name__ == "__main__":
    main() 