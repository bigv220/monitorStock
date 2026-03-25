#!/usr/bin/env python3
"""
Stock Portfolio Monitor with Price Action Analysis based on Al Brooks
Main entry point
"""
import argparse
import os
import sys

from src.portfolio import Portfolio
from src.data_fetcher import get_hourly_kline
from src.price_action import analyze_stock
from src.notifier import create_notifier, format_analysis_message


def main():
    parser = argparse.ArgumentParser(description='Stock Portfolio Monitor with Price Action Analysis')
    parser.add_argument('--config', default='config/settings.json', help='Path to config file')
    parser.add_argument('--daily', action='store_true', help='Send as daily summary')
    args = parser.parse_args()
    
    # Check config file exists
    if not os.path.exists(args.config):
        print(f"Error: Config file {args.config} not found")
        print("Please copy config/settings.json.example to config/settings.json and fill in your information")
        sys.exit(1)
    
    try:
        # Load portfolio
        portfolio = Portfolio(args.config)
        print(f"Loaded {len(portfolio.positions)} positions, {len(portfolio.watch_list)} watching stocks")
        
        # Calculate portfolio
        portfolio_data = portfolio.calculate_portfolio()
        
        # Analyze each holding
        analysis_results = {}
        for pos in portfolio_data['positions']:
            code = pos['code']
            df = get_hourly_kline(code, limit=30)
            if df is not None and len(df) > 5:
                analysis = analyze_stock(df)
                analysis_results[code] = analysis
        
        # Analyze watch list
        watch_analysis = {}
        for watch in portfolio.watch_list:
            code = watch.code
            df = get_hourly_kline(code, limit=30)
            if df is not None and len(df) > 5:
                analysis = analyze_stock(df)
                watch_analysis[code] = analysis
        
        # Create notifier
        notification_config = portfolio.get_notification_config()
        notifier = create_notifier(notification_config)
        
        # Format and send
        message = format_analysis_message(
            portfolio_data, 
            analysis_results, 
            watch_analysis if watch_analysis else {},
            is_daily=args.daily
        )
        
        print("\nGenerated message:")
        print(message[:500] + "..." if len(message) > 500 else message)
        
        success = notifier.send(message)
        if success:
            print("\nNotification sent successfully!")
        else:
            print("\nFailed to send notification to some channels")
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
