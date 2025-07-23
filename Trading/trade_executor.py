from trading.binance_api import BinanceAPI
from trading.config import get_chunk_size, get_symbol_step_size, get_symbol_min_qty
import math
import time

from trading.utils import decimal_round
from decimal import Decimal

# Helper to round quantity to step size using Decimal for precision
def round_qty_to_step(qty, step):
    return float(decimal_round(qty, step))

class TradeExecutor:
    def __init__(self):
        self.api = BinanceAPI()

    def execute_order(self, symbol, side, total_usdt, price, max_retries=3, chunk_size_usdt=None, test_mode=False):
        if chunk_size_usdt is None:
            chunk_size_usdt = get_chunk_size(symbol)
        from trading.config import TOTAL_TRADE_AMOUNT_USDT
        # In test mode, ensure existing position exposure does not exceed portfolio cap
        if test_mode:
            try:
                pos_info = self.api.get_position(symbol)
                if isinstance(pos_info, list):
                    # Binance returns a list; take the first dict
                    pos_info = pos_info[0]
                position_amt = float(pos_info.get('positionAmt', 0))  # positive long, negative short
                current_notional = abs(position_amt) * price
                if current_notional > TOTAL_TRADE_AMOUNT_USDT:
                    print(f"[TEST MODE] Skipping order for {symbol}: current position notional {current_notional:.2f} exceeds cap {TOTAL_TRADE_AMOUNT_USDT} USDT")
                    return {'vwap': None, 'notional': 0, 'qty': 0}
            except Exception as e:
                print(f"[TEST MODE] Could not fetch position for {symbol}: {e}. Proceeding without cap check.")
        chunk_qty = chunk_size_usdt / price
        total_qty = total_usdt / price
        filled_qty = 0.0
        chunk_num = 0
        step = get_symbol_step_size(symbol)
        min_qty = get_symbol_min_qty(symbol)
        from trading.config import get_symbol_min_notional
        min_notional = get_symbol_min_notional(symbol)
        fills = []  # (fill_price, fill_qty)
        if total_qty < min_qty:
            print(f"Total desired quantity {total_qty:.6f} for {symbol} is below Binance minimum ({min_qty}). No order will be placed.")
            return {'vwap': None, 'notional': 0, 'qty': 0}
        while filled_qty < total_qty:
            qty = min(chunk_qty, total_qty - filled_qty)
            qty = round_qty_to_step(qty, step)
            # Format quantity to correct decimals for Binance
            step_decimals = max(0, -int(round(math.log10(step))) if step < 1 else 0)
            qty = float(f"{qty:.{step_decimals}f}")
            notional = qty * price
            if qty < min_qty:
                print(f"Chunk quantity {qty:.6f} for {symbol} is below Binance minimum ({min_qty}). Skipping this chunk.")
                break
            if notional < min_notional:
                print(f"Chunk notional {notional:.2f} USDT for {symbol} is below Binance minimum notional ({min_notional}). Skipping this chunk.")
                break
            retries = 0
            while retries < max_retries:
                try:
                    resp = self.api.place_market_order(symbol, side, qty)
                    order_id = resp.get('orderId')
                    status = resp.get('status', '')
                    chunk_num += 1
                    print(f"Order {chunk_num} for {symbol}: {resp}")

                    # Poll order status until FILLED or timeout
                    poll_attempts = 0
                    max_poll_attempts = 20
                    while status != 'FILLED' and poll_attempts < max_poll_attempts:
                        time.sleep(1.5)
                        order_status = self.api.get_order_status(symbol, order_id)
                        status = order_status.get('status', '')
                        print(f"Polling order {order_id} for {symbol}: status={status}")
                        if status == 'FILLED':
                            executed_qty = float(order_status.get('executedQty', 0))
                            # VWAP: get avg fill price from order status or response
                            fill_price = None
                            if 'avgPrice' in order_status and float(order_status['avgPrice']) > 0:
                                fill_price = float(order_status['avgPrice'])
                            elif 'avgFillPrice' in order_status and float(order_status['avgFillPrice']) > 0:
                                fill_price = float(order_status['avgFillPrice'])
                            elif 'fills' in resp and len(resp['fills']) > 0:
                                fill_price = float(resp['fills'][0].get('price', 0))
                            else:
                                fill_price = price  # fallback to signal price
                            fills.append((fill_price, executed_qty))
                            filled_qty += executed_qty
                            break
                        poll_attempts += 1
                    if status != 'FILLED':
                        print(f"Warning: Order {order_id} for {symbol} not fully filled after polling (status: {status}). Retrying chunk.")
                        retries += 1
                        continue  # retry this chunk
                    else:
                        break  # chunk filled, proceed to next chunk
                except Exception as e:
                    retries += 1
                    print(f"Order error for {symbol} (attempt {retries}): {e}")
                    time.sleep(1.5 * retries)  # exponential backoff
            else:
                print(f"Failed to execute chunk for {symbol} after {max_retries} retries. Aborting remaining chunks.")
                break
            time.sleep(0.3)  # avoid rate limits
        # Compute VWAP
        total_notional = sum(q * p for p, q in fills)
        total_filled_qty = sum(q for _, q in fills)
        vwap = total_notional / total_filled_qty if total_filled_qty > 0 else None
        print(f"Total filled for {symbol}: {filled_qty:.6f} contracts (target: {total_qty:.6f}), VWAP: {vwap}")
        return {'vwap': vwap, 'notional': total_notional, 'qty': total_filled_qty}
