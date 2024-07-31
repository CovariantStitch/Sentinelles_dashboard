import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from common import get_data_from_api, add_double_divider, labels
from common_plots import plot_map
from sentinel_api import SentinelClient


def plot_simple(df: pd.DataFrame, x, y='inc', line_group=None, title='Incidence dans le temps', labels=labels):
    fig = px.line(df, x=x, y=y, title=title, line_group=line_group, hover_name=line_group, color=line_group,
                  labels=labels)
    return fig


# load diseases
client = SentinelClient()
disease_list = client.indicators_list["name"]

disease = st.selectbox("Sélectionner une pathologie", disease_list, index=2)

add_double_divider("Explorer les données historiques pour différentes pathologies")

# graph units
unite = st.radio(
    "Unité",
    ["Incidence totale", "Incidence pour 100 000 habitants"]
)

# get API data at national level
df = get_data_from_api(client, disease, geo="PAY")

# plot the time evolution
if unite == "Incidence totale":
    fig = plot_simple(df, x="date", y="inc")
else:
    fig = plot_simple(df, x="date", y="inc100")
st.plotly_chart(fig)

# try to get the regional data
df_reg = get_data_from_api(client, disease, geo="RDD")

add_double_divider("Explorer les données à l'échelle régionale")

if df_reg.empty or "week" not in df_reg.columns:
    st.write(f"Aucune donnée disponible au niveau régional pour {disease}")
else:
    col1, col2 = st.columns([0.5, 0.5])
    with col1:
        year_map = st.number_input(label='Année', min_value=1980, max_value=2024, value=2022)
        list_dates = df_reg[df_reg["date"].dt.year == year_map]["date"].to_list()

        fig = plot_simple(df_reg[df_reg["date"].dt.year == year_map], "date", y="inc100", line_group="geo_name",
                          title="Incidence dans les différentes régions (pour 100 000)")
        fig.update_layout(legend=dict(orientation="h", y=-0.2, valign="middle", title_text="Régions"))
        st.plotly_chart(fig)

    with col2:
        week_slider = st.slider(label="Faites glisser pour faire évoluer la carte",
                                min_value=min(list_dates).to_pydatetime(),
                                max_value=max(list_dates).to_pydatetime(),
                                value=min(list_dates).to_pydatetime(),
                                step=datetime.timedelta(days=7))
        df_reg = df_reg[df_reg["date"] == week_slider]

        if "fig_map" not in st.session_state:
            fig_map = plot_map(df_reg)
            fig_map.update_layout(title=f'Données pour {week_slider.strftime("%d %B, %Y")}')
            fig_map.update_geos(fitbounds="locations", visible=False)

            map_placeholder = st.plotly_chart(fig_map)
            st.session_state.fig_map = fig_map
        else:
            st.session_state.fig_map.data[0].z = df_reg["inc100"]
            st.session_state.fig_map.update_layout(title_text=f'Données pour {week_slider.strftime("%d %B, %Y")}')
            st.plotly_chart(st.session_state.fig_map)
