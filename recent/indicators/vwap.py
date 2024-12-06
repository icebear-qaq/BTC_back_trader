import backtrader as bt

class VWAP(bt.Indicator):
    lines = ('vwap',)

    params = (
        ('period', 14),  # 默认14周期
    )

    def __init__(self):
        # 创建累积总价 * 成交量（成交额）和累积成交量
        self.addminperiod(self.params.period)
        self.initialized = False  # 添加一个标志位，用于初始化
        self.total_vol = 0  # 累计成交量
        self.total_value = 0  # 累计成交额

    def next(self):
        # 初始化VWAP
        if not self.initialized:
            self.lines.vwap[0] = 0  # 初始化VWAP为0
            self.initialized = True  # 设置标志位，表示已经初始化

        # 计算VWAP: 当前周期的成交额和成交量
        price_vol = self.data.close[0] * self.data.volume[0] * 1e9  # 转换成交量单位
        volume = self.data.volume[0] * 1e9  # 转换成交量单位

        # 确保 volume 不为零
        if volume == 0:
            print("成交量为零，设置为1")
            volume = 1

        # 累加成交额和成交量
        self.total_vol += volume
        self.total_value += price_vol

        # 计算VWAP: 累计成交额 / 累计成交量
        if self.total_vol != 0:
            self.lines.vwap[0] = self.total_value / self.total_vol
        else:
            self.lines.vwap[0] = 0