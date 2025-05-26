#!/usr/bin/env python3
"""
🎯 Signal Quality Filter - Only Take The Best Trades
Filters signals to only the highest probability setups
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)

class SignalQualityFilter:
    """
    Professional signal filtering to maximize win rate and profit
    Only trades signals with multiple confluence factors
    """
    
    def __init__(self):
        self.min_confluence_score = 0.7  # Minimum confluence required
        self.required_factors = 3  # Minimum number of supporting factors
        
        # Confluence weights
        self.confluence_weights = {
            'technical_alignment': 0.25,    # Multiple timeframes agree
            'sentiment_strength': 0.20,     # Strong news sentiment
            'volatility_optimal': 0.15,     # Optimal volatility conditions
            'session_timing': 0.15,         # Good market session timing
            'support_resistance': 0.15,     # Near key S/R levels
            'momentum_confirmation': 0.10   # Momentum indicators confirm
        }
        
        logger.info("🎯 Signal Quality Filter initialized")
    
    def analyze_technical_alignment(self, signal, technical_data: Dict) -> Dict:
        """Check if multiple timeframes align."""
        try:
            timeframe_scores = technical_data.get('timeframe_breakdown', {})
            
            if len(timeframe_scores) < 2:
                return {'score': 0.0, 'reason': 'Insufficient timeframe data'}
            
            # Check alignment between timeframes
            scores = list(timeframe_scores.values())
            signal_direction = 1 if signal.signal_type == "BUY" else -1
            
            # Count how many timeframes agree with signal direction
            agreeing_timeframes = 0
            total_timeframes = len(scores)
            
            for score in scores:
                if (signal_direction > 0 and score > 0.2) or (signal_direction < 0 and score < -0.2):
                    agreeing_timeframes += 1
            
            alignment_ratio = agreeing_timeframes / total_timeframes
            
            # Bonus for strong agreement
            if alignment_ratio >= 0.8:  # 80%+ agreement
                alignment_score = 1.0
                reason = f"Strong alignment: {agreeing_timeframes}/{total_timeframes} timeframes agree"
            elif alignment_ratio >= 0.6:  # 60%+ agreement
                alignment_score = 0.7
                reason = f"Good alignment: {agreeing_timeframes}/{total_timeframes} timeframes agree"
            else:
                alignment_score = 0.3
                reason = f"Weak alignment: {agreeing_timeframes}/{total_timeframes} timeframes agree"
            
            return {
                'score': alignment_score,
                'reason': reason,
                'agreeing_timeframes': agreeing_timeframes,
                'total_timeframes': total_timeframes
            }
            
        except Exception as e:
            logger.error(f"Error analyzing technical alignment: {e}")
            return {'score': 0.0, 'reason': 'Error in alignment analysis'}
    
    def analyze_sentiment_strength(self, signal) -> Dict:
        """Analyze strength and quality of news sentiment."""
        try:
            sentiment = signal.news_sentiment
            
            # Strong sentiment thresholds
            if abs(sentiment) >= 0.6:
                strength_score = 1.0
                reason = f"Very strong sentiment: {sentiment:.2f}"
            elif abs(sentiment) >= 0.4:
                strength_score = 0.8
                reason = f"Strong sentiment: {sentiment:.2f}"
            elif abs(sentiment) >= 0.2:
                strength_score = 0.5
                reason = f"Moderate sentiment: {sentiment:.2f}"
            else:
                strength_score = 0.2
                reason = f"Weak sentiment: {sentiment:.2f}"
            
            # Check sentiment direction alignment
            signal_direction = 1 if signal.signal_type == "BUY" else -1
            sentiment_direction = 1 if sentiment > 0 else -1
            
            if signal_direction == sentiment_direction:
                alignment_bonus = 0.2
                reason += " (aligned with signal)"
            else:
                alignment_bonus = -0.3
                reason += " (conflicts with signal)"
            
            final_score = max(0.0, min(1.0, strength_score + alignment_bonus))
            
            return {
                'score': final_score,
                'reason': reason,
                'sentiment_value': sentiment
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment strength: {e}")
            return {'score': 0.0, 'reason': 'Error in sentiment analysis'}
    
    def analyze_volatility_conditions(self, signal, pair_volatility: float = None) -> Dict:
        """Check if volatility conditions are optimal for trading."""
        try:
            # Get volatility from advanced position sizer if available
            if pair_volatility is None:
                # Default volatility estimates
                volatility_estimates = {
                    'EUR/USD': 0.08, 'GBP/USD': 0.12, 'USD/JPY': 0.09,
                    'USD/CHF': 0.10, 'AUD/USD': 0.11, 'USD/CAD': 0.09,
                    'NZD/USD': 0.13
                }
                pair_volatility = volatility_estimates.get(signal.pair, 0.10)
            
            # Optimal volatility range for forex scalping
            optimal_min = 0.06  # 6% annual volatility
            optimal_max = 0.15  # 15% annual volatility
            
            if optimal_min <= pair_volatility <= optimal_max:
                vol_score = 1.0
                reason = f"Optimal volatility: {pair_volatility:.1%}"
            elif pair_volatility < optimal_min:
                vol_score = 0.4
                reason = f"Low volatility: {pair_volatility:.1%} (may be slow)"
            else:  # Too high volatility
                vol_score = 0.3
                reason = f"High volatility: {pair_volatility:.1%} (risky)"
            
            return {
                'score': vol_score,
                'reason': reason,
                'volatility': pair_volatility
            }
            
        except Exception as e:
            logger.error(f"Error analyzing volatility: {e}")
            return {'score': 0.5, 'reason': 'Default volatility assumption'}
    
    def analyze_session_timing(self, signal) -> Dict:
        """Check if signal occurs during optimal trading sessions."""
        try:
            signal_time = signal.timestamp
            hour = signal_time.hour  # UTC hour
            
            # Market session scoring
            if 8 <= hour <= 16:  # London session
                if 13 <= hour <= 16:  # London-NY overlap
                    session_score = 1.0
                    reason = "London-NY overlap (highest liquidity)"
                else:
                    session_score = 0.8
                    reason = "London session (high liquidity)"
            elif 13 <= hour <= 21:  # New York session
                session_score = 0.8
                reason = "New York session (high liquidity)"
            elif 0 <= hour <= 8:  # Tokyo session
                session_score = 0.6
                reason = "Tokyo session (moderate liquidity)"
            else:  # Off-hours
                session_score = 0.3
                reason = "Off-hours (low liquidity)"
            
            # Day of week adjustment
            weekday = signal_time.weekday()
            if weekday in [0, 1, 2]:  # Monday-Wednesday (best days)
                day_bonus = 0.1
            elif weekday == 3:  # Thursday (good)
                day_bonus = 0.0
            else:  # Friday (avoid late Friday trades)
                day_bonus = -0.2
                reason += ", Friday (caution)"
            
            final_score = max(0.0, min(1.0, session_score + day_bonus))
            
            return {
                'score': final_score,
                'reason': reason,
                'session_hour': hour,
                'weekday': weekday
            }
            
        except Exception as e:
            logger.error(f"Error analyzing session timing: {e}")
            return {'score': 0.5, 'reason': 'Default session timing'}
    
    def analyze_support_resistance(self, signal) -> Dict:
        """Check proximity to key support/resistance levels."""
        try:
            entry_price = signal.entry_price
            target_price = signal.target_price
            stop_loss = signal.stop_loss
            
            # Calculate pip distances
            if 'JPY' in signal.pair:
                pip_value = 0.01
            else:
                pip_value = 0.0001
            
            target_pips = abs(target_price - entry_price) / pip_value
            stop_pips = abs(entry_price - stop_loss) / pip_value
            
            # Ideal pip ranges for scalping
            ideal_target_min, ideal_target_max = 20, 50
            ideal_stop_min, ideal_stop_max = 10, 30
            
            # Score target distance
            if ideal_target_min <= target_pips <= ideal_target_max:
                target_score = 1.0
            elif target_pips < ideal_target_min:
                target_score = 0.6  # Too small
            else:
                target_score = 0.4  # Too large
            
            # Score stop distance
            if ideal_stop_min <= stop_pips <= ideal_stop_max:
                stop_score = 1.0
            elif stop_pips < ideal_stop_min:
                stop_score = 0.7  # Too tight
            else:
                stop_score = 0.5  # Too wide
            
            # Risk:Reward ratio check
            risk_reward = target_pips / stop_pips if stop_pips > 0 else 1.0
            
            if risk_reward >= 1.5:
                rr_score = 1.0
                rr_reason = f"Good R:R {risk_reward:.1f}"
            elif risk_reward >= 1.2:
                rr_score = 0.8
                rr_reason = f"Acceptable R:R {risk_reward:.1f}"
            else:
                rr_score = 0.4
                rr_reason = f"Poor R:R {risk_reward:.1f}"
            
            # Combined score
            sr_score = (target_score + stop_score + rr_score) / 3
            
            reason = f"Target: {target_pips:.0f} pips, Stop: {stop_pips:.0f} pips, {rr_reason}"
            
            return {
                'score': sr_score,
                'reason': reason,
                'target_pips': target_pips,
                'stop_pips': stop_pips,
                'risk_reward': risk_reward
            }
            
        except Exception as e:
            logger.error(f"Error analyzing S/R levels: {e}")
            return {'score': 0.5, 'reason': 'Default S/R analysis'}
    
    def analyze_momentum_confirmation(self, signal, technical_data: Dict) -> Dict:
        """Check if momentum indicators confirm the signal."""
        try:
            technical_score = technical_data.get('score', 0)
            confidence = signal.confidence
            
            # Strong technical + high confidence = good momentum
            if abs(technical_score) >= 0.6 and confidence >= 0.7:
                momentum_score = 1.0
                reason = f"Strong momentum: tech={technical_score:.2f}, conf={confidence:.1%}"
            elif abs(technical_score) >= 0.4 and confidence >= 0.6:
                momentum_score = 0.8
                reason = f"Good momentum: tech={technical_score:.2f}, conf={confidence:.1%}"
            elif abs(technical_score) >= 0.2 and confidence >= 0.5:
                momentum_score = 0.6
                reason = f"Moderate momentum: tech={technical_score:.2f}, conf={confidence:.1%}"
            else:
                momentum_score = 0.3
                reason = f"Weak momentum: tech={technical_score:.2f}, conf={confidence:.1%}"
            
            return {
                'score': momentum_score,
                'reason': reason,
                'technical_score': technical_score,
                'confidence': confidence
            }
            
        except Exception as e:
            logger.error(f"Error analyzing momentum: {e}")
            return {'score': 0.5, 'reason': 'Default momentum analysis'}
    
    def calculate_confluence_score(self, signal, technical_data: Dict = None, 
                                 pair_volatility: float = None) -> Dict:
        """
        Calculate overall confluence score for signal quality
        """
        try:
            if technical_data is None:
                technical_data = {}
            
            logger.info(f"🔍 Analyzing signal quality for {signal.pair} {signal.signal_type}")
            
            # Analyze all confluence factors
            factors = {}
            
            factors['technical_alignment'] = self.analyze_technical_alignment(signal, technical_data)
            factors['sentiment_strength'] = self.analyze_sentiment_strength(signal)
            factors['volatility_optimal'] = self.analyze_volatility_conditions(signal, pair_volatility)
            factors['session_timing'] = self.analyze_session_timing(signal)
            factors['support_resistance'] = self.analyze_support_resistance(signal)
            factors['momentum_confirmation'] = self.analyze_momentum_confirmation(signal, technical_data)
            
            # Calculate weighted confluence score
            total_score = 0.0
            supporting_factors = 0
            
            for factor_name, factor_data in factors.items():
                factor_score = factor_data['score']
                weight = self.confluence_weights[factor_name]
                
                total_score += factor_score * weight
                
                # Count supporting factors (score > 0.6)
                if factor_score > 0.6:
                    supporting_factors += 1
                
                logger.info(f"  {factor_name}: {factor_score:.2f} - {factor_data['reason']}")
            
            # Quality assessment
            if total_score >= 0.8 and supporting_factors >= 4:
                quality = "EXCELLENT"
                recommendation = "STRONG BUY"
            elif total_score >= 0.7 and supporting_factors >= 3:
                quality = "GOOD"
                recommendation = "BUY"
            elif total_score >= 0.6 and supporting_factors >= 2:
                quality = "FAIR"
                recommendation = "CONSIDER"
            else:
                quality = "POOR"
                recommendation = "SKIP"
            
            result = {
                'confluence_score': total_score,
                'supporting_factors': supporting_factors,
                'required_factors': self.required_factors,
                'quality': quality,
                'recommendation': recommendation,
                'should_trade': total_score >= self.min_confluence_score and supporting_factors >= self.required_factors,
                'factor_breakdown': factors
            }
            
            logger.info(f"🎯 Confluence Score: {total_score:.2f} ({quality}) - {recommendation}")
            logger.info(f"📊 Supporting factors: {supporting_factors}/{len(factors)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating confluence score: {e}")
            return {
                'confluence_score': 0.0,
                'supporting_factors': 0,
                'quality': 'ERROR',
                'recommendation': 'SKIP',
                'should_trade': False,
                'factor_breakdown': {}
            }

# Test the signal quality filter
if __name__ == "__main__":
    from forex_signal_generator import ForexSignal
    from datetime import datetime
    
    # Initialize filter
    filter_system = SignalQualityFilter()
    
    # Create test signal
    test_signal = ForexSignal(
        pair="EUR/USD",
        signal_type="BUY",
        entry_price=1.0800,
        target_price=1.0850,
        stop_loss=1.0750,
        confidence=0.75,
        pips_target=50,
        pips_risk=50,
        risk_reward_ratio="1:1",
        reason="Test signal",
        timestamp=datetime.now(),
        news_sentiment=0.6,
        technical_score=0.7
    )
    
    # Mock technical data
    technical_data = {
        'score': 0.7,
        'timeframe_breakdown': {
            'H1': 0.6,
            'H4': 0.8,
            'D': 0.7
        }
    }
    
    # Analyze signal quality
    result = filter_system.calculate_confluence_score(test_signal, technical_data, 0.08)
    
    print("🎯 SIGNAL QUALITY ANALYSIS:")
    print("=" * 50)
    print(f"Confluence Score: {result['confluence_score']:.2f}")
    print(f"Quality: {result['quality']}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Should Trade: {result['should_trade']}")
    print(f"Supporting Factors: {result['supporting_factors']}/{len(result['factor_breakdown'])}") 