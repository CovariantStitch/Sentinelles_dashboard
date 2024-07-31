import numpy as np
from sentinel_api import SentinelClient
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from scipy.optimize import curve_fit
from models.common import split_years, compute_rrmse
from scipy.interpolate import interp1d
import pandas as pd
from info import path


def eq_system(y, t, beta, gamma, t0):
    if t < t0:
        return [0, 0, 0]
    s, i, r = y
    ds = - beta * s * i
    di = + beta * s * i - gamma * i
    dr = gamma * i
    return [ds, di, dr]

def sir_equation(x, beta, gamma, t0, n):
    res = odeint(eq_system, y0 = [100000, 10, 0], t=x, args = (beta, gamma, t0))
    i = res.T[1]
    i *= n / i.max()
    return i


def adjust_single_sir(x_, y_):
    p0_ = [5e-5, 0.8, x_[np.argmax(y_)], y_.max() // 2]
    res = curve_fit(sir_equation, xdata=x_, ydata=y_, p0=p0_, bounds=[[0, 0, 0, 10], [1, 10, len(y_), 1e5]])
    params_, pcov_ = res[:2]
    return params_, pcov_


if __name__ == "__main__":
    client = SentinelClient()
    df = client.get_incidence(id_pathologie=3, geo="PAY")
    df = df[["date", "inc100"]]
    df = df.drop_duplicates(subset="date", keep='first')
    df_sub = split_years(df)
    a = 0
    plot = False
    results = []
    for years in df_sub.keys():
        print(years)
        date_range = pd.date_range(start=df_sub[years]['date'].min(), end=df_sub[years]['date'].max(), freq='D')
        df_reindexed = df_sub[years].set_index('date').reindex(date_range)
        df_interpolated = df_reindexed.interpolate(method='linear')
        df_interpolated = df_interpolated.reset_index().rename(columns={'index': 'date'})

        y = df_interpolated["inc100"]
        x = np.linspace(0, 365, len(y))
        params = adjust_single_sir(x, y)
        beta, gamma, t0, n = params[0]
        y_model = sir_equation(x, *params[0])
        rrmse = compute_rrmse(y, y_model)
        results.append(np.array([beta, gamma, t0, n, rrmse]))

        if plot or rrmse > 2:
            print(params)
            fig, ax = plt.subplots()
            ax.plot(x, y_model, label="Model")
            ax.plot(x, y, label="Data")
            ax.legend()
            fig.tight_layout()
            plt.show()

    results = np.array(results)
    fig, ax = plt.subplots(2, 2)
    for i in range(4):
        pos = (i//2, i%2)
        ax[pos].scatter(df_sub.keys(), results.T[i])
    fig.tight_layout()

    fig, ax = plt.subplots()
    df = pd.read_csv(path / "models" / "gaussian_fit" / "gaussian_fit_3_inc100_PAY.csv", sep=";")
    ax.scatter(df_sub.keys(), results.T[-1], color='tab:blue')
    ax.scatter(df["year"], df["rrmse"], color='tab:red')
    print(f"RRMSE moyenne SIR      : {results.T[-1].mean()}")
    print(f"RRMSE moyenne GAUSSIAN : {df['rrmse'].mean()}")

    plt.show()
