import backtrader as bt
from data_loader.data_loader import load_data
from strategies.vwap_ema200_strategy import VWAPEMA200Strategy

# 定义文件路径
data_dir = 'test'

# 加载数据
combined_df = load_data(data_dir)

# 创建一个Backtrader的数据feed
class PandasData(bt.feeds.PandasData):
    # 设置DataFrame的列名映射
    lines = ('amount',)
    params = (
        ('datetime', None),  # datetime列会使用索引
        ('open', 'open'),
        ('high', 'high'),
        ('low', 'low'),
        ('close', 'close'),
        ('volume', 'volume'),
        ('amount', 'amount'),
        ('open_time', None),
        ('close_time', None),
    )

def run_cerebro(params):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(VWAPEMA200Strategy, cerebro=cerebro, **params)
    cerebro.broker.set_cash(1000)
    cerebro.broker.setcommission(commission=0.0002)
    cerebro.adddata(PandasData(dataname=combined_df))
    cerebro.run()
    return cerebro.broker.get_value()

if __name__ == '__main__':
    # 创建Cerebro引擎
    cerebro = bt.Cerebro()

    # 加载数据
    data = PandasData(dataname=combined_df)

    # 将数据添加到Cerebro引擎
    cerebro.adddata(data)

    # 设置优化参数
    params_list = [
        {'vwap_period': vwap_period, 'ema_period': ema_period, 'take_profit': take_profit, 'stop_loss': stop_loss}
        for vwap_period in range(10, 20)
        for ema_period in range(180, 220)
        for take_profit in [0.03, 0.04, 0.05]
        for stop_loss in [0.005, 0.008, 0.01]
    ]

    # 运行优化
    results = []
    for params in params_list:
        value = run_cerebro(params)
        results.append((params, value))

    # 输出最佳参数组合
    best_result = max(results, key=lambda x: x[1])
    print(f"最佳参数组合: {best_result[0]}")
    print(f"最佳回报: {best_result[1]}")