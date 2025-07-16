import requests
import pandas as pd
import time
from datetime import datetime, timedelta

def fetch_binance_klines(symbol='BTCUSDT', interval='1h', start_str='2023-01-01', end_str=None, save_path='data.csv'):
    base_url = 'https://api.binance.com/api/v3/klines'
    limit = 1000
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
        start_ts = last_ts + 1
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
