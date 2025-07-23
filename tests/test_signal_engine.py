import importlib
from collections import deque

import pytest

import trading.signal_engine as se_module
from trading.signal_engine import SignalEngine


def test_signal_engine_entry_exit(monkeypatch):
    """Ensure SignalEngine produces entry and exit signals with configured MA period and threshold."""
    # Reduce MA_PERIOD and threshold for quick testing
    monkeypatch.setattr(se_module, "MA_PERIOD", 3)
    monkeypatch.setattr(se_module, "MA_BASIS_POINTS", 0.01)  # 0.01 bp threshold

    engine = SignalEngine()

    symbol = "BTCUSDT"
    # Feed three equal prices – should produce no signal yet (ma_change zero)
    assert engine.update_price(symbol, 100) is None
    assert engine.update_price(symbol, 100) is None
    # Third price completes the moving average window – but ma_change still 0 -> no signal
    assert engine.update_price(symbol, 100) is None

    # Fourth price increases MA slightly above threshold – expect an "entry" signal
    assert engine.update_price(symbol, 100.05) == "entry"

    # Another flat price keeps MA roughly the same -> no transition
    assert engine.update_price(symbol, 100.05) is None

    # Drop price so MA falls back below threshold -> expect "exit" signal
    assert engine.update_price(symbol, 99.90) == "exit"
