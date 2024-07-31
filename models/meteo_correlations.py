import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sentinel_api import SentinelClient
import plotly.express as px
import plotly.graph_objects as go



client = SentinelClient()
df_disease = client.get_incidence(3, geo="RDD")
df_temperature = pd.read_csv("../meteo_API/meteo_historique/temperature_moyenne_regions.csv", sep=";")
df_temperature["time"] = pd.to_datetime(df_temperature["time"], format="%Y-%m-%d")
df_population = pd.read_csv("../ressources/population_par_region_evolution.csv", sep=";")


df_temperature = df_temperature.rename({"Centre-Val de Loire": "Centre-Val-de-Loire", "Corsica": "Corse",
                                        "Provence-Alpes-Côte d’Azur": "Provence-Alpes-Côte d'Azur"}, axis=1)
mapper = {df_population.iloc[i]["name"]: df_population.iloc[i]["code"] for i in range(len(df_population))}
df_temperature2 = pd.melt(df_temperature, id_vars=["time"], var_name="region", value_name="temperature")
df_temperature2["code"] = df_temperature2["region"].map(mapper).astype(int)


for region in df_temperature.columns[1:]:
    print(region)
    region_code = df_population[df_population["name"]==region]["code"].values[0]

    df = df_disease[df_disease["geo_insee"] == region_code]


    fig = px.line(df, "date", "inc")

    fig2  = px.line(df_temperature, "time", region)
    fig.add_trace(fig2.data[0])
    fig.data[1].update(yaxis="y2")

    fig.show()
    break