import pandas as pd

def add_ma_to_csv(file_path='data.csv', ma_period=360, output_path='data_with_ma.csv'):
    df = pd.read_csv(file_path, parse_dates=['timestamp'], index_col='timestamp')
    df.sort_index(inplace=True)  # make sure it's sorted from oldest to newest
    df[f'ma_360'] = df['close'].rolling(window=ma_period).mean()
    df[f'ma_360'] = df['close'].rolling(window=ma_period).mean()
    df.dropna(inplace=True)  # drop rows with incomplete MA calculation
    df.to_csv(output_path)
    #print(f"Added MA column and saved to {output_path}")
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

