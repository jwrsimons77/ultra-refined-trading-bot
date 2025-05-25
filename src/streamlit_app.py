import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import io
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from sniper_bot import SniperBot
from data_generator import NewsDataGenerator

# Page configuration
st.set_page_config(
    page_title="Sniper Bot - AI Trading Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styles */
    .main-header {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .sub-header {
        text-align: center;
        font-size: 1.3rem;
        color: #64748b;
        margin-bottom: 3rem;
        font-weight: 400;
    }
    
    /* Card Styles */
    .metric-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
        margin-bottom: 1rem;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #64748b;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .success-metric .metric-value {
        color: #059669;
    }
    
    .warning-metric .metric-value {
        color: #d97706;
    }
    
    .danger-metric .metric-value {
        color: #dc2626;
    }
    
    .info-metric .metric-value {
        color: #2563eb;
    }
    
    /* Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    /* Sidebar Styles */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* Tab Styles */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Alert Styles */
    .alert-success {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border: 1px solid #34d399;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 1px solid #f59e0b;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .alert-info {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border: 1px solid #3b82f6;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Data Table Styles */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Progress Bar Styles */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Feature Card */
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #1e293b;
    }
    
    .feature-description {
        color: #64748b;
        font-size: 0.9rem;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header Section
    st.markdown('<h1 class="main-header">🎯 Sniper Bot</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Event-Driven Trading Platform with Advanced Sentiment Analysis</p>', unsafe_allow_html=True)
    
    # Quick Stats Bar
    if 'performance' in st.session_state and st.session_state.performance:
        display_quick_stats()
    
    # Sidebar configuration
    configure_sidebar()
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 Dashboard", 
        "📊 Data Setup", 
        "🚀 Backtest", 
        "📈 Results", 
        "📋 Trade Details"
    ])
    
    with tab1:
        display_dashboard()
    
    with tab2:
        display_data_setup()
    
    with tab3:
        display_backtest_tab()
    
    with tab4:
        display_results_tab()
    
    with tab5:
        display_trade_details_tab()

def configure_sidebar():
    """Configure the sidebar with bot parameters and settings."""
    st.sidebar.markdown("### ⚙️ Bot Configuration")
    
    # Bot parameters
    with st.sidebar.expander("🤖 Trading Parameters", expanded=True):
        initial_capital = st.number_input(
            "Initial Capital ($)", 
            min_value=100, 
            max_value=1000000, 
            value=10000, 
            step=1000,
            help="Starting capital for the trading bot"
        )
        
        max_daily_trades = st.number_input(
            "Max Daily Trades", 
            min_value=1, 
            max_value=20, 
            value=5,
            help="Maximum number of trades per day"
        )
        
        confidence_threshold = st.slider(
            "Confidence Threshold", 
            min_value=0.1, 
            max_value=1.0, 
            value=0.65, 
            step=0.05,
            help="Minimum confidence score for trade execution"
        )
        
        position_size = st.slider(
            "Position Size (%)", 
            min_value=1, 
            max_value=20, 
            value=5,
            help="Percentage of capital per trade"
        )
    
    # Risk Management
    with st.sidebar.expander("🛡️ Risk Management"):
        stop_loss = st.slider(
            "Stop Loss (%)", 
            min_value=1, 
            max_value=10, 
            value=3,
            help="Maximum loss per trade"
        )
        
        take_profit = st.slider(
            "Take Profit (%)", 
            min_value=1, 
            max_value=20, 
            value=6,
            help="Target profit per trade"
        )
        
        max_drawdown = st.slider(
            "Max Drawdown (%)", 
            min_value=5, 
            max_value=30, 
            value=15,
            help="Maximum portfolio drawdown"
        )
    
    # Store parameters in session state
    st.session_state.bot_params = {
        'initial_capital': initial_capital,
        'max_daily_trades': max_daily_trades,
        'confidence_threshold': confidence_threshold,
        'position_size': position_size,
        'stop_loss': stop_loss,
        'take_profit': take_profit,
        'max_drawdown': max_drawdown
    }
    
    # Initialize bot if not exists
    if 'bot' not in st.session_state:
        st.session_state.bot = SniperBot(
            initial_capital=initial_capital, 
            max_daily_trades=max_daily_trades
        )

