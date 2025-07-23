from add_MA import add_ma_to_csv, add_ma_change_short
from Calculate_prices_short import add_entry_exit_signals_short, calculate_pnl_short
from drawdown import add_max_drawdown
import os

# List of coins (adjust as needed)
coins = [
    "BTC",   # Bitcoin
    "ETH",   # Ethereum
    "XRP",   # XRP
    "SOL",   # Solana
    "TRX",   # Tron
    "DOGE",  # Dogecoin
    "ADA",   # Cardano
    "PEPE",  # Pepe
    "AAVE",  # Aave
    "LINK",  # Chainlink
    "AVAX",  # Avalanche
    "UNI",   # Uniswap
]
for coin in coins:
    csv_path = f'csvs/{coin}USDT.csv'
    ma_path = f'ma_csvs/{coin}USDT_short.csv'


    # Step 1: Add MA
    add_ma_to_csv(file_path=csv_path, output_path=ma_path, ma_period=360)

    # Step 2: Add MA change for short
    add_ma_change_short(file_path=ma_path, output_path=ma_path)

    # Step 3: Entry/exit signals for shorts
    add_entry_exit_signals_short(file_path=ma_path, output_path=ma_path)

    # Step 4: Calculate PnL for shorts
    calculate_pnl_short(file_path=ma_path, output_path=ma_path)

    # Step 5: Add drawdown stats
    add_max_drawdown(file_path=ma_path, output_path=ma_path)

    print(f"✅ Finished short strategy for {coin}")

# === Portfolio aggregation and drawdown for shorts ===
from portfolio import combine_weighted_portfolio
from drawdown import add_max_drawdown

# Portfolio weights (adjust if needed)
weights = [
    0.25,   # BTC
    0.1,    # ETH
    0.18,   # XRP
    0.17,   # SOL
    0.05,   # TRX
    0.1,    # DOGE
    0.05,   # ADA
    0.058,  # PEPE
    0.015,  # AAVE
    0.012,  # LINK
    0.008,  # AVAX
    0.007,  # UNI
]

paths = []


for coin in coins:
    path = 'ma_csvs/' + coin + 'USDT_short' + '.csv'
    paths.append(path) 
combine_weighted_portfolio(paths, weights, output_path='portfolio_cum_pnl_short.csv')
add_max_drawdown('portfolio_cum_pnl_short.csv', output_path='portfolio_drawdown_short.csv')
print('✅ Portfolio short aggregation and drawdown complete')
