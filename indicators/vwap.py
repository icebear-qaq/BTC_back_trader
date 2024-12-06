import backtrader as bt

class VWAP(bt.Indicator):
    lines = ('vwap',)

    params = (
        ('period', 14),  # Default period of 14
    )

    def __init__(self):
        # Create cumulative total price * volume (total value) and cumulative volume
        self.addminperiod(self.params.period)
        self.initialized = False  # Add a flag to indicate initialization
        self.total_vol = 0  # Cumulative volume
        self.total_value = 0  # Cumulative total value

    def next(self):
        # Initialize VWAP
        if not self.initialized:
            self.lines.vwap[0] = 0  # Initialize VWAP to 0
            self.initialized = True  # Set the flag to indicate initialization

        # Calculate VWAP: current period's total value and volume
        price_vol = self.data.close[0] * self.data.volume[0] * 1e9  # Convert volume unit
        volume = self.data.volume[0] * 1e9  # Convert volume unit

        # Ensure volume is not zero
        if volume == 0:
            print("Volume is zero, setting to 1")
            volume = 1

        # Accumulate total value and volume
        self.total_vol += volume
        self.total_value += price_vol

        # Calculate VWAP: cumulative total value / cumulative volume
        if self.total_vol != 0:
            self.lines.vwap[0] = self.total_value / self.total_vol
        else:
            self.lines.vwap[0] = 0