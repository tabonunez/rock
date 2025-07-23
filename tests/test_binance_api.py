import hashlib
import hmac
import urllib.parse
from trading.binance_api import BinanceAPI


def test_sign():
    api = BinanceAPI()
    api.api_secret = "test_secret"
    params = {"symbol": "BTCUSDT", "timestamp": 1234567890}
    expected = hmac.new(
        b"test_secret",
        urllib.parse.urlencode(params).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    assert api._sign(params) == expected
