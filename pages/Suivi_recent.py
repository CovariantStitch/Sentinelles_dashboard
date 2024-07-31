import datetime

import plotly.express as px
import streamlit as st

from common import get_data_from_api, add_double_divider, labels
from common_plots import plot_map
from sentinel_api import SentinelClient

# charge le client
client = SentinelClient()
diseases_list_with_regions = client.diseases_list_with_regions

add_double_divider("Suivi des pathologies saisonnières disponibles : France entière")
cols = st.columns(2)
add_double_divider(f"Suivi des pathologies saisonnières disponibles : par régions")
cols_region = st.columns(2)

seuil_epidemique = {"Syndromes Grippaux": [100, 200], "Diarrhée aiguë": [90, 200], "Varicelle": [15, 30],
                    "Infection respiratoire aiguë (IRA)": [225, 525]}
circle_indicators = [":large_green_square:", ":large_orange_square:", ":large_red_square:"]

st.sidebar.header("Etat des pathologies en France")
# charger les données pour les quatre pathologies avec suivi
for i, disease in enumerate(diseases_list_with_regions):
    # charger les données
    indicators = client.indicators_list
    id_pathologie = indicators[indicators["name"] == disease]["id"].values[0]
    df_pays = get_data_from_api(client, disease, geo="PAY")

    # filtre sur l'année courante
    current_year = datetime.datetime.now().year
    start_date = datetime.datetime(current_year - 1, 9, 1)
    end_date = datetime.datetime.now()
    df_pays = df_pays[(df_pays["date"] > start_date) & (df_pays["date"] < end_date)]

    # indicateurs sidebar
    seuil = seuil_epidemique[disease]
    state = ""
    for j in range(3):
        actual = df_pays.iloc[2 - j]['inc100']
        cat = 0 if actual < seuil[0] else (1 if actual < seuil[1] else 2)
        state += circle_indicators[cat] + " "
    st.sidebar.markdown(f"{disease} : {state}", help=str(df_pays.iloc[0]['date']))

    # Affichage pays
    fig = px.line(df_pays, x="date", y="inc100", labels=labels, title=disease)
    with cols[i // 2]:
        st.plotly_chart(fig)

    # Affichage régions
    df_regions = get_data_from_api(client, disease, geo="RDD")
    df_regions = df_regions[df_regions["date"] == df_regions["date"].max()]
    with cols_region[i // 2]:
        fig = plot_map(df_regions, range_color=[0, seuil[-1]])
        fig.update_layout(title=f"{disease} (au {df_regions['date'].max().strftime('%Y-%m-%d')})")
        st.plotly_chart(fig)

    # indicateurs sidebar
    # st.sidebar.markdown(f"{disease} : ")
    # for idx, df_ in df_regions.groupby("geo_name"):
    #     actual = df_.iloc[0]['inc100']
    #     circle = 0 if actual < seuil[0] else (1 if actual < seuil[1] else 2)
    #     if circle > 0:
    #         st.sidebar.markdown(f"   {idx} : {circle_indicators[circle]}")
