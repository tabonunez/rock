from binance_api import BinanceAPI
from config import CHUNK_SIZE_USDT
import math
import time

class TradeExecutor:
    def __init__(self):
        self.api = BinanceAPI()

    def execute_order(self, symbol, side, total_usdt, price):
        # Calculate how many contracts to buy/sell per chunk
        chunk_qty = CHUNK_SIZE_USDT / price
        total_qty = total_usdt / price
        n_chunks = math.ceil(total_qty / chunk_qty)
        for i in range(n_chunks):
            qty = min(chunk_qty, total_qty - i * chunk_qty)
            # Binance requires quantity precision, should be adjusted per symbol
            qty = round(qty, 3)
            try:
                resp = self.api.place_market_order(symbol, side, qty)
                print(f"Order {i+1}/{n_chunks} for {symbol}: {resp}")
                time.sleep(0.2)  # avoid rate limits
            except Exception as e:
                print(f"Order error for {symbol}: {e}")
