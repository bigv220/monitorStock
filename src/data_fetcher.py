"""
Data Fetcher Module
Get stock data from Tencent Finance API more accurate
"""
import requests
from typing import Optional
import pandas as pd
import akshare as ak
from typing import Dict


def format_stock_code(code: str) -> str:
    """Format for Tencent API"""
    if code.startswith('6') or code.startswith('5'):
        return f"sh{code}"
    elif code.startswith('0') or code.startswith('3'):
        return f"sz{code}"
    return code


def get_current_price(code: str) -> Optional[float]:
    """Get current stock price from Tencent API"""
    try:
        t_code = format_stock_code(code)
        url = f"http://qt.gtimg.cn/q={t_code}"
        headers = {'Referer': 'http://stock.finance.qq.com/'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200 and response.text:
            # parse response: vername~code~...~current_price~...
            data = response.text.split('~')
            if len(data) >= 4:
                price = float(data[3])
                return price
        return None
    except Exception as e:
        print(f"Error getting current price for {code}: {e}")
        return None


def get_daily_kline(code: str, limit: int = 30) -> Optional[pd.DataFrame]:
    """Get daily K-line data"""
    try:
        df = ak.stock_zh_a_daily(symbol=format_stock_code(code), adjust="qfq")
        df = df[["open", "high", "low", "close"]]
        df = df.tail(limit)
        return df if len(df) > 0 else None
    except Exception as e:
        print(f"Error getting daily K-line for {code}: {e}")
        return None


def get_hourly_kline(code: str, limit: int = 30) -> Optional[pd.DataFrame]:
    """Get hourly K-line using AkShare - 60min data from stock_zh_a_hist_min_em"""
    try:
        df = ak.stock_zh_a_hist_min_em(symbol=code, period="60", adjust="qfq")
        df = df[["开盘", "最高", "最低", "收盘"]]
        df = df.rename(columns={
            "开盘": "open",
            "最高": "high", 
            "最低": "low",
            "收盘": "close"
        })
        df = df.tail(limit)
        return df if len(df) > 0 else None
    except Exception as e:
        print(f"Error getting hourly K-line from min_em for {code}: {e}")
        try:
            # Fallback to 60min from stock_zh_a_minute
            df = ak.stock_zh_a_minute(symbol=format_stock_code(code), period="60min")
            df = df[["open", "high", "low", "close"]]
            df = df.tail(limit)
            return df if len(df) > 0 else None
        except Exception as e2:
            print(f"Error getting hourly K-line from minute fallback: {e2}")
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
