import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import io
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from sniper_bot import SniperBot
from data_generator import NewsDataGenerator

# Page configuration
st.set_page_config(
    page_title="Sniper Bot - Event-Driven Trading",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-metric {
        border-left-color: #28a745;
    }
    .warning-metric {
        border-left-color: #ffc107;
    }
    .danger-metric {
        border-left-color: #dc3545;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">🎯 Sniper Bot</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Event-Driven Trading Bot with Sentiment Analysis & Backtesting</p>', unsafe_allow_html=True)
    
    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")
    
    # Bot parameters
    st.sidebar.subheader("Bot Parameters")
    initial_capital = st.sidebar.number_input("Initial Capital ($)", min_value=100, max_value=100000, value=1000, step=100)
    max_daily_trades = st.sidebar.number_input("Max Daily Trades", min_value=1, max_value=10, value=3)
    confidence_threshold = st.sidebar.slider("Confidence Threshold", min_value=0.1, max_value=1.0, value=0.6, step=0.05)
    
    # Initialize session state
    if 'bot' not in st.session_state:
        st.session_state.bot = SniperBot(initial_capital=initial_capital, max_daily_trades=max_daily_trades)
    
    if 'results_df' not in st.session_state:
        st.session_state.results_df = pd.DataFrame()
    
    if 'performance' not in st.session_state:
        st.session_state.performance = {}
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Data & Setup", "🚀 Run Backtest", "📈 Results", "📋 Trade Details"])
    
    with tab1:
        st.header("📊 Data Setup")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Option 1: Upload Your Data")
            uploaded_file = st.file_uploader(
                "Upload CSV file with news data",
                type=['csv'],
                help="CSV should contain columns: headline, date, source (optional)"
            )
            
            if uploaded_file is not None:
                try:
                    news_df = pd.read_csv(uploaded_file)
                    st.success(f"✅ Loaded {len(news_df)} news articles")
                    st.dataframe(news_df.head())
                    st.session_state.news_file_path = uploaded_file
                except Exception as e:
                    st.error(f"Error loading file: {e}")
        
        with col2:
            st.subheader("Option 2: Generate Sample Data")
            
            num_articles = st.number_input("Number of Articles", min_value=50, max_value=2000, value=500)
            start_date = st.date_input("Start Date", value=datetime(2023, 1, 1))
            end_date = st.date_input("End Date", value=datetime(2023, 12, 31))
            
            if st.button("🎲 Generate Sample Data", type="primary"):
                with st.spinner("Generating sample news data..."):
                    generator = NewsDataGenerator()
                    sample_df = generator.generate_sample_data(
                        num_articles=num_articles,
                        start_date=start_date.strftime('%Y-%m-%d'),
                        end_date=end_date.strftime('%Y-%m-%d')
                    )
                    
                    # Save to temporary file
                    sample_path = 'data/sample_news.csv'
                    os.makedirs('data', exist_ok=True)
                    sample_df.to_csv(sample_path, index=False)
                    
                    st.session_state.news_file_path = sample_path
                    st.success(f"✅ Generated {len(sample_df)} sample articles")
                    st.dataframe(sample_df.head())
        
        # Data preview and statistics
        if hasattr(st.session_state, 'news_file_path'):
            st.subheader("📋 Data Preview")
            
            if isinstance(st.session_state.news_file_path, str):
                preview_df = pd.read_csv(st.session_state.news_file_path)
            else:
                preview_df = pd.read_csv(st.session_state.news_file_path)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Articles", len(preview_df))
            with col2:
                st.metric("Date Range", f"{len(preview_df['date'].nunique())} days")
            with col3:
                if 'source' in preview_df.columns:
                    st.metric("Sources", preview_df['source'].nunique())
                else:
                    st.metric("Sources", "N/A")
            with col4:
                if 'ticker' in preview_df.columns:
                    st.metric("Tickers", preview_df['ticker'].nunique())
                else:
                    st.metric("Tickers", "Auto-detect")
    
    with tab2:
        st.header("🚀 Run Backtest")
        
        if not hasattr(st.session_state, 'news_file_path'):
            st.warning("⚠️ Please upload or generate news data first in the Data & Setup tab.")
            return
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Backtest Configuration")
            
            # Display current settings
            st.info(f"""
            **Current Settings:**
            - Initial Capital: ${initial_capital:,}
            - Max Daily Trades: {max_daily_trades}
            - Confidence Threshold: {confidence_threshold}
            """)
        
        with col2:
            st.subheader("Run Backtest")
            
            if st.button("🎯 Start Backtest", type="primary", use_container_width=True):
                run_backtest(confidence_threshold)
        
        # Progress and status
        if st.session_state.get('backtest_running', False):
            st.info("🔄 Backtest in progress... This may take a few minutes.")
    
    with tab3:
        st.header("📈 Results Dashboard")
        
        if st.session_state.results_df.empty:
            st.info("📊 Run a backtest to see results here.")
            return
        
        display_results_dashboard()
    
    with tab4:
        st.header("📋 Trade Details")
        
        if st.session_state.results_df.empty:
            st.info("📋 Run a backtest to see trade details here.")
            return
        
        display_trade_details()

def run_backtest(confidence_threshold):
    """Run the backtest with progress tracking."""
    try:
        st.session_state.backtest_running = True
        
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Initialize bot with current parameters
        bot = st.session_state.bot
        
        # Update status
        status_text.text("Loading news data...")
        progress_bar.progress(10)
        
        # Load data
        if isinstance(st.session_state.news_file_path, str):
            file_path = st.session_state.news_file_path
        else:
            # Handle uploaded file
            file_path = 'data/temp_upload.csv'
            os.makedirs('data', exist_ok=True)
            with open(file_path, 'wb') as f:
                f.write(st.session_state.news_file_path.getvalue())
        
        # Run backtest
        status_text.text("Running backtest...")
        progress_bar.progress(30)
        
        results_df, performance = bot.run_full_backtest(file_path, confidence_threshold)
        
        progress_bar.progress(100)
        status_text.text("Backtest completed!")
        
        # Store results
        st.session_state.results_df = results_df
        st.session_state.performance = performance
        st.session_state.backtest_running = False
        
        st.success("✅ Backtest completed successfully!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error running backtest: {e}")
        st.session_state.backtest_running = False

def display_results_dashboard():
    """Display the results dashboard with metrics and charts."""
    results_df = st.session_state.results_df
    performance = st.session_state.performance
    
    # Key metrics
    st.subheader("🎯 Key Performance Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card success-metric">
            <h3>{performance.get('total_trades', 0)}</h3>
            <p>Total Trades</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        win_rate = performance.get('win_rate', 0) * 100
        color_class = "success-metric" if win_rate >= 50 else "warning-metric"
        st.markdown(f"""
        <div class="metric-card {color_class}">
            <h3>{win_rate:.1f}%</h3>
            <p>Win Rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_return = performance.get('total_return_pct', 0)
        color_class = "success-metric" if total_return >= 0 else "danger-metric"
        st.markdown(f"""
        <div class="metric-card {color_class}">
            <h3>{total_return:.1f}%</h3>
            <p>Total Return</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        sharpe = performance.get('sharpe_ratio', 0)
        color_class = "success-metric" if sharpe >= 1 else "warning-metric"
        st.markdown(f"""
        <div class="metric-card {color_class}">
            <h3>{sharpe:.2f}</h3>
            <p>Sharpe Ratio</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        final_capital = performance.get('final_capital', 0)
        st.markdown(f"""
        <div class="metric-card">
            <h3>${final_capital:,.0f}</h3>
            <p>Final Capital</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    st.subheader("📊 Performance Charts")
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Cumulative Returns', 'Return Distribution', 
                       'Outcome Distribution', 'Monthly Performance'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # 1. Cumulative Returns
    cumulative_returns = (1 + results_df['return_pct'] / 100).cumprod()
    fig.add_trace(
        go.Scatter(x=list(range(len(cumulative_returns))), y=cumulative_returns,
                  mode='lines', name='Cumulative Returns', line=dict(color='#1f77b4')),
        row=1, col=1
    )
    
    # 2. Return Distribution
    fig.add_trace(
        go.Histogram(x=results_df['return_pct'], nbinsx=30, name='Returns',
                    marker_color='#ff7f0e', opacity=0.7),
        row=1, col=2
    )
    
    # 3. Outcome Distribution
    outcome_counts = results_df['outcome'].value_counts()
    fig.add_trace(
        go.Bar(x=outcome_counts.index, y=outcome_counts.values, name='Outcomes',
               marker_color=['#2ca02c', '#d62728', '#ff7f0e']),
        row=2, col=1
    )
    
    # 4. Monthly Performance
    results_df['month'] = pd.to_datetime(results_df['date']).dt.to_period('M')
    monthly_returns = results_df.groupby('month')['return_pct'].sum()
    colors = ['#2ca02c' if x >= 0 else '#d62728' for x in monthly_returns.values]
    fig.add_trace(
        go.Bar(x=[str(m) for m in monthly_returns.index], y=monthly_returns.values,
               name='Monthly Returns', marker_color=colors),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=False, title_text="Performance Dashboard")
    st.plotly_chart(fig, use_container_width=True)
    
    # Additional insights
    st.subheader("🔍 Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Best Performing Tickers:**")
        ticker_performance = results_df.groupby('ticker')['return_pct'].agg(['count', 'mean', 'sum']).round(2)
        ticker_performance.columns = ['Trades', 'Avg Return %', 'Total Return %']
        ticker_performance = ticker_performance.sort_values('Total Return %', ascending=False).head(10)
        st.dataframe(ticker_performance)
    
    with col2:
        st.write("**Performance by Confidence Score:**")
        results_df['confidence_bucket'] = pd.cut(results_df['confidence_score'], 
                                               bins=[0, 0.6, 0.8, 1.0], 
                                               labels=['Low', 'Medium', 'High'])
        confidence_performance = results_df.groupby('confidence_bucket')['return_pct'].agg(['count', 'mean']).round(2)
        confidence_performance.columns = ['Trades', 'Avg Return %']
        st.dataframe(confidence_performance)

def display_trade_details():
    """Display detailed trade information."""
    results_df = st.session_state.results_df
    
    # Filters
    st.subheader("🔍 Filter Trades")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        outcome_filter = st.selectbox("Outcome", ['All'] + list(results_df['outcome'].unique()))
    
    with col2:
        ticker_filter = st.selectbox("Ticker", ['All'] + sorted(results_df['ticker'].unique()))
    
    with col3:
        min_confidence = st.slider("Min Confidence", 0.0, 1.0, 0.0)
    
    with col4:
        position_filter = st.selectbox("Position Type", ['All'] + list(results_df['position_type'].unique()))
    
    # Apply filters
    filtered_df = results_df.copy()
    
    if outcome_filter != 'All':
        filtered_df = filtered_df[filtered_df['outcome'] == outcome_filter]
    
    if ticker_filter != 'All':
        filtered_df = filtered_df[filtered_df['ticker'] == ticker_filter]
    
    if position_filter != 'All':
        filtered_df = filtered_df[filtered_df['position_type'] == position_filter]
    
    filtered_df = filtered_df[filtered_df['confidence_score'] >= min_confidence]
    
    # Display filtered results
    st.subheader(f"📋 Trade Details ({len(filtered_df)} trades)")
    
    if not filtered_df.empty:
        # Format the dataframe for display
        display_df = filtered_df.copy()
        display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m-%d')
        display_df['return_pct'] = display_df['return_pct'].round(2)
        display_df['confidence_score'] = display_df['confidence_score'].round(3)
        display_df['buy_price'] = display_df['buy_price'].round(2)
        display_df['exit_price'] = display_df['exit_price'].round(2)
        
        # Select columns to display
        columns_to_show = [
            'date', 'ticker', 'outcome', 'return_pct', 'confidence_score',
            'position_type', 'buy_price', 'exit_price', 'days_held', 'source'
        ]
        
        st.dataframe(
            display_df[columns_to_show],
            use_container_width=True,
            hide_index=True
        )
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Results",
            data=csv,
            file_name=f"sniper_bot_trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No trades match the current filters.")

if __name__ == "__main__":
    main() 