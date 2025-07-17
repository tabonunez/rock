# Configuration for live trading bot

# API keys are now stored in secret_keys.py for security. DO NOT commit secret_keys.py to version control!
from secret_keys import BINANCE_API_KEY, BINANCE_API_SECRET




# Trading symbols (USDT perpetuals)
SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT", "TRXUSDT", "DOGEUSDT", "ADAUSDT", "PEPEUSDT", "AAVEUSDT", "LINKUSDT", "AVAXUSDT", "UNIUSDT"
]

# Portfolio weights as a dictionary (symbol: weight)
PORTFOLIO_WEIGHTS = {
    "BTCUSDT": 0.25,
    "ETHUSDT": 0.10,
    "XRPUSDT": 0.18,
    "SOLUSDT": 0.17,
    "TRXUSDT": 0.05,
    "DOGEUSDT": 0.10,
    "ADAUSDT": 0.05,
    "PEPEUSDT": 0.058,
    "AAVEUSDT": 0.015,
    "LINKUSDT": 0.012,
    "AVAXUSDT": 0.008,
    "UNIUSDT": 0.007,
}


SYMBOLS = ["SOLUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT", "AAVEUSDT", "DOTUSDT"]
PORTFOLIO_WEIGHTS = {
    "SOLUSDT": 0.3,
    "XRPUSDT": 0.4,
    "DOGEUSDT": 0.1,
    "ADAUSDT": 0.1,
    "AAVEUSDT": 0.1,
    "DOTUSDT": 0.1,
    }




# Strategy parameters
MA_PERIOD = 360  # periods (hours)
MA_BASIS_POINTS = 1  # Entry threshold

# Trading parameters
TOTAL_TRADE_AMOUNT_USDT = 100  # Total capital to allocate across all coins (portfolio level)

# Define liquidity classes for chunk sizing
CLASS_A = [  # Most liquid
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"
]
CLASS_B = [  # Less liquid
    "TRXUSDT", "DOGEUSDT", "ADAUSDT", "PEPEUSDT", "AAVEUSDT", "LINKUSDT", "AVAXUSDT", "UNIUSDT"
]
CHUNK_SIZE_A = 10   # USDT per order for class A
CHUNK_SIZE_B = 10   # USDT per order for class B

def get_chunk_size(symbol):
    if symbol in CLASS_A:
        return CHUNK_SIZE_A
    else:
        return CHUNK_SIZE_B

# Helper: calculate per-symbol trade size based on weights
# Example usage in main_live.py:
#   trade_usdt = TOTAL_TRADE_AMOUNT_USDT * PORTFOLIO_WEIGHTS[symbol]

# Symbol precision and minQty cache and fetchers
symbol_precision_cache = {}
symbol_min_qty_cache = {}
symbol_min_notional_cache = {}
import requests

def get_symbol_min_notional(symbol):
    if symbol in symbol_min_notional_cache:
        return symbol_min_notional_cache[symbol]
    url = BASE_URL + "/fapi/v1/exchangeInfo"
    resp = requests.get(url)
    resp.raise_for_status()
    info = resp.json()
    for s in info['symbols']:
        if s['symbol'] == symbol:
            for f in s['filters']:
                if f['filterType'] == 'MIN_NOTIONAL':
                    min_notional = float(f['notional'])
                    symbol_min_notional_cache[symbol] = min_notional
                    return min_notional
    raise ValueError(f"minNotional not found for symbol {symbol}")
# Usage: get_symbol_min_notional(symbol) returns minimum USDT value for any order for that symbol.

def get_symbol_step_size(symbol):
    if symbol in symbol_precision_cache:
        return symbol_precision_cache[symbol]
    url = BASE_URL + "/fapi/v1/exchangeInfo"
    resp = requests.get(url)
    resp.raise_for_status()
    info = resp.json()
    for s in info['symbols']:
        if s['symbol'] == symbol:
            for f in s['filters']:
                if f['filterType'] == 'LOT_SIZE':
                    step_size = float(f['stepSize'])
                    symbol_precision_cache[symbol] = step_size
                    return step_size
    raise ValueError(f"Step size not found for symbol {symbol}")

def get_symbol_min_qty(symbol):
    if symbol in symbol_min_qty_cache:
        return symbol_min_qty_cache[symbol]
    url = BASE_URL + "/fapi/v1/exchangeInfo"
    resp = requests.get(url)
    resp.raise_for_status()
    info = resp.json()
    for s in info['symbols']:
        if s['symbol'] == symbol:
            for f in s['filters']:
                if f['filterType'] == 'LOT_SIZE':
                    min_qty = float(f['minQty'])
                    symbol_min_qty_cache[symbol] = min_qty
                    return min_qty
    raise ValueError(f"minQty not found for symbol {symbol}")

# Binance rate limits
REQUESTS_PER_MINUTE = 1100  # as per Binance API docs
SAFE_REQUESTS_PER_MINUTE = 900

# Other
BASE_URL = "https://fapi.binance.com"  # Binance Futures API endpoint

# Logging
LOG_FILE = "trade_log.txt"
