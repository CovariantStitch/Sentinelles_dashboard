import plotly.express as px

from common import load_population, load_shapefile


def plot_map(df_reg, y="inc100", width=800, height=500, range_color=None):
    population = load_population()
    sf = load_shapefile()
    sf_ = sf.merge(df_reg, left_on="code", right_on="geo_insee")
    sf_ = sf_.merge(population, left_on="code", right_on="code")

    fig_map = px.choropleth(
        sf_,
        geojson=sf_['geometry'],
        locations=sf_.index,
        color=y,  # Colonne des valeurs à afficher
        scope="europe",
        width=width, height=height,
        hover_name="geo_name",
        hover_data="geo_insee",
        labels={"inc100": "Incidence (pour 100 000 personnes)", },
        color_continuous_scale="Bluered",
        range_color=range_color
    )
    fig_map.update_geos(fitbounds="locations", visible=False)

    return fig_map
