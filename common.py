from info import path
import streamlit as st
import geopandas as gpd
import pandas as pd
import numpy as np

from sentinel_api import SentinelClient

@st.cache_data
def load_shapefile():
    sf = gpd.read_file(path / 'ressources' / 'regions_France.geojson').astype({"code": np.int64})
    # enlever les DROM/TOM
    sf = sf[sf["code"] > 6]
    return sf


@st.cache_data
def load_population():
    file = path / 'ressources' / 'population_par_region_evolution.csv'
    population = pd.read_csv(file, sep=";")
    return population

@st.cache_data
def get_data_from_api(_client: SentinelClient, disease_: str, geo: str = "PAY"):
    indicators = _client.indicators_list
    id_pathologie = indicators[indicators["name"] == disease_]["id"].values[0]
    data = _client.get_incidence(id_pathologie=id_pathologie, geo=geo)
    return data

def add_double_divider(text):
    st.divider()
    st.markdown(
        f"""
            <div style="text-align: center; font-size: 24px; font-weight: bold;">
                {text}
            </div>
            """,
        unsafe_allow_html=True
    )
    st.divider()

labels = {"inc": "Incidence", "inc100": "Incidence pour 100 000 habitants", "time": "Date", "date": "Date",
          "geo_name": "Régions", "gaussian": "Ajustement gaussien", "sir": "Ajustement SIR"}
