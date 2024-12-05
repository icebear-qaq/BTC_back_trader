import pandas as pd
import backtrader as bt
from indicators.vwap import VWAP

class VWAPEMA200Strategy(bt.Strategy):
    params = (
        ('vwap_period', 14),  # VWAP周期
        ('ema_period', 200),  # EMA200周期
        ('take_profit', 0.04),  # 止盈阈值 (0.6%)
        ('stop_loss', 0.008),  # 止损阈值 (0.4%)
    )

    def __init__(self, cerebro):
        # 计算VWAP (自定义实现)
        self.vwap = VWAP(self.data, period=self.params.vwap_period)
        # 计算EMA200
        self.ema200 = bt.indicators.ExponentialMovingAverage(self.data.close, period=self.params.ema_period)
        self.buy_price = None
        self.buy_date = None
        self.trades = []  # 用于保存交易记录
        self.cerebro = cerebro  # 传递 cerebro 对象

    def notify_order(self, order):
        if order.status == order.Completed:
            if order.isbuy():
                print(f"买入成功，价格: {order.executed.price}, 数量: {order.executed.size}")
            elif order.issell():
                print(f"卖出成功，价格: {order.executed.price}, 数量: {order.executed.size}")
        elif order.status == order.Canceled:
            print("订单被取消")
        elif order.status == order.Margin:
            print("订单由于保证金不足未能执行")
        elif order.status == order.Rejected:
            print("订单被拒绝")

    def next(self):
        if not self.position:
            # 如果当前价格穿越VWAP，并且在EMA200之上，则买入
            if self.data.close[0] > self.vwap[0] and self.data.close[0] > self.ema200[0]:
                self.buy_price = self.data.close[0]
                self.buy_date = self.data.datetime.date(0)
                size_to_buy = self.cerebro.broker.getvalue() / self.data.close[0]  # 用所有现金买入
                size_to_buy = size_to_buy - size_to_buy * 0.001
                if size_to_buy > 0:
                    self.buy(size=size_to_buy)  # 买入
                print(f"买入数量: {size_to_buy} BTC")
        else:
            # 判断当前价格相对于买入价格的涨跌幅
            price_change = (self.data.close[0] - self.position.price) / self.position.price

            # 如果价格涨幅超过0.6%则止盈
            if price_change >= self.params.take_profit:
                self.sell(size=self.position.size)  # 卖出持有数量
                self.trades.append(('buy', self.buy_date, self.buy_price, 'sell', self.data.datetime.date(0),
                                    self.data.close[0], 'take profit'))

            # 如果价格跌幅超过0.4%则止损
            elif price_change <= -self.params.stop_loss:
                self.sell(size=self.position.size)
                self.trades.append(('buy', self.buy_date, self.buy_price, 'sell', self.data.datetime.date(0),
                                    self.data.close[0], 'stop loss'))

    def stop(self):
        # 计算胜率
        profitable_trades = sum(1 for trade in self.trades if trade[6] == 'take profit')
        total_trades = len(self.trades)
        win_rate = (profitable_trades / total_trades) if total_trades > 0 else 0

        # 计算回报率
        total_profit = sum((trade[5] - trade[2]) / trade[2] for trade in self.trades)
        return_rate = total_profit

        print(f"策略胜率: {win_rate * 100:.2f}%")
        print(f"总回报率: {return_rate * 100:.2f}%")

        # 生成交易表格
        trade_records = []
        for trade in self.trades:
            buy_date = trade[1]
            buy_price = trade[2]
            sell_date = trade[4]
            sell_price = trade[5]
            profit = (sell_price - buy_price) / buy_price
            close_reason = trade[6]
            trade_records.append([buy_price, buy_date, sell_price, sell_date, profit, close_reason])

        trade_df = pd.DataFrame(trade_records, columns=['开仓点', '开仓时间', '平仓点', '平仓时间', '收益', '平仓原因'])
        trade_df.to_csv('交易记录.csv', index=False)