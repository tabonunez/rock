import pandas as pd

def add_max_drawdown(file_path='data_with_cum_pnl.csv', output_path='data_with_drawdown.csv'):
    df = pd.read_csv(file_path, parse_dates=['timestamp'], index_col='timestamp')
    df.sort_index(inplace=True)

    # Running peak of cumulative pnl
    df['cum_peak'] = df['cumulative_pnl'].cummax()

    # Drawdown = current pnl - peak
    df['drawdown'] = df['cumulative_pnl'] - df['cum_peak']

    # Max drawdown value
    max_dd = df['drawdown'].min()
    max_dd_row = df['drawdown'].idxmin()
    peak_row = df.loc[:max_dd_row]['cumulative_pnl'].idxmax()

    print(f"📉 Max Drawdown: {max_dd:.2f}")
    print(f"From peak at {peak_row} to trough at {max_dd_row}")
    df.to_csv(output_path)
    return df
