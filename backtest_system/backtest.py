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

# 创建Cerebro引擎
cerebro = bt.Cerebro()

# 加载数据
data = PandasData(dataname=combined_df)

# 将数据添加到Cerebro引擎
cerebro.adddata(data)

# 添加策略
cerebro.addstrategy(VWAPEMA200Strategy)

# 设置初始资金
cerebro.broker.set_cash(1000)

# 设置佣金
cerebro.broker.setcommission(commission=0.0002)

# 输出初始资金
print(f'初始资金: {cerebro.broker.get_value()}')

# 运行回测
cerebro.run()

# 输出最终资金
print(f'最终资金: {cerebro.broker.get_value()}')

# 绘制结果
#cerebro.plot()