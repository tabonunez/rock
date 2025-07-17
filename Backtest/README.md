# Real-Time Binance Perpetuals Trading Bot

This bot replicates a moving average momentum strategy on Binance USDT-margined perpetuals using market orders. Orders are chunked to avoid market impact and rate limits.

## Files
- `config.py`: Configuration (API keys, trade size, etc.)
- `binance_api.py`: Binance API handling (candles, orders, positions)
- `signal_engine.py`: Computes MA and generates entry/exit signals
- `trade_executor.py`: Splits and executes orders
- `main_live.py`: Main event loop (to be created)

## Usage
1. Fill in your Binance API credentials in `config.py`.
2. Adjust trading parameters as needed.
3. Run the main script: `python main_live.py`

**Risk management is your responsibility.**

---

## Rate Limit Handling
- The bot is designed to stay well below Binance rate limits.
- All requests are spaced and chunked.

---

## Disclaimer
- Use at your own risk. Crypto trading is risky and this code is for educational purposes.
