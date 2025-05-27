#!/usr/bin/env python3
"""
🔍 Railway Log Analyzer
Analyzes Railway bot logs to extract performance data and suggest optimizations
"""

import re
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
import statistics

@dataclass
class LogTrade:
    """Trade extracted from Railway logs."""
    timestamp: datetime
    trade_id: str
    pair: str
    signal_type: str
    confidence: float
    entry_price: float
    target_price: float
    stop_loss: float
    units: int
    expected_profit: float
    expected_loss: float
    risk_reward_ratio: float
    status: str = "UNKNOWN"
    actual_profit: Optional[float] = None
    pips_gained: Optional[float] = None

class RailwayLogAnalyzer:
    """Analyze Railway bot logs for performance insights."""
    
    def __init__(self):
        self.trades: List[LogTrade] = []
        self.balance_history = []
        self.performance_reports = []
        
    def parse_log_file(self, log_content: str):
        """Parse Railway log content to extract trading data."""
        lines = log_content.split('\n')
        
        for line in lines:
            self._parse_trade_execution(line)
            self._parse_balance_update(line)
            self._parse_performance_report(line)
            self._parse_trade_closure(line)
    
    def _parse_trade_execution(self, line: str):
        """Extract trade execution data from log line."""
        # Look for trade execution patterns
        trade_pattern = r"📊 TRADE RECORDED: (\w+/\w+) (\w+) \| ID: (\w+) \| Confidence: ([\d.]+)%"
        match = re.search(trade_pattern, line)
        
        if match:
            pair, signal_type, trade_id, confidence = match.groups()
            
            # Extract timestamp
            timestamp_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
            timestamp_match = re.search(timestamp_pattern, line)
            timestamp = datetime.strptime(timestamp_match.group(1), "%Y-%m-%d %H:%M:%S") if timestamp_match else datetime.now()
            
            # Create trade record (will be updated with more details from subsequent logs)
            trade = LogTrade(
                timestamp=timestamp,
                trade_id=trade_id,
                pair=pair,
                signal_type=signal_type,
                confidence=float(confidence) / 100,
                entry_price=0,  # Will be updated
                target_price=0,  # Will be updated
                stop_loss=0,    # Will be updated
                units=0,        # Will be updated
                expected_profit=0,  # Will be updated
                expected_loss=0,    # Will be updated
                risk_reward_ratio=0  # Will be updated
            )
            
            self.trades.append(trade)
    
    def _parse_balance_update(self, line: str):
        """Extract balance updates from log lines."""
        balance_pattern = r"💰 Account Balance: \$([,\d.]+)"
        match = re.search(balance_pattern, line)
        
        if match:
            balance_str = match.group(1).replace(',', '')
            balance = float(balance_str)
            
            timestamp_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
            timestamp_match = re.search(timestamp_pattern, line)
            timestamp = datetime.strptime(timestamp_match.group(1), "%Y-%m-%d %H:%M:%S") if timestamp_match else datetime.now()
            
            self.balance_history.append({
                'timestamp': timestamp,
                'balance': balance
            })
    
    def _parse_performance_report(self, line: str):
        """Extract performance report data."""
        if "📊 RAILWAY BOT PERFORMANCE REPORT" in line:
            # Mark start of performance report
            self.performance_reports.append({
                'timestamp': datetime.now(),
                'type': 'PERFORMANCE_REPORT'
            })
    
    def _parse_trade_closure(self, line: str):
        """Extract trade closure information."""
        closure_pattern = r"🎯 TRADE CLOSED: (\w+/\w+) (\w+) \| (\w+) \| ([-\d.]+) pips \| \$([-\d.]+)"
        match = re.search(closure_pattern, line)
        
        if match:
            pair, signal_type, status, pips, profit = match.groups()
            
            # Find corresponding trade and update
            for trade in reversed(self.trades):  # Search from most recent
                if trade.pair == pair and trade.signal_type == signal_type and trade.status == "UNKNOWN":
                    trade.status = status
                    trade.pips_gained = float(pips)
                    trade.actual_profit = float(profit)
                    break
    
    def analyze_performance(self) -> Dict:
        """Analyze overall performance from logs."""
        if not self.trades:
            return {'error': 'No trades found in logs'}
        
        # Basic statistics
        total_trades = len(self.trades)
        closed_trades = [t for t in self.trades if t.status in ['CLOSED_WIN', 'CLOSED_LOSS']]
        open_trades = [t for t in self.trades if t.status == 'UNKNOWN']
        
        if not closed_trades:
            return {
                'total_trades': total_trades,
                'open_trades': len(open_trades),
                'status': 'No closed trades yet for analysis'
            }
        
        # Win rate analysis
        winners = [t for t in closed_trades if t.status == 'CLOSED_WIN']
        win_rate = len(winners) / len(closed_trades)
        
        # Profit analysis
        total_profit = sum([t.actual_profit for t in closed_trades if t.actual_profit])
        avg_win = statistics.mean([t.actual_profit for t in winners if t.actual_profit]) if winners else 0
        avg_loss = statistics.mean([t.actual_profit for t in closed_trades if t.status == 'CLOSED_LOSS' and t.actual_profit]) if any(t.status == 'CLOSED_LOSS' for t in closed_trades) else 0
        
        # Confidence analysis
        avg_confidence = statistics.mean([t.confidence for t in self.trades])
        confidence_vs_success = self._analyze_confidence_correlation()
        
        # Pair performance
        pair_performance = self._analyze_pair_performance()
        
        # Time analysis
        time_analysis = self._analyze_time_patterns()
        
        return {
            'total_trades': total_trades,
            'open_trades': len(open_trades),
            'closed_trades': len(closed_trades),
            'win_rate': win_rate,
            'total_profit': total_profit,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'avg_confidence': avg_confidence,
            'confidence_analysis': confidence_vs_success,
            'pair_performance': pair_performance,
            'time_analysis': time_analysis,
            'balance_progression': self._analyze_balance_progression()
        }
    
    def _analyze_confidence_correlation(self) -> Dict:
        """Analyze correlation between confidence and success rate."""
        confidence_buckets = {
            'low': [],    # 45-55%
            'medium': [], # 55-70%
            'high': []    # 70%+
        }
        
        for trade in self.trades:
            if trade.status in ['CLOSED_WIN', 'CLOSED_LOSS']:
                if trade.confidence < 0.55:
                    confidence_buckets['low'].append(trade)
                elif trade.confidence < 0.70:
                    confidence_buckets['medium'].append(trade)
                else:
                    confidence_buckets['high'].append(trade)
        
        analysis = {}
        for bucket, trades in confidence_buckets.items():
            if trades:
                winners = [t for t in trades if t.status == 'CLOSED_WIN']
                win_rate = len(winners) / len(trades)
                avg_profit = statistics.mean([t.actual_profit for t in trades if t.actual_profit])
                
                analysis[bucket] = {
                    'trades': len(trades),
                    'win_rate': win_rate,
                    'avg_profit': avg_profit,
                    'avg_confidence': statistics.mean([t.confidence for t in trades])
                }
        
        return analysis
    
    def _analyze_pair_performance(self) -> Dict:
        """Analyze performance by currency pair."""
        pair_stats = {}
        
        for trade in self.trades:
            if trade.pair not in pair_stats:
                pair_stats[trade.pair] = {
                    'total': 0,
                    'wins': 0,
                    'losses': 0,
                    'profit': 0,
                    'confidences': []
                }
            
            pair_stats[trade.pair]['total'] += 1
            pair_stats[trade.pair]['confidences'].append(trade.confidence)
            
            if trade.status == 'CLOSED_WIN':
                pair_stats[trade.pair]['wins'] += 1
                if trade.actual_profit:
                    pair_stats[trade.pair]['profit'] += trade.actual_profit
            elif trade.status == 'CLOSED_LOSS':
                pair_stats[trade.pair]['losses'] += 1
                if trade.actual_profit:
                    pair_stats[trade.pair]['profit'] += trade.actual_profit
        
        # Calculate win rates and averages
        for pair, stats in pair_stats.items():
            closed = stats['wins'] + stats['losses']
            stats['win_rate'] = stats['wins'] / closed if closed > 0 else 0
            stats['avg_confidence'] = statistics.mean(stats['confidences']) if stats['confidences'] else 0
        
        return pair_stats
    
    def _analyze_time_patterns(self) -> Dict:
        """Analyze performance by time patterns."""
        hourly_performance = {}
        daily_performance = {}
        
        for trade in self.trades:
            hour = trade.timestamp.hour
            day = trade.timestamp.strftime('%A')
            
            # Hourly analysis
            if hour not in hourly_performance:
                hourly_performance[hour] = {'trades': 0, 'wins': 0}
            hourly_performance[hour]['trades'] += 1
            if trade.status == 'CLOSED_WIN':
                hourly_performance[hour]['wins'] += 1
            
            # Daily analysis
            if day not in daily_performance:
                daily_performance[day] = {'trades': 0, 'wins': 0}
            daily_performance[day]['trades'] += 1
            if trade.status == 'CLOSED_WIN':
                daily_performance[day]['wins'] += 1
        
        # Calculate win rates
        for hour_data in hourly_performance.values():
            hour_data['win_rate'] = hour_data['wins'] / hour_data['trades'] if hour_data['trades'] > 0 else 0
        
        for day_data in daily_performance.values():
            day_data['win_rate'] = day_data['wins'] / day_data['trades'] if day_data['trades'] > 0 else 0
        
        return {
            'hourly': hourly_performance,
            'daily': daily_performance
        }
    
    def _analyze_balance_progression(self) -> Dict:
        """Analyze account balance progression."""
        if len(self.balance_history) < 2:
            return {'error': 'Insufficient balance data'}
        
        starting_balance = self.balance_history[0]['balance']
        current_balance = self.balance_history[-1]['balance']
        total_return = current_balance - starting_balance
        return_pct = (total_return / starting_balance) * 100
        
        # Calculate daily returns
        daily_returns = []
        for i in range(1, len(self.balance_history)):
            prev_balance = self.balance_history[i-1]['balance']
            curr_balance = self.balance_history[i]['balance']
            daily_return = (curr_balance - prev_balance) / prev_balance * 100
            daily_returns.append(daily_return)
        
        return {
            'starting_balance': starting_balance,
            'current_balance': current_balance,
            'total_return': total_return,
            'return_percentage': return_pct,
            'avg_daily_return': statistics.mean(daily_returns) if daily_returns else 0,
            'volatility': statistics.stdev(daily_returns) if len(daily_returns) > 1 else 0
        }
    
    def generate_optimization_suggestions(self, analysis: Dict) -> List[str]:
        """Generate optimization suggestions based on analysis."""
        suggestions = []
        
        # Confidence threshold optimization
        if 'confidence_analysis' in analysis:
            conf_analysis = analysis['confidence_analysis']
            if 'high' in conf_analysis and conf_analysis['high']['win_rate'] > 0.7:
                suggestions.append("🎯 Consider raising minimum confidence threshold to 70% - high confidence trades show excellent win rate")
            elif 'low' in conf_analysis and conf_analysis['low']['win_rate'] < 0.5:
                suggestions.append("⚠️ Consider raising minimum confidence threshold - low confidence trades underperforming")
        
        # Pair-specific suggestions
        if 'pair_performance' in analysis:
            pair_perf = analysis['pair_performance']
            best_pairs = [pair for pair, stats in pair_perf.items() if stats.get('win_rate', 0) > 0.7]
            worst_pairs = [pair for pair, stats in pair_perf.items() if stats.get('win_rate', 0) < 0.4]
            
            if best_pairs:
                suggestions.append(f"📈 Focus on high-performing pairs: {', '.join(best_pairs)}")
            if worst_pairs:
                suggestions.append(f"📉 Consider excluding underperforming pairs: {', '.join(worst_pairs)}")
        
        # Time-based suggestions
        if 'time_analysis' in analysis:
            time_analysis = analysis['time_analysis']
            if 'hourly' in time_analysis:
                best_hours = [str(hour) for hour, stats in time_analysis['hourly'].items() if stats.get('win_rate', 0) > 0.7]
                if best_hours:
                    suggestions.append(f"⏰ Best trading hours: {', '.join(best_hours)}:00 UTC")
        
        # Risk management suggestions
        if analysis.get('win_rate', 0) > 0.7:
            suggestions.append("💰 Consider increasing position size - high win rate indicates good signal quality")
        elif analysis.get('win_rate', 0) < 0.5:
            suggestions.append("🛡️ Consider reducing position size until performance improves")
        
        return suggestions
    
    def generate_report(self, analysis: Dict) -> str:
        """Generate a comprehensive performance report."""
        report = []
        report.append("🔍 RAILWAY BOT LOG ANALYSIS REPORT")
        report.append("=" * 50)
        
        # Basic performance
        report.append(f"📊 Total Trades: {analysis.get('total_trades', 0)}")
        report.append(f"🔄 Open Trades: {analysis.get('open_trades', 0)}")
        report.append(f"✅ Closed Trades: {analysis.get('closed_trades', 0)}")
        
        if analysis.get('closed_trades', 0) > 0:
            report.append(f"🎯 Win Rate: {analysis.get('win_rate', 0):.1%}")
            report.append(f"💰 Total Profit: ${analysis.get('total_profit', 0):.2f}")
            report.append(f"📊 Average Win: ${analysis.get('avg_win', 0):.2f}")
            report.append(f"📉 Average Loss: ${analysis.get('avg_loss', 0):.2f}")
        
        # Balance progression
        if 'balance_progression' in analysis:
            bal_prog = analysis['balance_progression']
            if 'error' not in bal_prog:
                report.append("")
                report.append("💰 BALANCE PROGRESSION:")
                report.append(f"   Starting: ${bal_prog['starting_balance']:,.2f}")
                report.append(f"   Current: ${bal_prog['current_balance']:,.2f}")
                report.append(f"   Return: ${bal_prog['total_return']:+,.2f} ({bal_prog['return_percentage']:+.2f}%)")
        
        # Optimization suggestions
        suggestions = self.generate_optimization_suggestions(analysis)
        if suggestions:
            report.append("")
            report.append("🔧 OPTIMIZATION SUGGESTIONS:")
            for suggestion in suggestions:
                report.append(f"   {suggestion}")
        
        return "\n".join(report)

def analyze_railway_logs(log_content: str) -> str:
    """Main function to analyze Railway logs and return report."""
    analyzer = RailwayLogAnalyzer()
    analyzer.parse_log_file(log_content)
    analysis = analyzer.analyze_performance()
    return analyzer.generate_report(analysis)

if __name__ == "__main__":
    print("🔍 Railway Log Analyzer")
    print("Copy your Railway logs and paste them when prompted...")
    print("Press Ctrl+D (Unix) or Ctrl+Z (Windows) when done.")
    
    try:
        log_content = ""
        while True:
            line = input()
            log_content += line + "\n"
    except EOFError:
        pass
    
    if log_content.strip():
        report = analyze_railway_logs(log_content)
        print("\n" + report)
    else:
        print("No log content provided.") 