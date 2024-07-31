import pandas as pd
import numpy as np
from info import path

df_total = pd.DataFrame()
for year in np.arange(1975, 2025, 1):
    print(year)
    df = pd.read_excel("./population_par_region_1975_2024.xls", sheet_name=str(year), skiprows=4)
    df_ = df[["Unnamed: 0", "Total"]].iloc[:14].rename(columns={"Unnamed: 0": "name", "Total": f"{year}"})
    if df_total.empty:
        df_total = df_.copy()
    else:
        df_total = df_total.merge(df_, left_on="name", right_on="name")
df_total["code"] = [84, 27, 53, 24, 9, 44, 32, 11, 28, 75, 76, 52, 93, 0]
df_total.to_csv(path / 'ressources' / 'population_par_region_evolution.csv', index=False, sep=";")
