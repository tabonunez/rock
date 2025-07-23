import requests
import pandas as pd
import time
from datetime import datetime, timedelta

def fetch_binance_klines(symbol='BTCUSDT', interval='1h', start_str='2023-01-01', end_str=None, save_path='data.csv'):
    base_url = 'https://api.binance.com/api/v3/klines'
    limit = 1000
    # Map interval string to milliseconds for proper cursor advance
    interval_ms = {
        "1m": 60_000,
        "3m": 180_000,
        "5m": 300_000,
        "15m": 900_000,
        "30m": 1_800_000,
        "1h": 3_600_000,
        "2h": 7_200_000,
        "4h": 14_400_000,
        "6h": 21_600_000,
        "8h": 28_800_000,
        "12h": 43_200_000,
        "1d": 86_400_000,
    }
    if interval not in interval_ms:
        raise ValueError(f"Unsupported interval: {interval}")
    start_ts = int(pd.to_datetime(start_str).timestamp() * 1000)
    end_ts = int(pd.to_datetime(end_str).timestamp() * 1000) if end_str else int(time.time() * 1000)

    all_candles = []
    while start_ts < end_ts:
        url = f"{base_url}?symbol={symbol}&interval={interval}&startTime={start_ts}&limit={limit}"
        response = requests.get(url)
        data = response.json()

        if not data:
            break

        all_candles.extend(data)
        last_ts = data[-1][0]
        start_ts = last_ts + interval_ms[interval]
        time.sleep(0.5)  # sleep to avoid hitting the rate limit

    df = pd.DataFrame(all_candles, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df = df[["open", "high", "low", "close", "volume"]].astype(float)

    df.to_csv(save_path)
    #print(f"Saved {len(df)} rows to {save_path}")

# Example usage:
#fetch_binance_klines('ETHUSDT', '1h', '2023-01-01', '2025-07-01')
