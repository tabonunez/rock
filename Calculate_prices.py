import pandas as pd

def add_entry_exit_signals(file_path='data_with_ma_change.csv', output_path='data_with_signals.csv'):
    df = pd.read_csv(file_path, parse_dates=['timestamp'], index_col='timestamp')
    df.sort_index(inplace=True)

    df['position_bool_prev'] = df['position_bool'].shift(1)

    # Entry: prev was 0, now 1 → use previous close (negative to flag it as entry)
    df['trade_price'] = None
    entry_condition = (df['position_bool_prev'] == 0) & (df['position_bool'] == 1)
    df.loc[entry_condition, 'trade_price'] = -df['close']

    # Exit: prev was 1, now 0 → use current close
    exit_condition = (df['position_bool_prev'] == 1) & (df['position_bool'] == 0)
    df.loc[exit_condition, 'trade_price'] = df['close']

    df.drop(columns=['position_bool_prev'], inplace=True)
    df.to_csv(output_path)
    #print(df['trade_price'].sum())
    #print(f"Trade signals written to {output_path}")
    return df


def calculate_pnl(file_path='data_with_signals.csv', output_path='data_with_pnl.csv', notional=100000):
    df = pd.read_csv(file_path, parse_dates=['timestamp'], index_col='timestamp')
    df.sort_index(inplace=True)

    df['pnl'] = 0.0
    current_entry_price = None

    for idx, row in df.iterrows():
        price = row['trade_price']

        if pd.notna(price):
            if price < 0:  # entry
                current_entry_price = -price
            elif current_entry_price is not None:  # exit
                position_size = notional / current_entry_price
                pnl = position_size * price - notional
                df.at[idx, 'pnl'] = pnl
                current_entry_price = None  # reset after exit
    df['cumulative_pnl'] = df['pnl'].cumsum()
    print(df['cumulative_pnl'][-1],file_path)
    df.to_csv(output_path)
    #print(df['pnl'].sum())
    #print(f"PnL added and saved to {output_path}")
    return df

