from meteo_API.client_open_meteo import ClientOpenMeteo
import pandas as pd
import json
import numpy as np
import time
import os


if __name__ == "__main__":
    start_date = "1987-01-01"
    end_date = "2024-05-01"

    files = os.listdir("./meteo_historique")
    already_extracted = [file.split("_")[-1].split(".")[0] for file in files]

    with open("../ressources/cities_france.json", 'r', encoding="utf-8") as f:
        cities = json.load(f)
    df = pd.DataFrame(cities)
    df = df.astype({"lat": float, "lng": float, "population": float, "population_proper": float})
    client = ClientOpenMeteo()
    temperature = {region:[] for region in df["admin_name"].unique()}
    for region, df_ in df.groupby("admin_name"):
        if region in already_extracted:
            print(f"{region} already extracted")
            continue
        else:
            print(f"Extracting {region}")
        for i in range(min(10, len(df_))):
            meteo = client.get_meteo(df.iloc[i]["lat"], df.iloc[i]["lng"], start_date, end_date)
            temperature[region].append(meteo["daily"]["temperature_2m_mean"])
            dates = meteo["daily"]["time"]

        df_final = pd.DataFrame({"time": dates})
        temp_mean = np.array(temperature[region]).mean(axis=0)
        df_final[region] = temp_mean
        df_final.to_csv(f"./meteo_historique/temperature_moyenne_{region}.csv", sep=";", index=False)
        time.sleep(60)
