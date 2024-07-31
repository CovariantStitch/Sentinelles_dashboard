import requests
import pandas as pd
import os
import json
from ressources import region_mapping
import numpy as np
from info import path


class SentinelClient:
    def __init__(self):
        self.path = path
        self.url = "https://www.sentiweb.fr/api/v1/"

        self.indicators_list = pd.DataFrame(self.get_indicators_list())
        self.diseases_list_with_regions = [d["name"] for i, d in self.indicators_list.iterrows() if "RDD" in d["geo"]]

    def get_indicators_list(self):
        path = self.path / "saved_data" / "indicators_list.json"

        if not os.path.exists(path):
            url = self.url + "datasets/rest/indicators"
            response = requests.request("GET", url)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(response.json(), f)
            return response.json()
        else:
            with open(path, 'r', encoding="utf-8") as f:
                data = json.load(f)
            return data

    def get_incidence(self, id_pathologie: int, geo: str = "PAY") -> pd.DataFrame:
        # convert old regions to new regions
        if geo == "REG":
            geo = "RDD"

        # check that the geo is available
        pathologie = self.indicators_list[self.indicators_list["id"] == str(id_pathologie)]
        available_geo = pathologie["geo"].values[0]
        if geo not in available_geo:
            return pd.DataFrame()

        file_name = self.path / "saved_data" / f"indicator_{id_pathologie}_{geo}.csv"

        # first check if the file exist locally
        # todo: check that the file is up-to-date
        if os.path.exists(file_name):
            df = pd.read_csv(file_name, sep=";")
        # otherwise get the data from Sentiweb API
        else:
            url = self.url + f"datasets/rest/dataset?id=inc-{id_pathologie}-{geo}&span=all"
            response = requests.request("GET", url)
            try:
                data = response.json()["data"]
                df = pd.DataFrame(data)
                df.to_csv(file_name, sep=";", index=False)
            except KeyError:
                df = pd.DataFrame()
                return df

        # convert week or year to datetime
        if "week" in df.columns:
            df["date"] = pd.to_datetime(df["week"].map(lambda d: str(d) + '-0'), format="%Y%W-%w")
        elif "year" in df.columns:
            df["date"] = pd.to_datetime(df["year"].map(lambda d: str(d) + '0101'), format="%Y%m%d")
        else:
            df["date"] = pd.to_datetime(df["month"].map(lambda d: str(d) + '01'), format="%Y%m%d")
        return df
