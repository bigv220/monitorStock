"""
Data Fetcher Module
Get stock data using AkShare
"""
import akshare as ak
import pandas as pd
from typing import Tuple, Optional, Dict


def format_stock_code(code: str) -> str:
    """Format stock code for AkShare"""
    if code.startswith('6') or code.startswith('5'):
        return f"sh{code}"
    elif code.startswith('0') or code.startswith('3'):
        return f"sz{code}"
    elif code.startswith('8') or code.startswith('4'):
        return f"bj{code}"
    return code


def get_current_price(code: str) -> Optional[float]:
    """Get current stock price"""
    try:
        formatted_code = format_stock_code(code)
        price = ak.stock_zh_a_spot()
        price_data = price[price['代码'] == formatted_code]
        if not price_data.empty:
            return float(price_data['最新价'].values[0])
        return None
    except Exception as e:
        print(f"Error getting current price for {code}: {e}")
        return None


def get_hourly_kline(code: str, limit: int = 30) -> Optional[pd.DataFrame]:
    """Get hourly K-line data for analysis"""
    try:
        formatted_code = format_stock_code(code)
        df = ak.stock_zh_a_hist_min_em(symbol=formatted_code, period="60")
        
        df = df[['时间', '开盘', '收盘', '最高', '最低', '成交量']]
        df.columns = ['time', 'open', 'close', 'high', 'low', 'volume']
        
        for col in ['open', 'close', 'high', 'low', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df = df.dropna()
        df = df.tail(limit)
        
        return df
    except Exception as e:
        print(f"Error getting hourly K-line for {code}: {e}")
        return None


def get_stock_info(code: str) -> Dict:
    """Get basic stock information"""
    price = get_current_price(code)
    df = get_hourly_kline(code)
    
    return {
        "code": code,
        "current_price": price,
        "hourly_kline": df
    }
