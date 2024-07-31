import datetime
import os.path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from common import get_data_from_api, add_double_divider
from info import path
from models.gaussian_fit.gaussian_fits import start_gaussian_fit
from sentinel_api import SentinelClient


def plot_correlations(df):
    # correlations
    df_pivot = df.pivot_table(index='date', columns='geo_name', values='inc')
    correlation_matrix = df_pivot.corr()
    fig = px.imshow(correlation_matrix[correlation_matrix > 0.8], aspect="auto",
                    labels={"geo_name": "région", "color": "corrélation"}, width=700, height=500,
                    title="Matrice de corrélations entre régions."
                          "Donnes des informations sur la propagation des épidémies entre régions")
    fig.update_layout(xaxis=dict(showticklabels=False, title="Région"),
                      yaxis=dict(title="Région"))
    st.plotly_chart(fig, use_container_width=True)


def plot_per_year_per_region():
    # charge les données
    df = get_data_from_api(client, disease, geo="RDD")
    df["year"] = df["date"].dt.year
    aggregated_region_year = df.groupby(['geo_name', 'year'])['inc100'].sum().reset_index()

    fig = px.line(aggregated_region_year, "year", "inc100", line_group="geo_name", color="geo_name",
                  labels={"inc%": "Incidence (pour 100 000 personnes)",
                          "year": "Année", "geo_name": "région"}, title="Incidence par an et par région")
    st.plotly_chart(fig)

    # plot_correlations(df)


def plot_gaussian_fits_PAY(id_pathologie):
    file_path = path / "models" / "gaussian_fit" / f"gaussian_fit_{id_pathologie}_inc100_PAY.csv"
    if not os.path.exists(file_path):
        start_gaussian_fit(id_pathologie, "inc100", "PAY")
    df_fit = pd.read_csv(file_path, sep=";")
    df_fit["mu"] = df_fit["mu"].apply(
        lambda x: (datetime.datetime(2000, 9, 1) + datetime.timedelta(days=x)).timetuple().tm_yday)
    df_fit["mu"] = df_fit["mu"].apply(lambda x: x - 366 if x > 280 else x)
    df_fit["tot"] = df_fit["alpha"] * df_fit["sigma"] * np.sqrt(2 * np.pi)
    df_fit["d_tot"] = (df_fit["alpha"] + df_fit["d_alpha"]) * (df_fit["sigma"] - df_fit["d_sigma"]) * np.sqrt(
        2 * np.pi) - \
                      df_fit["tot"]
    labels = {"mu": "Date moyenne du pic épidémique (à partir du 1er janvier)", "geo_name": "Régions",
              "sigma": "Durée moyenne de l'épidémie (jours)", "alpha": "Pic d'incidence (pour 100 000 personnes)",
              "period": "Périodes", "tot": "Nombre total de contaminations (pour 100 000 personnes)"}

    col1, col2, col3 = st.columns(3)
    with col1:
        fig = px.scatter(df_fit, x="year", y="alpha", error_y="d_alpha", labels=labels)
        st.plotly_chart(fig)
    with col2:
        fig = px.scatter(df_fit, x="year", y="mu", error_y="d_mu", labels=labels)
        st.plotly_chart(fig)
    with col3:
        fig = px.scatter(df_fit, x="year", y="sigma", error_y="d_sigma", labels=labels)
        st.plotly_chart(fig)


def plot_gaussian_fits_RDD(id_pathologie, years1, years2):
    file_path = path / "models" / "gaussian_fit" / f"gaussian_fit_{id_pathologie}_inc100_RDD.csv"
    if not os.path.exists(file_path):
        start_gaussian_fit(id_pathologie, "inc100", "RDD")
    df_fit = pd.read_csv(file_path, sep=";")
    df_fit["year2"] = df_fit["year"].apply(lambda x: int(x[:4]))
    df_fit["tot"] = df_fit["alpha"] * df_fit["sigma"] * np.sqrt(2 * np.pi)
    df_fit_mean = pd.DataFrame(
        columns=["geo_name", "geo_insee", "alpha", "mu", "sigma", "tot", "d_alpha", "d_mu", "d_sigma", "d_tot",
                 "period"])
    for i, years in enumerate([years1, years2]):
        df_fit_ = df_fit[(df_fit["year2"] > years[0]) & (df_fit["year2"] < years[1])]
        for region, df_ in df_fit_.groupby("geo_name"):
            if region == "CORSE":
                continue
            geo_insee = df_["geo_insee"].unique()[0]
            df_fit_mean.loc[len(df_fit_mean.index)] = [region, geo_insee, df_["alpha"].mean(), df_["mu"].mean(),
                                                       2 * df_["sigma"].mean(), df_["tot"].mean(),
                                                       df_["alpha"].sem(), df_["mu"].sem(), df_["sigma"].sem(),
                                                       df_["tot"].sem(), years]

    df_fit_mean["mu"] = df_fit_mean["mu"].apply(
        lambda x: (datetime.datetime(2000, 9, 1) + datetime.timedelta(days=x)).timetuple().tm_yday)
    labels = {"mu": "Date moyenne du pic épidémique (à partir du 1er janvier)", "geo_name": "Régions",
              "sigma": "Durée moyenne de l'épidémie (jours)", "alpha": "Pic d'incidence (pour 100 000 personnes)",
              "tot": "Incidence totale (pour 100 000 personnes)"}

    col1, col2, col3 = st.columns(3)
    with col1:
        fig = px.scatter(df_fit_mean, x="geo_name", y="alpha", error_y="d_alpha", labels=labels, color="period",
                         symbol="period")
        st.plotly_chart(fig)
    with col2:
        fig = px.scatter(df_fit_mean, x="geo_name", y="mu", error_y="d_mu", labels=labels, color="period",
                         symbol="period")
        st.plotly_chart(fig)
    with col3:
        fig = px.scatter(df_fit_mean, x="geo_name", y="sigma", error_y="d_sigma", labels=labels, color="period",
                         symbol="period")
        st.plotly_chart(fig)


st.sidebar.header("Analyse gaussienne")

add_double_divider("Méthodologie")
# explications
st.markdown("""
Une analyse simple est ici proposée pour les pathologies saisonnières.
Un ajustement gaussien est effectué par année et par région. Les paramètres ajustés sont :
- le pic épidémiologique, qui donne des informations sur le nombre maximum de contaminations
- la date du pic épidémiologique, qui donne des informations sur la temporalité
- la largeur du pic épidémiologique, qui représente la durée de l'épidémie
""")

# charge le client
client = SentinelClient()
diseases_list_with_regions = client.diseases_list_with_regions

disease = st.selectbox("Sélectionner une pathologie", diseases_list_with_regions)
indicators = client.indicators_list
id_pathologie = indicators[indicators["name"] == disease]["id"].values[0]

add_double_divider("Statistiques à l'échelle nationale")
plot_gaussian_fits_PAY(id_pathologie)
# plot_epidemic_length()

add_double_divider("Statistiques à l'échelle régionale")
plot_per_year_per_region()

add_double_divider("Evolution des paramètres pour deux périodes")
col1, col2 = st.columns(2)
with col1:
    year_slider1 = st.slider(label="Première période", min_value=1980, max_value=2024, value=[1980, 2000], key=0)
with col2:
    year_slider2 = st.slider(label="Seconde période", min_value=1980, max_value=2024, value=[2005, 2024], key=1)
plot_gaussian_fits_RDD(id_pathologie, year_slider1, year_slider2)
