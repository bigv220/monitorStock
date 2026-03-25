# 股票持仓监控 + Al Brooks价格行为分析

这是一个针对平安证券持仓（或任何A股持仓）的自动监控应用，每小时小时级别分析，并通过钉钉/企业微信推送交易建议。

## 功能特点

- ✅ **自动获取行情**: 使用 AkShare 免费获取 A 股实时价格和小时K线
- ✅ **持仓盈亏计算**: 自动计算你每只股票和总盈亏
- ✅ **价格行为分析**: 基于 Al Brooks 价格行为学进行技术分析
- ✅ **交易建议**: 根据分析结果给出 `买入/卖出/持有` 明确建议
- ✅ **通知推送**: 支持钉钉机器人和企业微信机器人推送
- ✅ **关注列表**: 还可以监控你关注的股票

## Al Brooks 价格行为分析逻辑

1. **趋势识别**: 通过连续高低点判断是上涨/下跌/盘整趋势
2. **支撑阻力**: 找到最近的支撑位和阻力位
3. **K线形态分析**: 识别大实体、长影线、吞噬形态等价格信号
4. **位置分析**: 根据价格在支撑阻力区间的位置给出建议
5. **顺势而为**: 优先跟随趋势，结合K线反转信号判断入场出场点

## 项目结构

```
monitorStock/
├── main.py                 # 主程序入口
├── requirements.txt        # Python依赖
├── README.md               # 本文件
├── config/
│   └── settings.json       # 你的配置（持仓+通知设置）
│   └── settings.json.example  # 配置模板
└── src/
    ├── __init__.py
    ├── data_fetcher.py     # 数据获取模块
    ├── portfolio.py        # 持仓管理模块
    ├── price_action.py     # 价格行为分析模块
    └── notifier.py         # 通知推送模块
```

## 本地快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置你的持仓和通知

```bash
cp config/settings.json.example config/settings.json
# 编辑 config/settings.json，填入你的持仓股票和通知webhook
```

配置文件说明：
```json
{
  "stocks": [
    {
      "code": "600000",       // 股票代码
      "name": "浦发银行",      // 股票名称
      "quantity": 1000,       // 持仓数量
      "cost_price": 10.5,     // 你的成本价
      "is_holding": true      // 是否持有
    }
  ],
  "watch_list": [            // 关注列表
    {
      "code": "601318",
      "name": "中国平安"
    }
  ],
  "notifications": {
    "dingtalk": {            // 钉钉机器人设置
      "enabled": true,
      "webhook": "https://oapi.dingtalk.com/robot/send?access_token=xxx"
    },
    "wechat_work": {        // 企业微信机器人设置
      "enabled": false,
      "webhook": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"
    }
  }
}
```

### 3. 运行测试

```bash
python main.py
# 如果是每日汇总
python main.py --daily
```

## 云服务器部署

你说要部署到云服务器，下面是 crontab 定时任务配置示例：

### 1. 开盘时间每小时运行一次（A股 9:30-15:00）

编辑 crontab:
```bash
crontab -e
```

添加以下内容（每小时开盘运行一次）：
```
# 周一到周五，10点到15点，每小时运行一次
0 10-15 * * 1-5 cd /path/to/monitorStock && /usr/bin/python3 main.py >> /tmp/stock_monitor.log 2>&1

# 每日收盘后15:30发送汇总
30 15 * * 1-5 cd /path/to/monitorStock && /usr/bin/python3 main.py --daily >> /tmp/stock_monitor.log 2>&1
```

这样就会在交易时段每小时推送一次分析，收盘后发送汇总报告。

### 如何创建钉钉机器人

1. 在钉钉群聊中，点击... → 群机器人 → 添加机器人
2. 选择 "自定义" 机器人，关键字填写 "股票"
3. 获取到 webhook 地址，填入配置文件即可

## 关于平安证券

由于平安证券没有开放的公开API可以直接获取你的持仓，所以本项目：
- 需要你手动在配置文件中输入你的持仓信息
- 通过免费公开API获取市场价格进行分析
- 如果后续平安证券开放了API，可以扩展自动同步持仓功能

## 示例通知

```
# 📊 股票持仓监控

⏰ 更新时间: 2024-03-25 14:30

## 📈 持仓汇总
总市值: **15800.00**
总盈亏: 🟢 **+1250.00 (+8.50%)**

## 我的持仓

### 平安银行 (000001)
价格: **15.80**  盈亏: 🟢 +250.00 (+3.20%)
建议: **⏸️ 持有**
趋势: Uptrend - Higher highs and higher lows
支撑: 15.20  阻力: 16.10
波动率: 1.25%
- Trend is up (higher highs and higher lows)
- Bullish trend, hold longs
```

## License

MIT
