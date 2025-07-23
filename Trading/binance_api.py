import requests
import time
import hmac
import hashlib
import urllib.parse
from trading.config import BINANCE_API_KEY, BINANCE_API_SECRET, BASE_URL, SAFE_REQUESTS_PER_MINUTE

class BinanceAPI:
    def __init__(self):
        self.api_key = BINANCE_API_KEY
        self.api_secret = BINANCE_API_SECRET
        self.base_url = BASE_URL
        self.last_request_time = 0
        self.min_interval = 60 / SAFE_REQUESTS_PER_MINUTE

    def set_leverage(self, symbol, leverage=1):
        self._rate_limit()
        url = f"{self.base_url}/fapi/v1/leverage"
        params = {
            "symbol": symbol,
            "leverage": leverage,
            "timestamp": int(time.time() * 1000)
        }
        params["signature"] = self._sign(params)
        try:
            resp = requests.post(url, params=params, headers=self._headers())
            resp.raise_for_status()
            print(f"Set leverage {leverage}x for {symbol}")
        except Exception as e:
            self._handle_unauthorized(e, context=f'set leverage for {symbol}')

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

    from trading.utils import circuit_breaker

    @circuit_breaker(max_failures=5, cooldown=600)
    def _handle_unauthorized(self, exc: Exception, context: str = ""):
        """If exception contains 401 status, print public IP address for debugging."""
        status_code = None
        if hasattr(exc, "response") and exc.response is not None:
            status_code = getattr(exc.response, "status_code", None)
        if status_code == 401:
            ip = None
            try:
                ip = requests.get("https://api.ipify.org", timeout=3).text.strip()
            except Exception:
                ip = "<unable to fetch>"
            print(f"401 Unauthorized while {context}. Public IP: {ip}. Error: {exc}")
        else:
            print(f"Failed while {context}: {exc}")

    def get_position(self, symbol, max_retries=3):
        for attempt in range(max_retries):
            try:
                self._rate_limit()
                url = f"{self.base_url}/fapi/v2/positionRisk"
                params = {"symbol": symbol, "timestamp": int(time.time() * 1000)}
                params["signature"] = self._sign(params)
                resp = requests.get(url, params=params, headers=self._headers())
                resp.raise_for_status()
                return resp.json()
            except requests.exceptions.RequestException as e:
                self._handle_unauthorized(e, context=f'fetching position for {symbol} (attempt {attempt+1})')
                time.sleep(2 * (attempt + 1))  # exponential backoff
        raise Exception(f"Failed to fetch position for {symbol} after {max_retries} attempts.")

    def get_open_orders(self, symbol):
        self._rate_limit()
        url = f"{self.base_url}/fapi/v1/openOrders"
        params = {"symbol": symbol, "timestamp": int(time.time() * 1000)}
        params["signature"] = self._sign(params)
        resp = requests.get(url, params=params, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def get_order_status(self, symbol, order_id):
        self._rate_limit()
        url = f"{self.base_url}/fapi/v1/order"
        params = {"symbol": symbol, "orderId": order_id, "timestamp": int(time.time() * 1000)}
        params["signature"] = self._sign(params)
        resp = requests.get(url, params=params, headers=self._headers())
        resp.raise_for_status()
        return resp.json()
