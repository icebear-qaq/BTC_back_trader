import backtrader as bt
from data_loader.data_loader import load_data
from strategies.vwap_ema200_strategy import VWAPEMA200Strategy

# Define the file path
data_dir = 'recent'

# Load the data
combined_df = load_data(data_dir)

# Create a Backtrader data feed
class PandasData(bt.feeds.PandasData):
    # Set the DataFrame column name mapping
    lines = ('amount',)
    params = (
        ('datetime', None),  # The datetime column will use the index
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
    # Create the Cerebro engine
    cerebro = bt.Cerebro()

    # Load the data
    data = PandasData(dataname=combined_df)

    # Add the data to the Cerebro engine
    cerebro.adddata(data)

    # Set the optimization parameters
    params_list = [
        {'vwap_period': vwap_period, 'ema_period': ema_period, 'take_profit': take_profit, 'stop_loss': stop_loss}
        for vwap_period in range(10, 20)
        for ema_period in range(180, 220)
        for take_profit in [0.03, 0.04, 0.05]
        for stop_loss in [0.005, 0.008, 0.01]
    ]

    print("To enter the parameter optimization process, please input: 1, else input any key")
    if input() == "1":
        # Run the optimization
        results = []
        for params in params_list:
            value = run_cerebro(params)
            results.append((params, value))

        # Output the best parameter combination
        best_result = max(results, key=lambda x: x[1])
        print(f"Best parameter combination: {best_result[0]}")
        print(f"Best return: {best_result[1]}")
    else:
        run_cerebro(params={'vwap_period': 10, 'ema_period': 180, 'take_profit': 0.008, 'stop_loss': 0.006})