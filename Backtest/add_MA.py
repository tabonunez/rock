import pandas as pd

def add_ma_to_csv(file_path='data.csv', ma_period=360, output_path='data_with_ma.csv'):
    df = pd.read_csv(file_path, parse_dates=['timestamp'], index_col='timestamp')
    df.sort_index(inplace=True)  # make sure it's sorted from oldest to newest
    df[f'ma_360'] = df['close'].rolling(window=ma_period).mean()
    # Add volatility columns
    df['returns'] = df['close'].pct_change()
    df['volatility'] = df['returns'].rolling(window=20).std()
    df['volatility_ma'] = df['volatility'].rolling(window=20).mean()
    df.dropna(inplace=True)  # drop rows with incomplete MA calculation
    df.to_csv(output_path)
    #print(f"Added MA and volatility columns and saved to {output_path}")
    return df

def add_ma_change(file_path='data_with_ma.csv', ma_column='ma_360', output_path='data_with_ma_change.csv'):
    df = pd.read_csv(file_path, parse_dates=['timestamp'], index_col='timestamp')
    df.sort_index(inplace=True)

    df['ma_prev'] = df[ma_column].shift(1)
    df['ma_change'] = ((df[ma_column] / df['ma_prev']) - 1) * 10000  # in basis points

    # 1 if change > 1bp, else 0
    df['position_bool'] = (df['ma_change'] > 1).astype(int)

    df.dropna(inplace=True)
    df.to_csv(output_path)
    #print(f"Added ma_change and position_bool, saved to {output_path}")
    return df

def add_ma_change_short(file_path='data_with_ma.csv', ma_column='ma_360', output_path='data_with_ma_change_short.csv'):
    df = pd.read_csv(file_path, parse_dates=['timestamp'], index_col='timestamp')
    df.sort_index(inplace=True)

    df['ma_prev'] = df[ma_column].shift(1)
    df['ma_change'] = ((df[ma_column] / df['ma_prev']) - 1) * 10000  # in basis points

    # Add MA200 for trend filter
    df['ma_200'] = df['close'].rolling(window=360).mean()

    # 1 if change < -3bp, else 0 (stronger signal)
    df['position_bool'] = (df['ma_change'] < -1.5).astype(int)

    df.dropna(inplace=True)
    df.to_csv(output_path)
    #print(f"Added ma_change, MA200, and position_bool for short, saved to {output_path}")
    return df


