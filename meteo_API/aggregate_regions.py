import pandas as pd
import os

if __name__ == "__main__":
    files = os.listdir("./meteo_historique")
    df_total = pd.DataFrame()
    for file in files:
        if "region" in file:
            continue
        df = pd.read_csv(f"./meteo_historique/{file}", sep=";")

        if df_total.empty:
            df_total = df.copy()
        else:
            df_total = df_total.merge(df, left_on="time", right_on="time")
    df_total.to_csv("./meteo_historique/temperature_moyenne_regions.csv", sep=";", index=False)
