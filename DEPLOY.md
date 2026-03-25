# 部署文档 - 股票持仓监控器

项目地址：https://github.com/bigv220/monitorStock

服务器信息：
- IP: `101.96.192.55`
- 用户: `root`
- 项目路径: `/root/projects/monitorStock`

## 项目功能

- 监控A股持仓，自动计算盈亏
- 基于 Al Brooks 价格行为学做技术分析（需要K线数据）
- 通过飞书机器人自动推送通知
- 定时任务每小时推送一次，收盘后推送汇总

## 当前配置

### 持仓信息

| 股票名称 | 代码 | 持仓数量 | 成本价 |
|----------|------|----------|--------|
| 中恒电气 | 002364 | 900 | 33.3125 |
| 菲菱科思 | 301191 | 100 | 129.4513 |
| 和远气体 | 002980 | 1400 | 32.0325 |
| 国泰证券ETF | 510230 | 48000 | 1.2024 |

### 飞书配置

- Webhook: `https://open.feishu.cn/open-apis/bot/v2/hook/175b14ce-cd88-4973-bb52-bb152699e03f`
- 关键词验证：`股票`（已配置）

### 定时任务

```bash
crontab -l
```

输出：
```
# 每个交易日 10:00 - 15:00 每小时整点推送
0 10-15 * * 1-5 cd /root/projects/monitorStock && /usr/bin/python3 main.py >> /var/log/stock_monitor.log 2>&1
# 每个交易日 15:30 推送收盘汇总
30 15 * * 1-5 cd /root/projects/monitorStock && /usr/bin/python3 main.py --daily >> /var/log/stock_monitor.log 2>&1
```

## 如何修改配置

### 修改持仓/成本

```bash
nano /root/projects/monitorStock/config/settings.json
```
修改后按 `Ctrl+O` 回车保存，`Ctrl+X` 退出。

### 测试运行

```bash
cd /root/projects/monitorStock
python3 main.py
```
运行成功后飞书会收到通知。

### 查看日志

```bash
tail -f /var/log/stock_monitor.log
```

## 数据获取说明

- 当前价格使用 **腾讯财经API** 获取，稳定，频率限制宽松
- 历史K线由于火山引擎IP被限流，暂时无法获取，只做价格盈亏监控
- 如果需要技术分析功能，可以：
  1. 更换服务器公网IP
  2. 配置代理

## 项目结构

```
/root/projects/monitorStock/
├── main.py                 # 主入口
├── requirements.txt        # Python依赖
├── config/
│   └── settings.json       # 当前配置（持仓+飞书）
└── src/
    ├── data_fetcher.py     # 数据获取（腾讯API）
    ├── portfolio.py        # 持仓盈亏计算
    ├── price_action.py     # 价格行为分析（需要K线）
    └── notifier.py         # 飞书通知推送
```

## 重新部署步骤

如果需要重新部署：

```bash
# 安装依赖
apt update && apt install python3 python3-pip git -y

# 克隆项目
git clone https://github.com/bigv220/monitorStock.git
cd monitorStock

# 安装依赖
pip3 install -r requirements.txt --break-system-packages

# 配置 settings.json 后测试
python3 main.py

# 设置定时任务
crontab -e
# 添加上面的两条定时任务
```

## 最新持仓盈亏（2026-03-26收盘）

| 股票 | 当前价 | 盈亏 | 盈亏比例 |
|------|--------|------|---------|
| 中恒电气 | 29.90 | 🔴 -3,071.25 | -10.24% |
| 菲菱科思 | 130.99 | 🟢 +153.87 | +1.19% |
| 和远气体 | 40.51 | 🟢 +11,868.50 | +26.47% |
| 国泰证券ETF | 1.30 | 🟢 +4,588.80 | +7.95% |

**总市值: 159,027.00**  
**总盈亏: 🟢 +13,539.92 (+9.31%)**

---

*最后更新: 2026-03-26*
