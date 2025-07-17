import requests
import time
import hmac
import hashlib
import urllib.parse
from config import BINANCE_API_KEY, BINANCE_API_SECRET, BASE_URL, SAFE_REQUESTS_PER_MINUTE

class BinanceAPI:
    def __init__(self):
        self.api_key = BINANCE_API_KEY
        self.api_secret = BINANCE_API_SECRET
        self.base_url = BASE_URL
        self.last_request_time = 0
        self.min_interval = 60 / SAFE_REQUESTS_PER_MINUTE

    def _sign(self, params):
        query_string = urllib.parse.urlencode(params)
        signature = hmac.new(self.api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        return signature

    def _headers(self):
        return {"X-MBX-APIKEY": self.api_key}

    def _rate_limit(self):
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()

    def get_klines(self, symbol, interval="1h", limit=500):
        self._rate_limit()
        url = f"{self.base_url}/fapi/v1/klines"
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        resp = requests.get(url, params=params, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def place_market_order(self, symbol, side, quantity):
        self._rate_limit()
        url = f"{self.base_url}/fapi/v1/order"
        params = {
            "symbol": symbol,
            "side": side,
            "type": "MARKET",
            "quantity": quantity,
            "timestamp": int(time.time() * 1000)
        }
        params["signature"] = self._sign(params)
        resp = requests.post(url, params=params, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def get_position(self, symbol):
        self._rate_limit()
        url = f"{self.base_url}/fapi/v2/positionRisk"
        params = {"symbol": symbol, "timestamp": int(time.time() * 1000)}
        params["signature"] = self._sign(params)
        resp = requests.get(url, params=params, headers=self._headers())
        resp.raise_for_status()
        return resp.json()
