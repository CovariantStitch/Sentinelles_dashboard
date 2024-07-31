import streamlit as st
import pandas as pd
from sentinel_api import SentinelClient
from info import path
import plotly.express as px
from common import labels, get_data_from_api
import datetime

# load client
client = SentinelClient()
diseases_list_with_regions = client.diseases_list_with_regions
disease = st.selectbox("Sélectionner une pathologie", diseases_list_with_regions, index=2)
start_date = datetime.datetime(2010, 1, 1)
df_disease = get_data_from_api(client, disease, geo="RDD")
df_disease = df_disease[df_disease["date"] > start_date]


# load temperature and population
df_temperature = pd.read_csv(path / "meteo_API" / "meteo_historique" / "temperature_moyenne_regions.csv", sep=";")
df_temperature["time"] = pd.to_datetime(df_temperature["time"], format="%Y-%m-%d")
df_temperature = df_temperature[df_temperature["time"] > start_date]
correlations = df_disease[["date", "inc"]].merge(df_temperature, left_on="date", right_on="time").corr(numeric_only=True)
df_population = pd.read_csv(path / "ressources" / "population_par_region_evolution.csv", sep=";")
df_temperature = df_temperature.rename({"Centre-Val de Loire": "Centre-Val-de-Loire", "Corsica": "Corse",
                                        "Provence-Alpes-Côte d’Azur": "Provence-Alpes-Côte d'Azur"}, axis=1)
mapper = {df_population.iloc[i]["name"]: df_population.iloc[i]["code"] for i in range(len(df_population))}
df_temperature = pd.melt(df_temperature, id_vars=["time"], var_name="region", value_name="temperature")
df_temperature["code"] = df_temperature["region"].map(mapper).astype(int)

region = st.selectbox("Sélectionner une région", df_temperature["region"].unique(), index=2)
region_code = df_population[df_population["name"]==region]["code"].values[0]
df_d = df_disease[df_disease["geo_insee"] == region_code]
df_t = df_temperature[df_temperature["region"] == region]
# plots
fig = px.line(df_d, "date", "inc100", labels=labels)
fig2  = px.line(df_t, "time", "temperature")
fig.add_trace(fig2.data[0])
fig.data[1].update(yaxis="y2", line_color="#ff7f0e")
fig.update_layout(
    yaxis=dict(
        titlefont=dict(color="#1f77b4"),tickfont=dict(color="#1f77b4")),
    yaxis2=dict(
        title="Temperature (°C)",
        titlefont=dict(color="#ff7f0e"), tickfont=dict(color="#ff7f0e"), anchor="x", overlaying="y", side="right")
)

st.plotly_chart(fig)

fig = px.imshow(correlations)
st.plotly_chart(fig)