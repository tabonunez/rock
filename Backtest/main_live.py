import time
from binance_api import BinanceAPI
from signal_engine import SignalEngine
from trade_executor import TradeExecutor
from config import SYMBOLS, TOTAL_TRADE_AMOUNT_USDT, LOG_FILE

api = BinanceAPI()
signal_engine = SignalEngine()
trade_executor = TradeExecutor()

# Helper to get the latest close price from kline
def get_latest_close(symbol):
    klines = api.get_klines(symbol, limit=2)
    return float(klines[-1][4])  # close price

# Populate price history for all symbols at startup
for symbol in SYMBOLS:
    klines = api.get_klines(symbol, limit=360)
    for k in klines:
        close = float(k[4])
        signal_engine.update_price(symbol, close)
    print(f"Loaded {symbol} history")

print("Starting real-time trading loop...")
while True:
    for symbol in SYMBOLS:
        close = get_latest_close(symbol)
        signal = signal_engine.update_price(symbol, close)
        if signal == "entry":
            print(f"ENTRY signal for {symbol} at {close}")
            trade_executor.execute_order(symbol, "BUY", TOTAL_TRADE_AMOUNT_USDT, close)
            with open(LOG_FILE, "a") as f:
                f.write(f"ENTRY,{symbol},{close},{time.time()}\n")
        elif signal == "exit":
            print(f"EXIT signal for {symbol} at {close}")
            trade_executor.execute_order(symbol, "SELL", TOTAL_TRADE_AMOUNT_USDT, close)
            with open(LOG_FILE, "a") as f:
                f.write(f"EXIT,{symbol},{close},{time.time()}\n")
        time.sleep(1)
    # Sleep until next hour
    now = time.localtime()
    seconds_to_next_hour = 3600 - (now.tm_min * 60 + now.tm_sec)
    time.sleep(max(1, seconds_to_next_hour))
