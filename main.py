from fetch_prices import fetch_binance_klines
from add_MA import add_ma_to_csv, add_ma_change
from Calculate_prices import add_entry_exit_signals, calculate_pnl
from drawdown import add_max_drawdown
from portfolio import combine_weighted_portfolio
coins = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT",'LINKUSDT','SUIUSDT','AVAXUSDT']

coins = [
    "AVAX",  # Avalanche
    "UNI",   # Uniswap
]


'''
for coin in coins:
    path = 'ma_csvs/' + coin +'USDT' + '.csv'
    path1 = 'csvs/' + coin +'USDT' + '.csv'
    fetch_binance_klines(coin + 'USDT', '1h', '2023-01-01', '2025-07-01', save_path=path1)
'''
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
    path = 'ma_csvs/' + coin +'USDT' + '.csv'
    path1 = 'csvs/' + coin +'USDT' + '.csv'   
    add_ma_to_csv(file_path=path1,output_path=path, ma_period=360)
    add_ma_change(file_path=path,output_path=path)
    add_entry_exit_signals(file_path=path,output_path=path)
    calculate_pnl(file_path=path,output_path=path)
    add_max_drawdown(file_path=path,output_path=path)
w = [0.32, 0.21, 0.12, 0.21, 0.02, 0.06, 0.02, 0.02, 0.02]


w = [
    0.25,   # BTC
    0.1,   # ETH
    0.18,   # XRP
    0.17,   # SOL
    0.05,   # TRX
    0.1,   # DOGE
    0.05,   # ADA
    0.058,  # PEPE
    0.015,  # AAVE
    0.012,  # LINK
    0.008,  # AVAX
    0.007,  # UNI
]

paths = []


for coin in coins:
    path = 'ma_csvs/' + coin + 'USDT' + '.csv'
    paths.append(path) 

 
combine_weighted_portfolio(paths,w)
add_max_drawdown('portfolio_cum_pnl.csv')





w = [
    0.25,   # BTC
    0.1,   # ETH
    0.18,   # XRP
    0.17,   # SOL
    0.05,   # TRX
    0.1,   # DOGE
    0.05,   # ADA
    0.058,  # PEPE
    0.015,  # AAVE
    0.012,  # LINK
    0.008,  # AVAX
    0.007,  # UNI
]
f = 0
for i in w:
    f = f+i

print(f)
