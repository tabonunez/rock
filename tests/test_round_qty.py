from trading.trade_executor import round_qty_to_step

def test_round_qty_to_step():
    assert round_qty_to_step(1.2345, 0.01) == 1.23
    assert round_qty_to_step(0.1234, 0.0001) == 0.1234
    