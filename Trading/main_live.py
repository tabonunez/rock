import time
from trading.binance_api import BinanceAPI
from trading.signal_engine import SignalEngine
from trading.trade_executor import TradeExecutor
from trading.config import SYMBOLS, TOTAL_TRADE_AMOUNT_USDT, PORTFOLIO_WEIGHTS, LOG_FILE

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
    api.set_leverage(symbol, 1)

def wait_until_next_hour():
    now = time.localtime()
    seconds_to_next_hour = 3600 - (now.tm_min * 60 + now.tm_sec)
    if seconds_to_next_hour > 0:
        print(f"Waiting {seconds_to_next_hour} seconds until next hour...")
        time.sleep(seconds_to_next_hour)

print("Starting real-time trading loop...")
#wait_until_next_hour()  # Ensure we start at the very beginning of the next candle

def get_open_position_amt(symbol):
    pos_info = api.get_position(symbol)
    # positionAmt is a string, convert to float; Binance returns a list
    amt = float(pos_info[0]['positionAmt']) if isinstance(pos_info, list) else float(pos_info['positionAmt'])
    return amt

def get_total_open_notional():
    total = 0.0
    for sym in SYMBOLS:
        amt = get_open_position_amt(sym)
        if abs(amt) > 1e-8:
            price = get_latest_close(sym)
            total += abs(amt) * price
    return total

while True:
    for symbol in SYMBOLS:
        close = get_latest_close(symbol)
        signal = signal_engine.update_price(symbol, close)
        trade_usdt = TOTAL_TRADE_AMOUNT_USDT * PORTFOLIO_WEIGHTS[symbol]
        position_amt = get_open_position_amt(symbol)
        if signal == "entry":
            open_orders = api.get_open_orders(symbol)
            if open_orders:
                print(f"ENTRY signal for {symbol} at {close}, but open orders exist. Skipping new entry order.")
                continue
            # Check portfolio-level notional cap
            total_open_notional = get_total_open_notional()
            if total_open_notional + trade_usdt > TOTAL_TRADE_AMOUNT_USDT + 1e-8:
                print(f"ENTRY signal for {symbol} at {close}, but total open notional ({total_open_notional:.2f} USDT) + new trade ({trade_usdt:.2f} USDT) exceeds cap ({TOTAL_TRADE_AMOUNT_USDT} USDT). Skipping entry.")
                continue
            if abs(position_amt) < 1e-8:
                print(f"ENTRY signal for {symbol} at {close}")
                result = trade_executor.execute_order(symbol, "BUY", trade_usdt, close)
                vwap = result['vwap']
                notional = result['notional']
                from datetime import datetime
                now = datetime.now()
                from trading.utils import log_trade_csv
                log_trade_csv(LOG_FILE, ['action','symbol','signal_price','vwap','notional','epoch','human_time'],
                               ['ENTRY', symbol, close, vwap, notional, time.time(), now.strftime('%Y-%m-%d %H:%M:%S')])
            else:
                print(f"ENTRY signal for {symbol} at {close}, but position already open: {position_amt}")
        elif signal == "exit":
            open_orders = api.get_open_orders(symbol)
            if open_orders:
                print(f"EXIT signal for {symbol} at {close}, but open orders exist. Skipping new exit order.")
                continue
            if abs(position_amt) > 1e-8:
                print(f"EXIT signal for {symbol} at {close}, closing position of {position_amt}")
                # Loop: exit in chunks until position is zero
                max_exit_loops = 10
                exit_loops = 0
                exit_notional = abs(position_amt) * close
                exit_price = close
                exit_epoch = time.time()
                from datetime import datetime
                exit_human = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # Execute exit and get VWAP
                result = trade_executor.execute_order(symbol, side, exit_notional, close)
                vwap = result['vwap']
                notional = result['notional']
                from trading.utils import log_trade_csv
                log_trade_csv(LOG_FILE, ['action','symbol','signal_price','vwap','notional','epoch','human_time'],
                               ['EXIT', symbol, exit_price, vwap, notional, exit_epoch, exit_human])
                if abs(position_amt) < 1e-8:
                    print(f"Successfully closed all position for {symbol}")
                else:
                    print(f"Warning: Could not fully close position for {symbol} after {exit_loops} attempts. Remaining: {position_amt}")
            else:
                print(f"EXIT signal for {symbol} at {close}, but no open position to close.")
        time.sleep(1)
    wait_until_next_hour()  # Wait until the next hourly candle
