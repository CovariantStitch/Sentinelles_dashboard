import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
from sentinel_api import SentinelClient
from tqdm import tqdm

with open("./neighbours.json", 'r', encoding='utf-8') as f:
    dict_neighbours = json.load(f)

client = SentinelClient()
df = client.get_incidence(id_pathologie=3, geo="RDD")
df = df[df["geo_insee"].isin(list(map(int, dict_neighbours.keys())))]
df["inc_voisin"] = 0.
for i, data in tqdm(df.iterrows(), total=len(df)):
    neighbours = dict_neighbours[str(data["geo_insee"])]
    df_ = df[df["week"] == data["week"]]
    df_ = df_[df_["geo_insee"].isin(neighbours)]
    df.loc[i, "inc_voisin"] = df_["inc"].sum()

fig, ax = plt.subplots()
ax.scatter(df["inc_voisin"], df["inc"])
fig.tight_layout()
plt.show()
