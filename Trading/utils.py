"""Utility helpers for trading bot (retry decorator, precision helpers, logging, etc.)"""
from functools import wraps
import time
import csv
import os
from decimal import Decimal, getcontext
from trading.config import LOG_FILE
from typing import Callable, Any

# Give plenty precision for financial calcs
getcontext().prec = 18


def retry(max_tries: int = 3, backoff: float = 2.0):
    """Simple retry decorator for network/API calls.

    Parameters
    ----------
    max_tries: int
        Maximum number of attempts (initial try + retries).
    backoff: float
        Seconds multiplier for exponential back-off (wait = backoff * attempt).
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_tries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt >= max_tries - 1:
                        raise
                    wait = backoff * (attempt + 1)
                    print(f"{func.__name__}: error on attempt {attempt + 1}/{max_tries}: {e}. Retrying in {wait}s")
                    time.sleep(wait)
        return wrapper

    return decorator


def circuit_breaker(max_failures: int = 5, cooldown: float = 600.0):
    """Decorator implementing a simple circuit breaker.

    After `max_failures` consecutive exceptions, the circuit opens and further
    calls raise instantly for `cooldown` seconds. After the cooldown, the
    breaker resets automatically.
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Initialize state vars on first use
            if not hasattr(self, "_cb_failures"):
                self._cb_failures = 0
                self._cb_open = False
                self._cb_opened_at = 0.0

            # If open, check cooldown
            if self._cb_open:
                if time.time() - self._cb_opened_at < cooldown:
                    raise Exception("Circuit breaker open – skipping call")
                # Cooldown passed → reset
                self._cb_open = False
                self._cb_failures = 0

            try:
                result = func(self, *args, **kwargs)
                # Success → reset failures
                self._cb_failures = 0
                return result
            except Exception as e:
                self._cb_failures += 1
                if self._cb_failures >= max_failures:
                    self._cb_open = True
                    self._cb_opened_at = time.time()
                    print(f"Circuit breaker OPEN after {self._cb_failures} consecutive failures in {func.__name__}")
                raise
        return wrapper
    return decorator


def decimal_round(value: float | str, step: float | str) -> Decimal:
    """Round *down* value to the nearest multiple of step using Decimal for precision."""
    value_dec = Decimal(str(value))
    step_dec = Decimal(str(step))
    return float((value_dec // step_dec) * step_dec)


def log_trade_csv(log_path: str, headers: list[str], row: list[Any]):
    """Append a trade row to CSV, writing headers if the file is new."""
    file_exists = os.path.exists(log_path)
    with open(log_path, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)
        writer.writerow(row)


def calc_vwap(fills: list[tuple[float, float]]) -> float | None:
    """Calculate VWAP from list of (price, qty). Returns None if no fills."""
    if not fills:
        return None
    total_notional = sum(Decimal(str(p)) * Decimal(str(q)) for p, q in fills)
    total_qty = sum(Decimal(str(q)) for _, q in fills)
    if total_qty == 0:
        return None
    vwap = total_notional / total_qty
    return float(vwap)
