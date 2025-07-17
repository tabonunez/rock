import pandas as pd
from collections import deque
from config import MA_PERIOD, MA_BASIS_POINTS

class SignalEngine:
    def __init__(self):
        self.price_history = {}  # symbol: deque
        self.last_ma = {}        # symbol: float
        self.last_signal = {}    # symbol: int

    def update_price(self, symbol, close_price):
        if symbol not in self.price_history:
            self.price_history[symbol] = deque(maxlen=MA_PERIOD)
        self.price_history[symbol].append(close_price)
        return self.compute_signal(symbol)

    def compute_signal(self, symbol):
        ph = self.price_history[symbol]
        if len(ph) < MA_PERIOD:
            return 0  # not enough data
        ma = sum(ph) / MA_PERIOD
        prev_ma = self.last_ma.get(symbol, ma)
        ma_change = ((ma / prev_ma) - 1) * 10000 if prev_ma != 0 else 0
        signal = 1 if ma_change > MA_BASIS_POINTS else 0
        prev_signal = self.last_signal.get(symbol, 0)
        self.last_ma[symbol] = ma
        self.last_signal[symbol] = signal
        # Return entry/exit signal
        if prev_signal == 0 and signal == 1:
            return "entry"
        elif prev_signal == 1 and signal == 0:
            return "exit"
        else:
            return None
