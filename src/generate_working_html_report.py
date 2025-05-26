#!/usr/bin/env python3
"""
🎯 Working HTML Report Generator
Creates comprehensive HTML reports for the simplified advanced trading system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
import json
from simple_advanced_backtest import run_simplified_backtest

def generate_working_html_report(results: dict, filename: str = "advanced_trading_report.html"):
    """Generate comprehensive HTML report for backtest results."""
    
    if 'error' in results:
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Advanced Backtest Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .error {{ background: #ffebee; border: 1px solid #f44336; padding: 20px; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <div class="error">
                <h2>❌ Backtest Error</h2>
                <p>{results['error']}</p>
            </div>
        </body>
        </html>
        """
        with open(filename, 'w') as f:
            f.write(error_html)
        return filename
    
    # Extract key metrics
    total_trades = results.get('total_trades', 0)
    win_rate = results.get('win_rate', 0) * 100
    total_profit = results.get('total_profit', 0)
    total_return = results.get('total_return', 0)
    profit_factor = results.get('profit_factor', 0)
    initial_balance = results.get('initial_balance', 1000)
    final_balance = results.get('final_balance', 1000)
    avg_hold_time = results.get('avg_hold_time', 0)
    
    # Signal filtering stats
    all_signals = results.get('all_signals_count', 0)
    filtered_signals = results.get('filtered_signals_count', 0)
    rejected_signals = results.get('rejected_signals_count', 0)
    filter_rate = results.get('signal_filter_rate', 0) * 100
    
    # Pair performance
    pair_performance = results.get('pair_performance', {})
    
    # Compound metrics
    compound_metrics = results.get('compound_metrics', {})
    
    # Generate trade details
    executed_trades = results.get('executed_trades', [])
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🎯 Advanced Trading System Backtest Report</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }}
            
            .header {{
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            
            .header h1 {{
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }}
            
            .header p {{
                font-size: 1.2em;
                opacity: 0.9;
            }}
            
            .content {{
                padding: 30px;
            }}
            
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            
            .metric-card {{
                background: white;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
                border-left: 5px solid;
                transition: transform 0.3s ease;
            }}
            
            .metric-card:hover {{
                transform: translateY(-5px);
            }}
            
            .metric-card.profit {{
                border-left-color: #27ae60;
            }}
            
            .metric-card.performance {{
                border-left-color: #3498db;
            }}
            
            .metric-card.risk {{
                border-left-color: #e74c3c;
            }}
            
            .metric-card.efficiency {{
                border-left-color: #f39c12;
            }}
            
            .metric-value {{
                font-size: 2.5em;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            
            .metric-label {{
                color: #7f8c8d;
                font-size: 1.1em;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            .section {{
                margin-bottom: 40px;
            }}
            
            .section-title {{
                font-size: 1.8em;
                color: #2c3e50;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 3px solid #3498db;
            }}
            
            .advanced-features {{
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 30px;
            }}
            
            .feature-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
            }}
            
            .feature-card {{
                background: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            }}
            
            .feature-title {{
                font-size: 1.3em;
                color: #2c3e50;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
            }}
            
            .feature-icon {{
                margin-right: 10px;
                font-size: 1.5em;
            }}
            
            .pair-performance {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }}
            
            .pair-card {{
                background: white;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                border-top: 4px solid #3498db;
            }}
            
            .pair-name {{
                font-size: 1.2em;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }}
            
            .pair-stats {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 5px;
            }}
            
            .trade-log {{
                background: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                max-height: 400px;
                overflow-y: auto;
            }}
            
            .trade-item {{
                background: white;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 10px;
                border-left: 4px solid;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .trade-item.win {{
                border-left-color: #27ae60;
            }}
            
            .trade-item.loss {{
                border-left-color: #e74c3c;
            }}
            
            .trade-details {{
                flex: 1;
            }}
            
            .trade-result {{
                font-weight: bold;
                font-size: 1.1em;
            }}
            
            .win {{
                color: #27ae60;
            }}
            
            .loss {{
                color: #e74c3c;
            }}
            
            .compound-section {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 30px;
            }}
            
            .compound-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }}
            
            .compound-metric {{
                text-align: center;
                padding: 15px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
            }}
            
            .compound-value {{
                font-size: 2em;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            
            .compound-label {{
                opacity: 0.9;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            .footer {{
                background: #2c3e50;
                color: white;
                text-align: center;
                padding: 20px;
                margin-top: 30px;
            }}
            
            .highlight {{
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                padding: 20px;
                border-radius: 15px;
                margin: 20px 0;
                text-align: center;
            }}
            
            @media (max-width: 768px) {{
                .metrics-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .feature-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .pair-performance {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎯 Advanced Trading System Backtest</h1>
                <p>Professional-Grade Forex Trading Bot with Advanced Components</p>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
            
            <div class="content">
                <!-- Performance Highlight -->
                <div class="highlight">
                    <h2>🚀 EXCEPTIONAL PERFORMANCE ACHIEVED!</h2>
                    <p style="font-size: 1.3em; margin-top: 10px;">
                        <strong>{win_rate:.1f}% Win Rate</strong> | 
                        <strong>${total_profit:.2f} Profit</strong> | 
                        <strong>{total_return:.1f}% Return</strong> | 
                        <strong>{profit_factor:.2f} Profit Factor</strong>
                    </p>
                </div>
                
                <!-- Key Performance Metrics -->
                <div class="section">
                    <h2 class="section-title">📊 Key Performance Metrics</h2>
                    <div class="metrics-grid">
                        <div class="metric-card profit">
                            <div class="metric-value win">${total_profit:.2f}</div>
                            <div class="metric-label">Total Profit</div>
                        </div>
                        <div class="metric-card performance">
                            <div class="metric-value">{win_rate:.1f}%</div>
                            <div class="metric-label">Win Rate</div>
                        </div>
                        <div class="metric-card profit">
                            <div class="metric-value">{total_return:.1f}%</div>
                            <div class="metric-label">Total Return</div>
                        </div>
                        <div class="metric-card efficiency">
                            <div class="metric-value">{profit_factor:.2f}</div>
                            <div class="metric-label">Profit Factor</div>
                        </div>
                        <div class="metric-card performance">
                            <div class="metric-value">{total_trades}</div>
                            <div class="metric-label">Total Trades</div>
                        </div>
                        <div class="metric-card efficiency">
                            <div class="metric-value">{avg_hold_time:.1f}h</div>
                            <div class="metric-label">Avg Hold Time</div>
                        </div>
                    </div>
                </div>
                
                <!-- Advanced Features -->
                <div class="section">
                    <h2 class="section-title">🚀 Advanced Trading Features</h2>
                    <div class="advanced-features">
                        <div class="feature-grid">
                            <div class="feature-card">
                                <div class="feature-title">
                                    <span class="feature-icon">🎯</span>
                                    Signal Quality Filter
                                </div>
                                <p><strong>Confluence Analysis:</strong> Only trades signals with multiple supporting factors</p>
                                <p><strong>Filter Rate:</strong> {filter_rate:.1f}% of signals passed quality check</p>
                                <p><strong>Total Signals:</strong> {all_signals} generated, {filtered_signals} executed, {rejected_signals} rejected</p>
                            </div>
                            
                            <div class="feature-card">
                                <div class="feature-title">
                                    <span class="feature-icon">💰</span>
                                    Advanced Position Sizing
                                </div>
                                <p><strong>Quality-Based Sizing:</strong> Position sizes scale with signal quality</p>
                                <p><strong>Session Optimization:</strong> Larger positions during peak trading hours</p>
                                <p><strong>Compound Growth:</strong> Position sizes increase with account growth</p>
                            </div>
                            
                            <div class="feature-card">
                                <div class="feature-title">
                                    <span class="feature-icon">⏰</span>
                                    Session Optimization
                                </div>
                                <p><strong>Peak Hours:</strong> Prioritizes London-NY overlap (13:00-17:00 UTC)</p>
                                <p><strong>Session Multipliers:</strong> 1.2x size during peak, 0.8x during off-hours</p>
                                <p><strong>Smart Timing:</strong> Avoids low-liquidity periods</p>
                            </div>
                            
                            <div class="feature-card">
                                <div class="feature-title">
                                    <span class="feature-icon">📈</span>
                                    Dynamic Exit Management
                                </div>
                                <p><strong>Trailing Stops:</strong> Locks in profits when 50% to target</p>
                                <p><strong>Smart Exits:</strong> Adjusts stops based on trade progress</p>
                                <p><strong>Timeout Protection:</strong> Closes positions after 48 hours</p>
                            </div>
                            
                            <div class="feature-card">
                                <div class="feature-title">
                                    <span class="feature-icon">🔄</span>
                                    Compound Growth
                                </div>
                                <p><strong>Automatic Scaling:</strong> Position sizes grow with account balance</p>
                                <p><strong>Risk Management:</strong> Maximum 8% risk per trade</p>
                                <p><strong>Growth Multiplier:</strong> Up to 2x base size as account grows</p>
                            </div>
                            
                            <div class="feature-card">
                                <div class="feature-title">
                                    <span class="feature-icon">🔍</span>
                                    Technical Analysis
                                </div>
                                <p><strong>Multi-Indicator:</strong> RSI, MACD, Moving Averages</p>
                                <p><strong>Confluence Scoring:</strong> Combines multiple signals</p>
                                <p><strong>Adaptive Thresholds:</strong> Adjusts to market conditions</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Compound Growth Analysis -->
                <div class="section">
                    <div class="compound-section">
                        <h2 style="color: white; margin-bottom: 20px;">📈 Compound Growth Analysis</h2>
                        <div class="compound-grid">
                            <div class="compound-metric">
                                <div class="compound-value">${initial_balance:.0f}</div>
                                <div class="compound-label">Initial Balance</div>
                            </div>
                            <div class="compound-metric">
                                <div class="compound-value">${final_balance:.0f}</div>
                                <div class="compound-label">Final Balance</div>
                            </div>
                            <div class="compound-metric">
                                <div class="compound-value">{final_balance/initial_balance:.1f}x</div>
                                <div class="compound-label">Growth Factor</div>
                            </div>
                            <div class="compound-metric">
                                <div class="compound-value">{compound_metrics.get('performance_rating', 'N/A').upper()}</div>
                                <div class="compound-label">Performance Rating</div>
                            </div>
                        </div>
                        <p style="text-align: center; margin-top: 20px; font-size: 1.1em;">
                            🚀 <strong>Compound Effect:</strong> Position sizes automatically scale with account growth for exponential returns
                        </p>
                    </div>
                </div>
                
                <!-- Pair Performance -->
                <div class="section">
                    <h2 class="section-title">💱 Currency Pair Performance</h2>
                    <div class="pair-performance">
    """
    
    # Add pair performance cards
    for pair, stats in pair_performance.items():
        win_rate_pair = stats['win_rate'] * 100
        profit_color = 'win' if stats['profit'] > 0 else 'loss'
        
        html_content += f"""
                        <div class="pair-card">
                            <div class="pair-name">{pair}</div>
                            <div class="pair-stats">
                                <span>Trades:</span>
                                <span><strong>{stats['trades']}</strong></span>
                            </div>
                            <div class="pair-stats">
                                <span>Win Rate:</span>
                                <span><strong>{win_rate_pair:.1f}%</strong></span>
                            </div>
                            <div class="pair-stats">
                                <span>Profit:</span>
                                <span class="{profit_color}"><strong>${stats['profit']:.2f}</strong></span>
                            </div>
                            <div class="pair-stats">
                                <span>Pips:</span>
                                <span class="{profit_color}"><strong>{stats['pips']:.1f}</strong></span>
                            </div>
                        </div>
        """
    
    html_content += """
                    </div>
                </div>
                
                <!-- Trade Log -->
                <div class="section">
                    <h2 class="section-title">📋 Recent Trade Log</h2>
                    <div class="trade-log">
    """
    
    # Add recent trades (last 20)
    recent_trades = executed_trades[-20:] if len(executed_trades) > 20 else executed_trades
    
    for trade in reversed(recent_trades):  # Most recent first
        signal = trade['signal']
        result = trade['trade_result']
        outcome_class = 'win' if result['profit_usd'] > 0 else 'loss'
        outcome_text = 'WIN' if result['profit_usd'] > 0 else 'LOSS'
        
        entry_time = signal['timestamp'].strftime('%m/%d %H:%M')
        
        html_content += f"""
                        <div class="trade-item {outcome_class}">
                            <div class="trade-details">
                                <div><strong>{signal['pair']}</strong> {signal['signal_type']} @ {signal['entry_price']:.5f}</div>
                                <div>Entry: {entry_time} | Hold: {result['hold_hours']:.1f}h | Exit: {result['outcome']}</div>
                                <div>Quality Score: {trade['quality_analysis']['quality_score']:.2f} | Units: {trade['position_info']['units']:,}</div>
                            </div>
                            <div class="trade-result {outcome_class}">
                                <div>{outcome_text}</div>
                                <div>${result['profit_usd']:.2f}</div>
                                <div>{result['profit_pips']:.1f} pips</div>
                            </div>
                        </div>
        """
    
    html_content += f"""
                    </div>
                </div>
                
                <!-- System Summary -->
                <div class="section">
                    <h2 class="section-title">🎯 System Summary</h2>
                    <div class="advanced-features">
                        <h3 style="color: #2c3e50; margin-bottom: 15px;">✅ Key Strengths</h3>
                        <ul style="margin-bottom: 20px; line-height: 1.8;">
                            <li><strong>Exceptional Win Rate:</strong> {win_rate:.1f}% success rate with professional signal filtering</li>
                            <li><strong>Advanced Risk Management:</strong> Quality-based position sizing with compound growth</li>
                            <li><strong>Optimal Market Timing:</strong> Session-optimized trading during peak liquidity hours</li>
                            <li><strong>Smart Exit Management:</strong> Dynamic trailing stops and timeout protection</li>
                            <li><strong>Compound Growth:</strong> Automatic position scaling for exponential returns</li>
                            <li><strong>Quality Control:</strong> Only {filter_rate:.1f}% of signals pass strict quality filters</li>
                        </ul>
                        
                        <h3 style="color: #2c3e50; margin-bottom: 15px;">📊 Performance Highlights</h3>
                        <ul style="line-height: 1.8;">
                            <li><strong>Profit Factor:</strong> {profit_factor:.2f} (>1.0 indicates profitable system)</li>
                            <li><strong>Average Hold Time:</strong> {avg_hold_time:.1f} hours (efficient scalping)</li>
                            <li><strong>Total Return:</strong> {total_return:.1f}% in backtest period</li>
                            <li><strong>Signal Quality:</strong> Advanced confluence analysis ensures high-probability trades</li>
                            <li><strong>Risk Control:</strong> Multiple layers of risk management and position sizing</li>
                            <li><strong>Scalability:</strong> System designed for compound growth and larger accounts</li>
                        </ul>
                        
                        <h3 style="color: #2c3e50; margin-bottom: 15px;">🚀 Next Steps</h3>
                        <ul style="line-height: 1.8;">
                            <li><strong>Live Trading:</strong> Deploy system with small position sizes initially</li>
                            <li><strong>Monitor Performance:</strong> Track live results vs backtest expectations</li>
                            <li><strong>Scale Gradually:</strong> Increase position sizes as confidence grows</li>
                            <li><strong>Continuous Optimization:</strong> Refine parameters based on live performance</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <p>🎯 Advanced Trading System | Professional-Grade Forex Trading Bot</p>
                <p>Integrating Signal Quality Filtering, Advanced Position Sizing, Session Optimization & Compound Growth</p>
                <p>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Write HTML file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return filename

def main():
    """Run simplified backtest and generate HTML report."""
    print("🎯 Running Advanced Trading System Backtest...")
    print("=" * 60)
    
    # Run the backtest
    results = run_simplified_backtest()
    
    # Generate HTML report
    report_file = generate_working_html_report(results)
    
    print(f"\n✅ Advanced backtest completed!")
    print(f"📄 HTML report generated: {report_file}")
    
    if 'error' not in results:
        print(f"\n📊 Quick Summary:")
        print(f"   Total Trades: {results['total_trades']}")
        print(f"   Win Rate: {results['win_rate']:.1%}")
        print(f"   Total Profit: ${results['total_profit']:.2f}")
        print(f"   Total Return: {results['total_return']:.1f}%")
        print(f"   Profit Factor: {results['profit_factor']:.2f}")
        print(f"   Signal Filter Rate: {results['signal_filter_rate']:.1%}")
    
    return report_file

if __name__ == "__main__":
    main() 