def display_quick_stats():
    """Display quick performance stats at the top."""
    performance = st.session_state.performance
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_return = performance.get('total_return_pct', 0)
        color_class = "success-metric" if total_return >= 0 else "danger-metric"
        st.markdown(f"""
        <div class="metric-card {color_class}">
            <div class="metric-value">{total_return:.1f}%</div>
            <div class="metric-label">Total Return</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        win_rate = performance.get('win_rate', 0) * 100
        color_class = "success-metric" if win_rate >= 50 else "warning-metric"
        st.markdown(f"""
        <div class="metric-card {color_class}">
            <div class="metric-value">{win_rate:.1f}%</div>
            <div class="metric-label">Win Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        sharpe = performance.get('sharpe_ratio', 0)
        color_class = "success-metric" if sharpe >= 1 else "warning-metric"
        st.markdown(f"""
        <div class="metric-card {color_class}">
            <div class="metric-value">{sharpe:.2f}</div>
            <div class="metric-label">Sharpe Ratio</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_trades = performance.get('total_trades', 0)
        st.markdown(f"""
        <div class="metric-card info-metric">
            <div class="metric-value">{total_trades}</div>
            <div class="metric-label">Total Trades</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        final_capital = performance.get('final_capital', 0)
        st.markdown(f"""
        <div class="metric-card info-metric">
            <div class="metric-value">${final_capital:,.0f}</div>
            <div class="metric-label">Final Capital</div>
        </div>
        """, unsafe_allow_html=True)

def display_dashboard():
    """Display the main dashboard with overview and features."""
    st.markdown("## 🏠 Welcome to Sniper Bot")
    
    # Feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">AI-Powered Analysis</div>
            <div class="feature-description">
                Advanced sentiment analysis using transformer models to identify trading opportunities from news events.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Comprehensive Backtesting</div>
            <div class="feature-description">
                Robust backtesting engine with detailed performance metrics, risk analysis, and trade attribution.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Precision Trading</div>
            <div class="feature-description">
                Event-driven trading strategy that capitalizes on market inefficiencies following news releases.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Getting Started Guide
    st.markdown("## 🚀 Getting Started")
    
    with st.expander("📖 How to Use Sniper Bot", expanded=True):
        st.markdown("""
        ### Step-by-Step Guide:
        
        1. **📊 Data Setup**: Upload your news data or generate sample data for testing
        2. **⚙️ Configure Parameters**: Adjust trading parameters in the sidebar
        3. **🚀 Run Backtest**: Execute the backtesting engine with your data
        4. **📈 Analyze Results**: Review performance metrics and trade details
        5. **📋 Export Data**: Download detailed trade logs for further analysis
        
        ### Key Features:
        - **Real-time Sentiment Analysis**: Uses BERT-based models for news sentiment
        - **Risk Management**: Built-in stop-loss and position sizing controls
        - **Performance Analytics**: Comprehensive metrics including Sharpe ratio, drawdown analysis
        - **Interactive Visualizations**: Dynamic charts and graphs for data exploration
        """)
    
    # Recent Activity (if available)
    if 'results_df' in st.session_state and not st.session_state.results_df.empty:
        st.markdown("## 📈 Recent Performance")
        
        results_df = st.session_state.results_df
        
        # Quick performance chart
        fig = go.Figure()
        
        cumulative_returns = (1 + results_df['return_pct'] / 100).cumprod()
        fig.add_trace(go.Scatter(
            x=list(range(len(cumulative_returns))),
            y=cumulative_returns,
            mode='lines',
            name='Cumulative Returns',
            line=dict(color='#667eea', width=3)
        ))
        
        fig.update_layout(
            title="Portfolio Performance",
            xaxis_title="Trade Number",
            yaxis_title="Cumulative Return",
            height=400,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)

def display_data_setup():
    """Display the data setup tab with improved UI."""
    st.markdown("## 📊 Data Setup")
    st.markdown("Choose how you want to provide news data for backtesting:")
    
    # Data source selection
    data_source = st.radio(
        "Select Data Source:",
        ["📁 Upload CSV File", "🎲 Generate Sample Data"],
        horizontal=True
    )
    
    if data_source == "📁 Upload CSV File":
        st.markdown("### Upload Your News Data")
        
        with st.container():
            uploaded_file = st.file_uploader(
                "Choose a CSV file",
                type=['csv'],
                help="CSV should contain columns: headline, date, source (optional), ticker (optional)"
            )
            
            if uploaded_file is not None:
                try:
                    news_df = pd.read_csv(uploaded_file)
                    st.session_state.news_file_path = uploaded_file
                    
                    st.markdown('<div class="alert-success">✅ File uploaded successfully!</div>', unsafe_allow_html=True)
                    
                    # Data preview
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown("**Data Preview:**")
                        st.dataframe(news_df.head(10), use_container_width=True)
                    
                    with col2:
                        st.markdown("**Data Statistics:**")
                        display_data_stats(news_df)
                        
                except Exception as e:
                    st.markdown(f'<div class="alert-warning">❌ Error loading file: {e}</div>', unsafe_allow_html=True)
    
    else:  # Generate Sample Data
        st.markdown("### Generate Sample News Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            num_articles = st.number_input(
                "Number of Articles", 
                min_value=50, 
                max_value=5000, 
                value=1000,
                help="More articles = longer backtest time but more robust results"
            )
            
            start_date = st.date_input(
                "Start Date", 
                value=datetime(2023, 1, 1),
                max_value=datetime.now() - timedelta(days=30)
            )
        
        with col2:
            end_date = st.date_input(
                "End Date", 
                value=datetime(2023, 12, 31),
                max_value=datetime.now()
            )
            
            include_tickers = st.multiselect(
                "Focus on Specific Tickers (optional)",
                ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA", "NFLX"],
                help="Leave empty for random tickers"
            )
        
        if st.button("🎲 Generate Sample Data", type="primary", use_container_width=True):
            generate_sample_data(num_articles, start_date, end_date, include_tickers)

def generate_sample_data(num_articles, start_date, end_date, include_tickers):
    """Generate sample data with progress tracking."""
    progress_container = st.container()
    
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("🔄 Initializing data generator...")
            progress_bar.progress(10)
            
            generator = NewsDataGenerator()
            
            status_text.text("📰 Generating news articles...")
            progress_bar.progress(30)
            
            sample_df = generator.generate_sample_data(
                num_articles=num_articles,
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                focus_tickers=include_tickers if include_tickers else None
            )
            
            progress_bar.progress(70)
            status_text.text("💾 Saving data...")
            
            # Save to file
            sample_path = 'data/sample_news.csv'
            os.makedirs('data', exist_ok=True)
            sample_df.to_csv(sample_path, index=False)
            
            progress_bar.progress(100)
            status_text.text("✅ Sample data generated successfully!")
            
            st.session_state.news_file_path = sample_path
            
            # Display results
            st.markdown('<div class="alert-success">🎉 Sample data generated successfully!</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("**Generated Data Preview:**")
                st.dataframe(sample_df.head(10), use_container_width=True)
            
            with col2:
                st.markdown("**Data Statistics:**")
                display_data_stats(sample_df)
                
        except Exception as e:
            st.markdown(f'<div class="alert-warning">❌ Error generating data: {e}</div>', unsafe_allow_html=True)

def display_data_stats(df):
    """Display data statistics in a nice format."""
    stats_data = {
        "📊 Total Articles": len(df),
        "📅 Date Range": f"{len(df['date'].nunique())} days",
        "🏢 Sources": df['source'].nunique() if 'source' in df.columns else "N/A",
        "📈 Tickers": df['ticker'].nunique() if 'ticker' in df.columns else "Auto-detect"
    }
    
    for label, value in stats_data.items():
        st.metric(label, value)

def display_backtest_tab():
    """Display the backtesting tab with improved UI."""
    st.markdown("## 🚀 Run Backtest")
    
    if not hasattr(st.session_state, 'news_file_path'):
        st.markdown('<div class="alert-warning">⚠️ Please set up your data first in the Data Setup tab.</div>', unsafe_allow_html=True)
        return
    
    # Current configuration display
    if 'bot_params' in st.session_state:
        params = st.session_state.bot_params
        
        st.markdown("### 📋 Current Configuration")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            **💰 Capital & Position**
            - Initial Capital: ${params['initial_capital']:,}
            - Position Size: {params['position_size']}%
            - Max Daily Trades: {params['max_daily_trades']}
            """)
        
        with col2:
            st.markdown(f"""
            **🎯 Trading Parameters**
            - Confidence Threshold: {params['confidence_threshold']:.2f}
            - Stop Loss: {params['stop_loss']}%
            - Take Profit: {params['take_profit']}%
            """)
        
        with col3:
            st.markdown(f"""
            **🛡️ Risk Management**
            - Max Drawdown: {params['max_drawdown']}%
            """)
    
    st.markdown("---")
    
    # Backtest execution
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🎯 Execute Backtest")
        st.markdown("Ready to run the backtest with your current configuration.")
        
        if st.button("🚀 Start Backtest", type="primary", use_container_width=True):
            run_enhanced_backtest()
    
    with col2:
        st.markdown("### ⏱️ Estimated Time")
        
        if hasattr(st.session_state, 'news_file_path'):
            # Estimate based on data size
            if isinstance(st.session_state.news_file_path, str):
                try:
                    df = pd.read_csv(st.session_state.news_file_path)
                    estimated_time = max(1, len(df) // 100)  # Rough estimate
                    st.info(f"⏱️ Estimated time: ~{estimated_time} minutes")
                except:
                    st.info("⏱️ Estimated time: ~2-5 minutes")
            else:
                st.info("⏱️ Estimated time: ~2-5 minutes")

def run_enhanced_backtest():
    """Run backtest with enhanced progress tracking and error handling."""
    try:
        # Create containers for progress tracking
        progress_container = st.container()
        
        with progress_container:
            st.markdown("### 🔄 Backtest in Progress")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            time_text = st.empty()
            
            start_time = datetime.now()
            
            # Initialize bot with current parameters
            params = st.session_state.bot_params
            bot = SniperBot(
                initial_capital=params['initial_capital'],
                max_daily_trades=params['max_daily_trades']
            )
            
            # Load data
            status_text.text("📂 Loading news data...")
            progress_bar.progress(10)
            
            if isinstance(st.session_state.news_file_path, str):
                file_path = st.session_state.news_file_path
            else:
                # Handle uploaded file
                file_path = 'data/temp_upload.csv'
                os.makedirs('data', exist_ok=True)
                with open(file_path, 'wb') as f:
                    f.write(st.session_state.news_file_path.getvalue())
            
            # Run backtest
            status_text.text("🤖 Analyzing sentiment and generating signals...")
            progress_bar.progress(30)
            
            # Update progress periodically
            for i in range(30, 90, 10):
                progress_bar.progress(i)
                elapsed = datetime.now() - start_time
                time_text.text(f"⏱️ Elapsed time: {elapsed.seconds}s")
                
            results_df, performance = bot.run_full_backtest(
                file_path, 
                params['confidence_threshold']
            )
            
            progress_bar.progress(100)
            status_text.text("✅ Backtest completed successfully!")
            
            # Store results
            st.session_state.results_df = results_df
            st.session_state.performance = performance
            
            total_time = datetime.now() - start_time
            time_text.text(f"⏱️ Total time: {total_time.seconds}s")
            
            st.markdown('<div class="alert-success">🎉 Backtest completed! Check the Results tab for detailed analysis.</div>', unsafe_allow_html=True)
            
            # Auto-switch to results tab would be nice, but Streamlit doesn't support this directly
            st.balloons()
            
    except Exception as e:
        st.markdown(f'<div class="alert-warning">❌ Error running backtest: {str(e)}</div>', unsafe_allow_html=True)
        st.error("Please check your data format and try again.")

def display_results_tab():
    """Display enhanced results with better visualizations."""
    st.markdown("## 📈 Performance Results")
    
    if 'results_df' not in st.session_state or st.session_state.results_df.empty:
        st.markdown('<div class="alert-info">📊 Run a backtest to see detailed results here.</div>', unsafe_allow_html=True)
        return
    
    results_df = st.session_state.results_df
    performance = st.session_state.performance
    
    # Enhanced performance metrics
    display_enhanced_metrics(performance)
    
    st.markdown("---")
    
    # Interactive charts
    display_enhanced_charts(results_df, performance)
    
    st.markdown("---")
    
    # Analysis insights
    display_analysis_insights(results_df)

def display_enhanced_metrics(performance):
    """Display enhanced performance metrics."""
    st.markdown("### 🎯 Performance Overview")
    
    # Primary metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    metrics = [
        ("Total Return", f"{performance.get('total_return_pct', 0):.1f}%", "success" if performance.get('total_return_pct', 0) >= 0 else "danger"),
        ("Win Rate", f"{performance.get('win_rate', 0) * 100:.1f}%", "success" if performance.get('win_rate', 0) >= 0.5 else "warning"),
        ("Sharpe Ratio", f"{performance.get('sharpe_ratio', 0):.2f}", "success" if performance.get('sharpe_ratio', 0) >= 1 else "warning"),
        ("Max Drawdown", f"{performance.get('max_drawdown', 0):.1f}%", "warning" if performance.get('max_drawdown', 0) <= 10 else "danger"),
        ("Total Trades", f"{performance.get('total_trades', 0)}", "info")
    ]
    
    for i, (label, value, color) in enumerate(metrics):
        with [col1, col2, col3, col4, col5][i]:
            st.markdown(f"""
            <div class="metric-card {color}-metric">
                <div class="metric-value">{value}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Secondary metrics
    st.markdown("### 📊 Detailed Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**💰 Financial Metrics**")
        st.metric("Final Capital", f"${performance.get('final_capital', 0):,.0f}")
        st.metric("Total P&L", f"${performance.get('total_pnl', 0):,.0f}")
        st.metric("Average Trade", f"${performance.get('avg_trade_pnl', 0):.2f}")
    
    with col2:
        st.markdown("**📈 Performance Ratios**")
        st.metric("Profit Factor", f"{performance.get('profit_factor', 0):.2f}")
        st.metric("Calmar Ratio", f"{performance.get('calmar_ratio', 0):.2f}")
        st.metric("Sortino Ratio", f"{performance.get('sortino_ratio', 0):.2f}")
    
    with col3:
        st.markdown("**⏱️ Trade Statistics**")
        st.metric("Avg Days Held", f"{performance.get('avg_days_held', 0):.1f}")
        st.metric("Best Trade", f"{performance.get('best_trade', 0):.1f}%")
        st.metric("Worst Trade", f"{performance.get('worst_trade', 0):.1f}%")

def display_enhanced_charts(results_df, performance):
    """Display enhanced interactive charts."""
    st.markdown("### 📊 Interactive Charts")
    
    # Chart selection
    chart_type = st.selectbox(
        "Select Chart Type:",
        ["Portfolio Performance", "Return Distribution", "Trade Analysis", "Risk Metrics"]
    )
    
    if chart_type == "Portfolio Performance":
        display_portfolio_chart(results_df)
    elif chart_type == "Return Distribution":
        display_return_distribution(results_df)
    elif chart_type == "Trade Analysis":
        display_trade_analysis(results_df)
    else:
        display_risk_metrics(results_df)

def display_portfolio_chart(results_df):
    """Display portfolio performance chart."""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Cumulative Returns', 'Daily Returns'),
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3]
    )
    
    # Cumulative returns
    cumulative_returns = (1 + results_df['return_pct'] / 100).cumprod()
    fig.add_trace(
        go.Scatter(
            x=results_df['date'],
            y=cumulative_returns,
            mode='lines',
            name='Portfolio',
            line=dict(color='#667eea', width=2),
            fill='tonexty'
        ),
        row=1, col=1
    )
    
    # Daily returns
    colors = ['#2ca02c' if x >= 0 else '#d62728' for x in results_df['return_pct']]
    fig.add_trace(
        go.Bar(
            x=results_df['date'],
            y=results_df['return_pct'],
            name='Daily Returns',
            marker_color=colors,
            opacity=0.7
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=600,
        showlegend=False,
        title_text="Portfolio Performance Over Time"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_return_distribution(results_df):
    """Display return distribution analysis."""
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Return Histogram', 'Box Plot by Outcome')
    )
    
    # Histogram
    fig.add_trace(
        go.Histogram(
            x=results_df['return_pct'],
            nbinsx=30,
            name='Returns',
            marker_color='#667eea',
            opacity=0.7
        ),
        row=1, col=1
    )
    
    # Box plot by outcome
    for outcome in results_df['outcome'].unique():
        outcome_data = results_df[results_df['outcome'] == outcome]['return_pct']
        fig.add_trace(
            go.Box(
                y=outcome_data,
                name=outcome,
                boxpoints='outliers'
            ),
            row=1, col=2
        )
    
    fig.update_layout(height=400, title_text="Return Distribution Analysis")
    st.plotly_chart(fig, use_container_width=True)

def display_trade_analysis(results_df):
    """Display trade analysis charts."""
    col1, col2 = st.columns(2)
    
    with col1:
        # Performance by ticker
        ticker_perf = results_df.groupby('ticker')['return_pct'].agg(['count', 'mean', 'sum']).round(2)
        ticker_perf = ticker_perf.sort_values('sum', ascending=False).head(10)
        
        fig = px.bar(
            x=ticker_perf.index,
            y=ticker_perf['sum'],
            title="Top 10 Tickers by Total Return",
            labels={'x': 'Ticker', 'y': 'Total Return %'}
        )
        fig.update_traces(marker_color='#667eea')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Performance by confidence
        results_df['confidence_bucket'] = pd.cut(
            results_df['confidence_score'],
            bins=[0, 0.6, 0.8, 1.0],
            labels=['Low', 'Medium', 'High']
        )
        
        conf_perf = results_df.groupby('confidence_bucket')['return_pct'].mean()
        
        fig = px.bar(
            x=conf_perf.index,
            y=conf_perf.values,
            title="Performance by Confidence Level",
            labels={'x': 'Confidence Level', 'y': 'Average Return %'}
        )
        fig.update_traces(marker_color='#764ba2')
        st.plotly_chart(fig, use_container_width=True)

def display_risk_metrics(results_df):
    """Display risk analysis charts."""
    # Rolling metrics
    window = min(30, len(results_df) // 4)
    
    if window > 5:
        rolling_returns = results_df['return_pct'].rolling(window=window).mean()
        rolling_vol = results_df['return_pct'].rolling(window=window).std()
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Rolling Average Return', 'Rolling Volatility')
        )
        
        fig.add_trace(
            go.Scatter(
                x=list(range(len(rolling_returns))),
                y=rolling_returns,
                mode='lines',
                name='Rolling Return',
                line=dict(color='#667eea')
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=list(range(len(rolling_vol))),
                y=rolling_vol,
                mode='lines',
                name='Rolling Volatility',
                line=dict(color='#d62728')
            ),
            row=2, col=1
        )
        
        fig.update_layout(height=500, title_text="Risk Metrics Over Time")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data for rolling risk metrics analysis.")

def display_analysis_insights(results_df):
    """Display analytical insights."""
    st.markdown("### 🔍 Key Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🏆 Top Performing Strategies**")
        
        # Best performing tickers
        ticker_performance = results_df.groupby('ticker')['return_pct'].agg(['count', 'mean', 'sum']).round(2)
        ticker_performance.columns = ['Trades', 'Avg Return %', 'Total Return %']
        ticker_performance = ticker_performance.sort_values('Total Return %', ascending=False).head(5)
        
        st.dataframe(ticker_performance, use_container_width=True)
    
    with col2:
        st.markdown("**📊 Performance Distribution**")
        
        # Outcome distribution
        outcome_dist = results_df['outcome'].value_counts()
        
        fig = px.pie(
            values=outcome_dist.values,
            names=outcome_dist.index,
            title="Trade Outcomes"
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

def display_trade_details_tab():
    """Display enhanced trade details with filtering."""
    st.markdown("## 📋 Trade Details")
    
    if 'results_df' not in st.session_state or st.session_state.results_df.empty:
        st.markdown('<div class="alert-info">📋 Run a backtest to see detailed trade information here.</div>', unsafe_allow_html=True)
        return
    
    results_df = st.session_state.results_df
    
    # Enhanced filters
    st.markdown("### 🔍 Filter Trades")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        outcome_filter = st.selectbox("Outcome", ['All'] + list(results_df['outcome'].unique()))
    
    with col2:
        ticker_filter = st.selectbox("Ticker", ['All'] + sorted(results_df['ticker'].unique()))
    
    with col3:
        confidence_range = st.slider(
            "Confidence Range",
            min_value=float(results_df['confidence_score'].min()),
            max_value=float(results_df['confidence_score'].max()),
            value=(float(results_df['confidence_score'].min()), float(results_df['confidence_score'].max())),
            step=0.01
        )
    
    with col4:
        position_filter = st.selectbox("Position Type", ['All'] + list(results_df['position_type'].unique()))
    
    # Date range filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=pd.to_datetime(results_df['date'].min()))
    with col2:
        end_date = st.date_input("End Date", value=pd.to_datetime(results_df['date'].max()))
    
    # Apply filters
    filtered_df = apply_trade_filters(
        results_df, outcome_filter, ticker_filter, confidence_range, 
        position_filter, start_date, end_date
    )
    
    # Display results
    st.markdown(f"### 📊 Filtered Results ({len(filtered_df)} trades)")
    
    if not filtered_df.empty:
        # Summary stats for filtered data
        display_filtered_summary(filtered_df)
        
        # Trade table
        display_trade_table(filtered_df)
        
        # Export functionality
        provide_export_options(filtered_df)
    else:
        st.markdown('<div class="alert-warning">No trades match the current filters.</div>', unsafe_allow_html=True)

def apply_trade_filters(df, outcome, ticker, confidence_range, position, start_date, end_date):
    """Apply all trade filters."""
    filtered_df = df.copy()
    
    if outcome != 'All':
        filtered_df = filtered_df[filtered_df['outcome'] == outcome]
    
    if ticker != 'All':
        filtered_df = filtered_df[filtered_df['ticker'] == ticker]
    
    if position != 'All':
        filtered_df = filtered_df[filtered_df['position_type'] == position]
    
    # Confidence range
    filtered_df = filtered_df[
        (filtered_df['confidence_score'] >= confidence_range[0]) &
        (filtered_df['confidence_score'] <= confidence_range[1])
    ]
    
    # Date range
    filtered_df['date_parsed'] = pd.to_datetime(filtered_df['date'])
    filtered_df = filtered_df[
        (filtered_df['date_parsed'] >= pd.to_datetime(start_date)) &
        (filtered_df['date_parsed'] <= pd.to_datetime(end_date))
    ]
    
    return filtered_df.drop('date_parsed', axis=1)

def display_filtered_summary(filtered_df):
    """Display summary statistics for filtered trades."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_return = filtered_df['return_pct'].mean()
        color = "success" if avg_return >= 0 else "danger"
        st.markdown(f"""
        <div class="metric-card {color}-metric">
            <div class="metric-value">{avg_return:.2f}%</div>
            <div class="metric-label">Avg Return</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        win_rate = (filtered_df['outcome'] == 'win').mean() * 100
        color = "success" if win_rate >= 50 else "warning"
        st.markdown(f"""
        <div class="metric-card {color}-metric">
            <div class="metric-value">{win_rate:.1f}%</div>
            <div class="metric-label">Win Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_return = filtered_df['return_pct'].sum()
        color = "success" if total_return >= 0 else "danger"
        st.markdown(f"""
        <div class="metric-card {color}-metric">
            <div class="metric-value">{total_return:.1f}%</div>
            <div class="metric-label">Total Return</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_confidence = filtered_df['confidence_score'].mean()
        st.markdown(f"""
        <div class="metric-card info-metric">
            <div class="metric-value">{avg_confidence:.3f}</div>
            <div class="metric-label">Avg Confidence</div>
        </div>
        """, unsafe_allow_html=True)

def display_trade_table(filtered_df):
    """Display the trade table with proper formatting."""
    # Format the dataframe for display
    display_df = filtered_df.copy()
    display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m-%d')
    display_df['return_pct'] = display_df['return_pct'].round(2)
    display_df['confidence_score'] = display_df['confidence_score'].round(3)
    display_df['buy_price'] = display_df['buy_price'].round(2)
    display_df['exit_price'] = display_df['exit_price'].round(2)
    
    # Select and reorder columns
    columns_to_show = [
        'date', 'ticker', 'outcome', 'return_pct', 'confidence_score',
        'position_type', 'buy_price', 'exit_price', 'days_held'
    ]
    
    # Add source if available
    if 'source' in display_df.columns:
        columns_to_show.append('source')
    
    st.dataframe(
        display_df[columns_to_show],
        use_container_width=True,
        hide_index=True,
        column_config={
            "return_pct": st.column_config.NumberColumn(
                "Return %",
                format="%.2f%%"
            ),
            "confidence_score": st.column_config.NumberColumn(
                "Confidence",
                format="%.3f"
            ),
            "buy_price": st.column_config.NumberColumn(
                "Buy Price",
                format="$%.2f"
            ),
            "exit_price": st.column_config.NumberColumn(
                "Exit Price", 
                format="$%.2f"
            )
        }
    )

def provide_export_options(filtered_df):
    """Provide export options for the filtered data."""
    st.markdown("### 📥 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # CSV export
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📄 Download as CSV",
            data=csv,
            file_name=f"sniper_bot_trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # JSON export
        json_data = filtered_df.to_json(orient='records', date_format='iso')
        st.download_button(
            label="📋 Download as JSON",
            data=json_data,
            file_name=f"sniper_bot_trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col3:
        # Summary report
        if st.button("📊 Generate Report", use_container_width=True):
            generate_summary_report(filtered_df)

def generate_summary_report(filtered_df):
    """Generate a summary report of the filtered trades."""
    report = f"""
# Sniper Bot Trading Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary Statistics
- Total Trades: {len(filtered_df)}
- Win Rate: {(filtered_df['outcome'] == 'win').mean() * 100:.1f}%
- Average Return: {filtered_df['return_pct'].mean():.2f}%
- Total Return: {filtered_df['return_pct'].sum():.2f}%
- Best Trade: {filtered_df['return_pct'].max():.2f}%
- Worst Trade: {filtered_df['return_pct'].min():.2f}%

## Performance by Ticker
{filtered_df.groupby('ticker')['return_pct'].agg(['count', 'mean', 'sum']).round(2).to_string()}

## Performance by Outcome
{filtered_df.groupby('outcome')['return_pct'].agg(['count', 'mean']).round(2).to_string()}
"""
    
    st.download_button(
        label="📄 Download Report",
        data=report,
        file_name=f"sniper_bot_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )

# Initialize session state
if 'results_df' not in st.session_state:
    st.session_state.results_df = pd.DataFrame()

if 'performance' not in st.session_state:
    st.session_state.performance = {}

if __name__ == "__main__":
    main() 