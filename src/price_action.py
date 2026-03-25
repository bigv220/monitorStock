"""
Price Action Analysis based on Al Brooks methodology
Hourly timeframe analysis
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional


class PriceActionAnalyzer:
    """Al Brooks Price Action Analyzer"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.current_price = df['close'].iloc[-1]
        if len(df) < 10:
            print("Warning: Not enough data for reliable analysis")
    
    def find_swing_points(self) -> Tuple[List[int], List[int]]:
        """Find swing highs and lows"""
        highs = []
        lows = []
        
        for i in range(2, len(self.df) - 2):
            if self.df['high'].iloc[i] > self.df['high'].iloc[i-1] and \
               self.df['high'].iloc[i] > self.df['high'].iloc[i-2] and \
               self.df['high'].iloc[i] > self.df['high'].iloc[i+1] and \
               self.df['high'].iloc[i] > self.df['high'].iloc[i+2]:
                highs.append(i)
            
            if self.df['low'].iloc[i] < self.df['low'].iloc[i-1] and \
               self.df['low'].iloc[i] < self.df['low'].iloc[i-2] and \
               self.df['low'].iloc[i] < self.df['low'].iloc[i+1] and \
               self.df['low'].iloc[i] < self.df['low'].iloc[i+2]:
                lows.append(i)
        
        return highs, lows
    
    def identify_trend(self) -> Dict:
        """Identify trend based on higher highs/lows pattern"""
        highs, lows = self.find_swing_points()
        
        if len(highs) < 2 or len(lows) < 2:
            return {"trend": "sideways", "description": "Insufficient swing points, trading sideways"}
        
        recent_highs = [self.df['high'].iloc[h] for h in highs[-3:]]
        recent_lows = [self.df['low'].iloc[l] for l in lows[-3:]]
        
        higher_highs = all(recent_highs[i] > recent_highs[i-1] for i in range(1, len(recent_highs)))
        higher_lows = all(recent_lows[i] > recent_lows[i-1] for i in range(1, len(recent_lows)))
        
        lower_highs = all(recent_highs[i] < recent_highs[i-1] for i in range(1, len(recent_highs)))
        lower_lows = all(recent_lows[i] < recent_lows[i-1] for i in range(1, len(recent_lows)))
        
        if higher_highs and higher_lows:
            return {"trend": "bullish", "description": "Uptrend - Higher highs and higher lows"}
        elif lower_highs and lower_lows:
            return {"trend": "bearish", "description": "Downtrend - Lower highs and lower lows"}
        else:
            return {"trend": "sideways", "description": "Range bound / Consolidation"}
    
    def get_support_resistance(self) -> Dict:
        """Get nearest support and resistance levels"""
        highs, lows = self.find_swing_points()
        
        if not highs or not lows:
            high_vals = self.df['high'].tail(10).values
            low_vals = self.df['low'].tail(10).values
        else:
            high_vals = [self.df['high'].iloc[h] for h in highs]
            low_vals = [self.df['low'].iloc[l] for l in lows]
        
        resistance_levels = sorted([h for h in high_vals if h > self.current_price])
        support_levels = sorted([l for l in low_vals if l < self.current_price], reverse=True)
        
        nearest_resistance = resistance_levels[0] if resistance_levels else self.df['high'].max()
        nearest_support = support_levels[0] if support_levels else self.df['low'].min()
        
        return {
            "support": nearest_support,
            "resistance": nearest_resistance,
            "distance_to_support_pct": (self.current_price - nearest_support) / self.current_price * 100,
            "distance_to_resistance_pct": (nearest_resistance - self.current_price) / self.current_price * 100
        }
    
    def analyze_recent_candles(self) -> Dict:
        """Analyze recent candle patterns"""
        last_3 = self.df.tail(3)
        current = self.df.iloc[-1]
        prev = self.df.iloc[-2]
        
        body_size = abs(current['close'] - current['open'])
        range_size = current['high'] - current['low']
        body_ratio = body_size / range_size if range_size > 0 else 0
        
        upper_wick = current['high'] - max(current['open'], current['close'])
        lower_wick = min(current['open'], current['close']) - current['low']
        
        is_bullish = current['close'] > current['open']
        is_bearish = current['close'] < current['open']
        
        has_long_upper_wick = upper_wick > 2 * body_size
        has_long_lower_wick = lower_wick > 2 * body_size
        
        # Check for engulfing pattern
        bullish_engulfing = (is_bullish and 
                             prev['close'] < prev['open'] and 
                             current['open'] < prev['low'] and 
                             current['close'] > prev['high'])
        
        bearish_engulfing = (is_bearish and 
                             prev['close'] > prev['open'] and 
                             current['open'] > prev['high'] and 
                             current['close'] < prev['low'])
        
        return {
            "is_bullish": is_bullish,
            "is_bearish": is_bearish,
            "body_ratio": body_ratio,
            "has_long_upper_wick": has_long_upper_wick,
            "has_long_lower_wick": has_long_lower_wick,
            "bullish_engulfing": bullish_engulfing,
            "bearish_engulfing": bearish_engulfing,
            "strong_bullish": is_bullish and body_ratio > 0.7,
            "strong_bearish": is_bearish and body_ratio > 0.7
        }
    
    def calculate_volatility(self) -> float:
        """Calculate recent average true range (ATR)"""
        df = self.df.copy()
        df['tr'] = np.maximum(
            df['high'] - df['low'],
            np.maximum(
                abs(df['high'] - df['close'].shift(1)),
                abs(df['low'] - df['close'].shift(1))
            )
        )
        atr = df['tr'].tail(10).mean()
        atr_pct = atr / self.current_price * 100
        return atr_pct
    
    def get_recommendation(self, trend: str, sr: Dict, candle: Dict) -> Dict:
        """Get trading recommendation based on Al Brooks principles"""
        
        recommendation = "hold"
        reasoning = []
        
        current_price = self.current_price
        
        # Trend following is primary according to Al Brooks
        if trend == "bullish":
            reasoning.append("Trend is up (higher highs and higher lows)")
            if current_price > (sr['support'] + sr['resistance']) / 2:
                if candle['is_bullish'] and not candle['has_long_upper_wick']:
                    recommendation = "buy"
                    reasoning.append("Price above midpoint with bullish candle - good for long")
                elif candle['bearish_engulfing'] and current_price > sr['resistance']:
                    recommendation = "sell"
                    reasoning.append("Bearish engulfing at resistance - potential reversal")
                else:
                    recommendation = "hold"
                    reasoning.append("Bullish trend, hold longs")
            
            elif current_price < sr['support'] * 1.01:
                if candle['has_long_lower_wick']:
                    recommendation = "buy"
                    reasoning.append("Testing support with bullish rejection - good entry")
                else:
                    recommendation = "sell"
                    reasoning.append("Breakdown below support in uptrend - exit")
        
        elif trend == "bearish":
            reasoning.append("Trend is down (lower highs and lower lows)")
            if current_price < (sr['support'] + sr['resistance']) / 2:
                if candle['is_bearish'] and not candle['has_long_lower_wick']:
                    recommendation = "sell"
                    reasoning.append("Price below midpoint with bearish candle - good for short")
                elif candle['bullish_engulfing'] and current_price < sr['support']:
                    recommendation = "buy"
                    reasoning.append("Bullish engulfing at support - potential reversal")
                else:
                    recommendation = "hold"
                    reasoning.append("Bearish trend, hold shorts")
            
            elif current_price > sr['resistance'] * 0.99:
                if candle['has_long_upper_wick']:
                    recommendation = "sell"
                    reasoning.append("Testing resistance with bearish rejection - good entry")
                else:
                    recommendation = "buy" if candle['strong_bullish'] else "hold"
                    if recommendation == "buy":
                        reasoning.append("Breakout above resistance - long")
        
        else:  # sideways
            reasoning.append("Trading in range/consolidation")
            dist_to_s = sr['distance_to_support_pct']
            dist_to_r = sr['distance_to_resistance_pct']
            
            if dist_to_s < 1.5:
                if candle['has_long_lower_wick'] or candle['bullish_engulfing']:
                    recommendation = "buy"
                    reasoning.append("At support with bullish reversal pattern")
                else:
                    recommendation = "sell" if candle['is_bearish'] else "hold"
                    if recommendation == "sell":
                        reasoning.append("At support with bearish breakout - breakdown likely")
            
            elif dist_to_r < 1.5:
                if candle['has_long_upper_wick'] or candle['bearish_engulfing']:
                    recommendation = "sell"
                    reasoning.append("At resistance with bearish reversal pattern")
                else:
                    recommendation = "buy" if candle['is_bullish'] else "hold"
                    if recommendation == "buy":
                        reasoning.append("Breakout above resistance - bullish")
            
            else:
                recommendation = "hold"
                reasoning.append("In middle of range, wait for clearer pattern")
        
        recommendation_map = {
            "buy": "📈 买入",
            "sell": "📉 卖出", 
            "hold": "⏸️ 持有"
        }
        
        return {
            "recommendation": recommendation,
            "recommendation_text": recommendation_map[recommendation],
            "reasoning": reasoning
        }
    
    def analyze(self) -> Dict:
        """Complete analysis"""
        trend_data = self.identify_trend()
        sr_data = self.get_support_resistance()
        candle_data = self.analyze_recent_candles()
        volatility = self.calculate_volatility()
        recommendation = self.get_recommendation(
            trend_data['trend'], 
            sr_data, 
            candle_data
        )
        
        return {
            "current_price": self.current_price,
            "trend": trend_data,
            "support_resistance": sr_data,
            "recent_candles": candle_data,
            "volatility_pct": volatility,
            "recommendation": recommendation
        }


def analyze_stock(df: pd.DataFrame) -> Dict:
    """Helper function to analyze a stock"""
    analyzer = PriceActionAnalyzer(df)
    return analyzer.analyze()
