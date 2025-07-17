# Configuration for live trading bot

BINANCE_API_KEY = "YOUR_API_KEY_HERE"  # Fill in securely
BINANCE_API_SECRET = "YOUR_API_SECRET_HERE"  # Fill in securely

# Trading symbols (USDT perpetuals)
SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT", "TRXUSDT", "DOGEUSDT", "ADAUSDT", "PEPEUSDT", "AAVEUSDT", "LINKUSDT", "AVAXUSDT", "UNIUSDT"
]

# Strategy parameters
MA_PERIOD = 360  # periods (hours)
MA_BASIS_POINTS = 1  # Entry threshold

# Trading parameters
TOTAL_TRADE_AMOUNT_USDT = 1000  # Total capital per trade
CHUNK_SIZE_USDT = 100           # Amount per market order chunk

# Binance rate limits
REQUESTS_PER_MINUTE = 1100  # as per Binance API docs
SAFE_REQUESTS_PER_MINUTE = 900

# Other
BASE_URL = "https://fapi.binance.com"  # Binance Futures API endpoint

# Logging
LOG_FILE = "trade_log.txt"
