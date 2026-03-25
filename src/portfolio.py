"""
Portfolio Manager Module
Read configuration and calculate portfolio performance
"""
import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass

from src.data_fetcher import get_current_price


@dataclass
class StockPosition:
    code: str
    name: str
    quantity: int
    cost_price: float
    is_holding: bool
    
    def calculate_pnl(self, current_price: float) -> Dict:
        """Calculate profit and loss"""
        cost = self.quantity * self.cost_price
        market_value = self.quantity * current_price
        pnl = market_value - cost
        pnl_percent = (current_price - self.cost_price) / self.cost_price * 100
        return {
            "cost": cost,
            "market_value": market_value,
            "pnl": pnl,
            "pnl_percent": pnl_percent
        }


@dataclass
class WatchStock:
    code: str
    name: str


class Portfolio:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.positions: List[StockPosition] = []
        self.watch_list: List[WatchStock] = []
        self.notifications: Dict = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from JSON file"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found at {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        self.positions = []
        for stock in config.get("stocks", []):
            if stock.get("is_holding", True):
                pos = StockPosition(
                    code=stock["code"],
                    name=stock["name"],
                    quantity=stock.get("quantity", 0),
                    cost_price=stock.get("cost_price", 0.0),
                    is_holding=stock.get("is_holding", True)
                )
                self.positions.append(pos)
        
        self.watch_list = []
        for stock in config.get("watch_list", []):
            ws = WatchStock(
                code=stock["code"],
                name=stock["name"]
            )
            self.watch_list.append(ws)
        
        self.notifications = config.get("notifications", {})
    
    def get_all_holding_codes(self) -> List[str]:
        """Get all holding stock codes"""
        return [pos.code for pos in self.positions]
    
    def get_all_watch_codes(self) -> List[str]:
        """Get all watch list codes"""
        return [ws.code for ws in self.watch_list]
    
    def calculate_portfolio(self) -> Dict:
        """Calculate entire portfolio performance"""
        total_cost = 0.0
        total_market_value = 0.0
        total_pnl = 0.0
        position_details = []
        
        for pos in self.positions:
            current_price = get_current_price(pos.code)
            if current_price is None:
                continue
                
            pnl_data = pos.calculate_pnl(current_price)
            total_cost += pnl_data["cost"]
            total_market_value += pnl_data["market_value"]
            total_pnl += pnl_data["pnl"]
            
            detail = {
                "code": pos.code,
                "name": pos.name,
                "quantity": pos.quantity,
                "cost_price": pos.cost_price,
                "current_price": current_price,
                "cost": pnl_data["cost"],
                "market_value": pnl_data["market_value"],
                "pnl": pnl_data["pnl"],
                "pnl_percent": pnl_data["pnl_percent"]
            }
            position_details.append(detail)
        
        total_pnl_percent = (total_pnl / total_cost * 100) if total_cost > 0 else 0
        
        return {
            "total_cost": total_cost,
            "total_market_value": total_market_value,
            "total_pnl": total_pnl,
            "total_pnl_percent": total_pnl_percent,
            "positions": position_details,
            "watch_list": [{"code": ws.code, "name": ws.name} for ws in self.watch_list]
        }
    
    def get_notification_config(self):
        """Get notification configuration"""
        return self.notifications
