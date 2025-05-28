#!/usr/bin/env python3
"""
Main entry point for Forex Trading App
Streamlit Cloud deployment
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main forex trading app
try:
    from forex_trading_app import main
    
    if __name__ == "__main__":
        main()
except ImportError as e:
    import streamlit as st
    st.error(f"Error importing forex trading app: {e}")
    st.info("Please ensure all dependencies are installed correctly.")
    
    # Fallback to a simple demo
    st.title("🚀 Forex Trading App")
    st.write("The main application is temporarily unavailable.")
    st.write("Please check the deployment logs for more information.") 