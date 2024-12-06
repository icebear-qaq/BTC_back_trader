import backtrader as bt
from data_loader.data_loader import load_data
from strategies.vwap_ema200_strategy import VWAPEMA200Strategy

# Define the file path
data_dir = 'test'

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

# Create the Cerebro engine
cerebro = bt.Cerebro()

# Load the data
data = PandasData(dataname=combined_df)

# Add the data to the Cerebro engine
cerebro.adddata(data)

# Add the strategy
cerebro.addstrategy(VWAPEMA200Strategy)

# Set the initial cash
cerebro.broker.set_cash(1000)

# Set the commission
cerebro.broker.setcommission(commission=0.0002)

# Print the initial cash
print(f'Initial cash: {cerebro.broker.get_value()}')

# Run the backtest
cerebro.run()

# Print the final cash
print(f'Final cash: {cerebro.broker.get_value()}')

# Plot the results
#cerebro.plot()