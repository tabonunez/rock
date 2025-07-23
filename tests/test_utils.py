import os
import time
import pytest
from unittest import mock

from trading.utils import (
    decimal_round,
    calc_vwap,
    retry,
    circuit_breaker,
    log_trade_csv,
)


def test_decimal_round():
    assert decimal_round(1.23456, 0.01) == 1.23
    assert decimal_round(0.0999, 0.0001) == 0.0999
    assert decimal_round(0.09999, 0.0001) == 0.0999


def test_calc_vwap():
    fills = [(100.0, 1.0), (101.0, 2.0)]
    vwap = calc_vwap(fills)
    assert abs(vwap - 100.6666667) < 1e-6
    assert calc_vwap([]) is None


def test_retry_decorator(monkeypatch):
    calls = {"n": 0}

    @retry(max_tries=3, backoff=0)
    def flaky():
        calls["n"] += 1
        if calls["n"] < 2:
            raise ValueError("boom")
        return "ok"

    assert flaky() == "ok"
    assert calls["n"] == 2  # succeeded on 2nd attempt


def test_circuit_breaker(monkeypatch):
    class Dummy:
        def __init__(self):
            self.fail = True

        @circuit_breaker(max_failures=2, cooldown=0.1)
        def maybe_fail(self):
            if self.fail:
                raise RuntimeError("fail")
            return "ok"

    d = Dummy()
    # Two consecutive failures – breaker should open on 2nd exception
    with pytest.raises(RuntimeError):
        d.maybe_fail()
    with pytest.raises(Exception):
        d.maybe_fail()

    # While breaker open, immediate exception
    with pytest.raises(Exception):
        d.maybe_fail()

    # After cooldown, should work again when fail flag cleared
    time.sleep(0.11)
    d.fail = False
    assert d.maybe_fail() == "ok"


def test_log_trade_csv(tmp_path):
    log_file = tmp_path / "trades.csv"
    headers = ["action", "symbol", "price"]
    row1 = ["ENTRY", "BTCUSDT", 10000]
    row2 = ["EXIT", "BTCUSDT", 10100]

    log_trade_csv(str(log_file), headers, row1)
    log_trade_csv(str(log_file), headers, row2)

    import csv

    with open(log_file, newline="") as f:
        data = list(csv.reader(f))

    assert data[0] == headers
    assert data[1] == [str(x) for x in row1]
    assert data[2] == [str(x) for x in row2]
