import pandas as pd
from openpyxl import load_workbook


output_excel = 'ma_csvs/Rock.xlsx'
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

# Load existing workbook

with pd.ExcelWriter(output_excel, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    for coin  in coins:
        file_path = 'ma_csvs/' + coin +'USDT' + '.csv'
        sheet_name = file_path.split('/')[-1].replace('.csv', '')[:31]
        df = pd.read_csv(file_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp', ascending=False)
        df.to_excel(writer, sheet_name=coin, index=False)

print(f"✅ New sheets added to {output_excel}")