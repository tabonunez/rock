import pandas as pd

def combine_weighted_portfolio(file_paths, weights, output_path='portfolio_cum_pnl.csv'):
    """
    file_paths: list of CSVs with cumulative_pnl columns
    weights: list of floats summing to 1 (or any total)
    """
    assert len(file_paths) == len(weights), "Each file must have a weight."

    dfs = []
    for path, weight in zip(file_paths, weights):
        df = pd.read_csv(path, parse_dates=['timestamp'], index_col='timestamp')
        df = df[['cumulative_pnl']].copy()
        df.rename(columns={'cumulative_pnl': path.split('.')[0]}, inplace=True)
        df *= weight
        dfs.append(df)

    # Merge all PnLs on timestamp
    portfolio_df = pd.concat(dfs, axis=1).fillna(method='ffill').fillna(0)
    portfolio_df['cumulative_pnl'] = portfolio_df.sum(axis=1)
    print(portfolio_df['cumulative_pnl'][-1])
    portfolio_df.to_csv(output_path)
    print(f"✅ Portfolio cumulative PnL saved to {output_path}")
    return portfolio_df
