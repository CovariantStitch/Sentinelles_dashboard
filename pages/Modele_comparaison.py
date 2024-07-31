import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from common import get_data_from_api, labels
from models.SIR.SIR_model import adjust_single_sir, sir_equation
from models.gaussian_fit.gaussian_fits import adjust_single_gaussian, gaussian_equation
from sentinel_api import SentinelClient
from models.common import compute_rmse

# charge le client
client = SentinelClient()
diseases_list_with_regions = client.diseases_list_with_regions

disease = st.selectbox("Sélectionner une pathologie", diseases_list_with_regions)
df = get_data_from_api(client, disease, geo="PAY")

year = st.slider(label='Année', min_value=df["date"].min().year, max_value=df["date"].max().year, value=df["date"].min().year+1)

df = df[["date", "inc100"]]
start_date = datetime.datetime(year - 1, 9, 1)
end_date = datetime.datetime(year, 8, 31)
df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
df = df.drop_duplicates(subset="date", keep='first')


# interpolate data for everyday
date_range = pd.date_range(start=df['date'].min(), end=df['date'].max(), freq='D')
df_reindexed = df.set_index('date').reindex(date_range)
df_interpolated = df_reindexed.interpolate(method='polynomial', order=1)
df = df_interpolated.reset_index().rename(columns={'index': 'date'})

x_ = (df["date"] - df["date"].min()).dt.days
params_gaussian, _ = adjust_single_gaussian(x_.values, df["inc100"])
y_gaussian = gaussian_equation(x_, *params_gaussian)
df["gaussian"] = y_gaussian

params_sir = adjust_single_sir(x_, df["inc100"])
y_sir = sir_equation(np.linspace(0, 365, len(x_)), *params_sir[0])
df["sir"] = y_sir

fig = px.line(df, x="date", y=["inc100", "gaussian", "sir"], labels=labels)
fig.update_layout(legend_title_text="Type d'ajustement", yaxis_title="Incidence pour 100 000 personnes")
fig.for_each_trace(lambda t: t.update(name=labels.get(t.name, t.name)))

st.plotly_chart(fig)
col1, col2 = st.columns(2)
with col1:
    st.metric(f"RMSE gaussien : ", round(compute_rmse(df['inc100'], y_gaussian), 2))
with col2:
    st.metric(f"RMSE SIR : ", round(compute_rmse(df['inc100'], y_sir), 2))
