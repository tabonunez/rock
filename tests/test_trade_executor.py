from trading.trade_executor import round_qty_to_step


def test_round_qty_to_step_precision():
    assert round_qty_to_step(1.23456, 0.01) == 1.23
    assert round_qty_to_step(0.123456, 0.0001) == 0.1234
