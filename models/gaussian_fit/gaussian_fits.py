import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.optimize import curve_fit

from info import path
from models.common import compute_rrmse, split_years
from sentinel_api import SentinelClient


def gaussian_equation(x, a, mu, sigma):
    return a * np.exp(-np.power(x - mu, 2) / 2 / np.power(sigma, 2))


def adjust_single_gaussian(x, y):
    res = curve_fit(gaussian_equation, x, y, p0=[y.max(), x[np.argmax(y)], 50],
                    bounds=[[0, 0, 0], [np.inf, 365, 100]])
    params, pcov = res[0:2]
    return params, pcov


def start_gaussian_fit(id_pathologie, observable="inc100", geo="RDD", save=True):
    client = SentinelClient()
    df = client.get_incidence(id_pathologie=id_pathologie, geo=geo)
    df["year"] = df["date"].dt.year

    df_fit = pd.DataFrame(columns=["geo_insee", "geo_name", "year", "rrmse", "alpha", "mu", "sigma",
                                   "d_alpha", "d_mu", "d_sigma"])

    if geo == "RDD":

        df_sub = split_years(df)

        for year, df_ in df_sub.items():
            print(year)
            for code in df_["geo_insee"].unique():
                df__ = df_[df_["geo_insee"] == code]
                y = df__[observable]
                x = (df__["date"] - df__["date"].min()).dt.days

                params, pcov = adjust_single_gaussian(x.values, y.values)
                y_ = gaussian_equation(x, *params)
                rrmse = compute_rrmse(y, y_)
                df_fit.loc[len(df_fit.index)] = [df__["geo_insee"].unique()[0], df__["geo_name"].unique()[0], year,
                                                 rrmse,
                                                 *params, *np.sqrt(np.diag(pcov))]
    elif geo == "PAY":
        df_sub = split_years(df)
        for year, df_ in df_sub.items():
            y = df_[observable]
            x = (df_["date"] - df_["date"].min()).dt.days
            params, pcov = adjust_single_gaussian(x.values, y.values)
            y_ = gaussian_equation(x, *params)
            rrmse = compute_rrmse(y, y_)
            df_fit.loc[len(df_fit.index)] = [0, "FRANCE", year, rrmse, *params, *np.sqrt(np.diag(pcov))]

    if save:
        df_fit.to_csv(path / "models" / "gaussian_fit" / f"gaussian_fit_{id_pathologie}_{observable}_{geo}.csv",
                      sep=";", index=False)


if __name__ == "__main__":
    id_pathologie = 25
    observable = "inc100"
    geo = "RDD"

    compute = 1
    if compute:
        start_gaussian_fit(id_pathologie, observable, geo)
    df_fit = pd.read_csv(f"./gaussian_fit_{id_pathologie}_{observable}_{geo}.csv", sep=";")

    fig, ax = plt.subplots()
    ax = sns.pointplot(df_fit, x="geo_name", y="rrmse", ax=ax, errorbar="se")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30)
    fig.tight_layout()

    fig, ax = plt.subplots()
    ax = sns.pointplot(df_fit, x="geo_name", y="mu", ax=ax, errorbar="se")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30)
    fig.tight_layout()

    fig, ax = plt.subplots()
    ax = sns.pointplot(df_fit, x="geo_name", y="sigma", ax=ax, errorbar="se")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30)
    fig.tight_layout()

    plt.show()
