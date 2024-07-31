import numpy as np
import pandas as pd


def split_years(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    sub_datasets = {}
    min_year = df['date'].min().year
    max_year = df['date'].max().year

    for year in range(min_year, max_year):
        start_date = pd.Timestamp(f'{year}-09-01')
        end_date = pd.Timestamp(f'{year + 1}-08-31')

        mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        sub_df = df.loc[mask]

        if not sub_df.empty:
            sub_datasets[f'{year}-{year + 1}'] = sub_df

    return sub_datasets


def compute_rmse(x, y):
    return np.sqrt(np.power((x - y), 2).sum() / len(x))


def compute_rrmse(x, y):
    return compute_rmse(x, y) / x.mean()
