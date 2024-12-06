import pandas as pd
import backtrader as bt
from indicators.vwap import VWAP

class VWAPEMA200Strategy(bt.Strategy):
    params = (
        ('vwap_period', 14),  # VWAP period
        ('ema_period', 200),  # EMA200 period
        ('take_profit', 0.008),  # Take profit threshold (0.6%)
        ('stop_loss', 0.006),  # Stop loss threshold (0.4%)
    )

    def __init__(self, cerebro):
        # Calculate VWAP (custom implementation)
        self.vwap = VWAP(self.data, period=self.params.vwap_period)
        # Calculate EMA200
        self.ema200 = bt.indicators.ExponentialMovingAverage(self.data.close, period=self.params.ema_period)
        self.buy_price = None
        self.buy_date = None
        self.trades = []  # To store trade records
        self.cerebro = cerebro  # Pass the cerebro object

    def notify_order(self, order):
        if order.status == order.Completed:
            if order.isbuy():
                print(f"Buy successful, price: {order.executed.price}, size: {order.executed.size}")
            elif order.issell():
                print(f"Sell successful, price: {order.executed.price}, size: {order.executed.size}")
        elif order.status == order.Canceled:
            print("Order canceled")
        elif order.status == order.Margin:
            print("Order not executed due to insufficient margin")
        elif order.status == order.Rejected:
            print("Order rejected")

    def next(self):
        if not self.position:
            # Buy if the current price crosses above VWAP and is above EMA200
            if self.data.close[0] > self.vwap[0] and self.data.close[0] > self.ema200[0]:
                self.buy_price = self.data.close[0]
                self.buy_date = self.data.datetime.date(0)
                size_to_buy = self.cerebro.broker.getvalue() / self.data.close[0]  # Use all cash to buy
                size_to_buy = size_to_buy - size_to_buy * 0.001
                if size_to_buy > 0:
                    self.buy(size=size_to_buy)  # Buy
                print(f"Buy size: {size_to_buy} BTC")
        else:
            # Calculate the price change relative to the buy price
            price_change = (self.data.close[0] - self.position.price) / self.position.price

            # Take profit if the price increase exceeds 0.6%
            if price_change >= self.params.take_profit:
                self.sell(size=self.position.size)  # Sell the holding size
                self.trades.append(('buy', self.buy_date, self.buy_price, 'sell', self.data.datetime.date(0),
                                    self.data.close[0], 'take profit'))

            # Stop loss if the price decrease exceeds 0.4%
            elif price_change <= -self.params.stop_loss:
                self.sell(size=self.position.size)
                self.trades.append(('buy', self.buy_date, self.buy_price, 'sell', self.data.datetime.date(0),
                                    self.data.close[0], 'stop loss'))

    def stop(self):
        profitable_trades = sum(1 for trade in self.trades if trade[6] == 'take profit')
        total_trades = len(self.trades)
        win_rate = (profitable_trades / total_trades) if total_trades > 0 else 0

        # Calculate the return rate
        total_profit = sum((trade[5] - trade[2]) / trade[2] for trade in self.trades)
        return_rate = total_profit

        # Calculate the number of take profit and stop loss trades
        take_profit_count = sum(1 for trade in self.trades if trade[6] == 'take profit')
        stop_loss_count = sum(1 for trade in self.trades if trade[6] == 'stop loss')

        print(f"Strategy win rate: {win_rate * 100:.2f}%")
        print(f"Total return rate: {return_rate * 100:.2f}%")
        print(f"Take profit count: {take_profit_count}")
        print(f"Stop loss count: {stop_loss_count}")

        # Generate trade table
        trade_records = []
        for trade in self.trades:
            buy_date = trade[1]
            buy_price = trade[2]
            sell_date = trade[4]
            sell_price = trade[5]
            profit = (sell_price - buy_price) / buy_price
            close_reason = trade[6]
            trade_records.append([buy_price, buy_date, sell_price, sell_date, profit, close_reason])

        trade_df = pd.DataFrame(trade_records, columns=['Entry Price', 'Entry Date', 'Exit Price', 'Exit Date', 'Profit', 'Exit Reason'])
        trade_df.to_csv('trade_records.csv', index=False)