"""
Notifier Module
Support DingTalk, WeChat Work and FeiShu robot notification
"""
import requests
import json
from typing import Dict, List
from datetime import datetime


class BaseNotifier:
    """Base class for notifiers"""
    def send(self, content: str) -> bool:
        raise NotImplementedError


class DingTalkNotifier(BaseNotifier):
    """DingTalk robot notifier"""
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send(self, content: str) -> bool:
        """Send markdown message to DingTalk"""
        try:
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": content
                }
            }
            response = requests.post(self.webhook_url, json=data)
            result = response.json()
            if result.get('errcode', 0) == 0:
                return True
            else:
                print(f"DingTalk send error: {result}")
                return False
        except Exception as e:
            print(f"Error sending to DingTalk: {e}")
            return False


class WeChatWorkNotifier(BaseNotifier):
    """WeChat Work robot notifier"""
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send(self, content: str) -> bool:
        """Send markdown message to WeChat Work"""
        try:
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": content
                }
            }
            response = requests.post(self.webhook_url, json=data)
            result = response.json()
            if result.get('errcode', 0) == 0:
                return True
            else:
                print(f"WeChat Work send error: {result}")
                return False
        except Exception as e:
            print(f"Error sending to WeChat Work: {e}")
            return False


class FeiShuNotifier(BaseNotifier):
    """FeiShu (Lark) robot notifier - support both custom bot and flow webhook"""
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send(self, content: str) -> bool:
        """Send markdown message to FeiShu"""
        try:
            if "flow/api/trigger-webhook" in self.webhook_url:
                # For flow webhook, send as simple json
                data = {
                    "text": content
                }
            else:
                # For custom bot
                data = {
                    "msg_type": "interactive",
                    "card": {
                        "header": {
                            "title": {
                                "content": "股票持仓监控",
                                "tag": "plain_text"
                            }
                        },
                        "elements": [
                            {
                                "tag": "markdown",
                                "content": content
                            }
                        ]
                    }
                }
            response = requests.post(self.webhook_url, json=data)
            result = response.json()
            # Flow webhook returns 0 for success
            if result.get('code', 0) == 0 or result.get('StatusCode', 0) == 0:
                return True
            else:
                print(f"FeiShu send error: {result}")
                return False
        except Exception as e:
            print(f"Error sending to FeiShu: {e}")
            return False


class CompositeNotifier:
    """Send to multiple notifiers"""
    def __init__(self, notifiers: List[BaseNotifier]):
        self.notifiers = notifiers
    
    def send(self, content: str) -> bool:
        success = True
        for notifier in self.notifiers:
            if not notifier.send(content):
                success = False
        return success


def format_analysis_message(portfolio_data: Dict, analysis_results: Dict, 
                           watch_analysis: Dict = None, is_daily: bool = False) -> str:
    """Format analysis result as markdown message"""
    if watch_analysis is None:
        watch_analysis = {}
    now = datetime.now()
    title = "📊 股票持仓监控" + (" (每日汇总)" if is_daily else "")
    message = f"# {title}\n\n"
    message += f"⏰ 更新时间: {now.strftime('%Y-%m-%d %H:%M')}\n\n"
    
    # Portfolio summary
    total_pnl = portfolio_data['total_pnl']
    total_pnl_percent = portfolio_data['total_pnl_percent']
    pnl_emoji = "🟢" if total_pnl >= 0 else "🔴"
    message += f"## 📈 持仓汇总\n"
    message += f"总市值: **{portfolio_data['total_market_value']:.2f}**\n"
    message += f"总盈亏: {pnl_emoji} **{total_pnl:+.2f} ({total_pnl_percent:+.2f}%)**\n\n"
    
    # Positions detail
    message += f"## 我的持仓\n"
    for pos in portfolio_data['positions']:
        analysis = analysis_results.get(pos['code'], None) if analysis_results else None
        pnl_emoji = "🟢" if pos['pnl'] >= 0 else "🔴"
        message += f"\n### {pos['name']} ({pos['code']})\n"
        message += f"价格: **{pos['current_price']:.2f}**  盈亏: {pnl_emoji} {pos['pnl']:.2f} ({pos['pnl_percent']:+.2f}%)\n"
        
        if analysis:
            rec_text = analysis['recommendation']['recommendation_text']
            message += f"建议: **{rec_text}**\n"
            message += f"趋势: {analysis['trend']['description']}\n"
            message += f"支撑: {analysis['support_resistance']['support']:.2f}  "
            message += f"阻力: {analysis['support_resistance']['resistance']:.2f}\n"
            message += f"波动率: {analysis['volatility_pct']:.2f}%\n"
            for r in analysis['recommendation']['reasoning']:
                message += f"- {r}\n"
    
    # Watch list
    if watch_analysis and len(watch_analysis) > 0:
        message += f"\n## 关注列表\n"
        for code, analysis in watch_analysis.items():
            name = next((w['name'] for w in portfolio_data['watch_list'] if w['code'] == code), code)
            rec_text = analysis['recommendation']['recommendation_text']
            message += f"\n**{name} ({code})** - {rec_text}\n"
            message += f"价格: {analysis['current_price']:.2f}  |  {analysis['trend']['description']}\n"
            message += f"{analysis['recommendation']['reasoning'][0] if analysis['recommendation']['reasoning'] else ''}\n"
    
    message += f"\n\n---\n*基于 Al Brooks 价格行为学*\n"
    return message


def create_notifier(config: Dict) -> CompositeNotifier:
    """Create notifier from config"""
    notifiers = []
    
    dingtalk_config = config.get("dingtalk", {})
    if dingtalk_config.get("enabled", False) and dingtalk_config.get("webhook"):
        notifiers.append(DingTalkNotifier(dingtalk_config["webhook"]))
    
    wechat_config = config.get("wechat_work", {})
    if wechat_config.get("enabled", False) and wechat_config.get("webhook"):
        notifiers.append(WeChatWorkNotifier(wechat_config["webhook"]))
    
    feishu_config = config.get("feishu", {})
    if feishu_config.get("enabled", False) and feishu_config.get("webhook"):
        notifiers.append(FeiShuNotifier(feishu_config["webhook"]))
    
    return CompositeNotifier(notifiers)
