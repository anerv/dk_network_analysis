# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
import geopandas as gpd
import numpy as np
import seaborn as sns

# sns.set_theme("paper")

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

# %%
# PLOT MUNI DENSITY

density_muni = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM density_municipality;",
    engine,
    crs=crs,
    geom_col="geometry",
)
density_muni.replace(0, np.nan, inplace=True)

# %%
# Individual LTS density

plot_cols = [
    "lts_1_dens",
    "lts_2_dens",
    "lts_3_dens",
    "lts_4_dens",
    "total_car_dens",
    "total_network_dens",
]
labels = ["LTS 1", "LTS 2", "LTS 3", "LTS 4", "Total car", "Total network"]
plot_titles = [f"Municipal network density for: {l}" for l in labels]
filepaths = [f"../results/network_density/administrative/{l}" for l in labels]

for i, p in enumerate(plot_cols):

    plot_func.plot_classified_poly(
        gdf=density_muni,
        plot_col=p,
        scheme="quantiles",
        cx_tile=cx_tile_2,
        plot_na=True,
        cmap=pdict["pos"],
        edgecolor="none",
        title=plot_titles[i],
        fp=filepaths[i],
    )

# %%
# Stepwise density
plot_cols = [
    "lts_1_dens",
    "lts_1_2_dens",
    "lts_1_3_dens",
    "lts_1_4_dens",
    "total_car_dens",
    "total_network_dens",
]
labels = ["LTS 1", "LTS 1-2", "LTS 1-3", "LTS 1-4", "Total car", "Total network"]
plot_titles = [f"Municipal network density for: {l}" for l in labels]
filepaths = [f"../results/network_density/administrative/{l}" for l in labels]

for i, p in enumerate(plot_cols):

    plot_func.plot_classified_poly(
        gdf=density_muni,
        plot_col=p,
        scheme="quantiles",
        cx_tile=cx_tile_2,
        plot_na=True,
        cmap=pdict["pos"],
        edgecolor="none",
        title=plot_titles[i],
        fp=filepaths[i],
    )

# %%

# Relative network length
plot_cols = [
    "lts_1_length_rel",
    "lts_1_2_length_rel",
    "lts_1_3_length_rel",
    "lts_1_4_length_rel",
    "lts_7_length_rel",
    # "total_car_length_rel",
]
for p in plot_cols:
    density_muni[p] = density_muni[p] * 100

labels = [
    "LTS 1 (%)",
    "LTS 1-2 (%)",
    "LTS 1-3 (%)",
    "LTS 1-4 (%)",
    "No biking (%)",
    # "Total car (%)",
]

plot_titles = [f"Municipal network length for: {l}" for l in labels]
filepaths = [f"../results/network_density/administrative/{l}" for l in labels]

for i, p in enumerate(plot_cols):

    plot_func.plot_classified_poly(
        gdf=density_muni,
        plot_col=p,
        scheme="quantiles",
        cx_tile=cx_tile_2,
        plot_na=True,
        cmap=pdict["pos"],
        edgecolor="none",
        title=plot_titles[i],
        fp=filepaths[i],
    )
# %%
# SOCIO
# Individual LTS density
density_socio = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM density_socio;",
    engine,
    crs=crs,
    geom_col="geometry",
)

density_socio.replace(0, np.nan, inplace=True)

plot_cols = [
    "lts_1_dens",
    "lts_2_dens",
    "lts_3_dens",
    "lts_4_dens",
    "total_car_dens",
    "total_network_dens",
]
labels = ["LTS 1", "LTS 2", "LTS 3", "LTS 4", "Total car", "Total network"]
plot_titles = [f"Socio network density for: {l}" for l in labels]
filepaths = [f"../results/network_density/socio/{l}" for l in labels]

for i, p in enumerate(plot_cols):

    plot_func.plot_classified_poly(
        gdf=density_socio,
        plot_col=p,
        scheme="quantiles",
        cx_tile=cx_tile_2,
        plot_na=True,
        cmap=pdict["pos"],
        edgecolor="none",
        title=plot_titles[i],
        fp=filepaths[i],
    )

# Stepwise density
plot_cols = [
    "lts_1_dens",
    "lts_1_2_dens",
    "lts_1_3_dens",
    "lts_1_4_dens",
    "total_car_dens",
    "total_network_dens",
]
labels = ["LTS 1", "LTS 1-2", "LTS 1-3", "LTS 1-4", "Total car", "Total network"]
plot_titles = [f"Socio network density for: {l}" for l in labels]
filepaths = [f"../results/network_density/socio/{l}" for l in labels]

for i, p in enumerate(plot_cols):

    plot_func.plot_classified_poly(
        gdf=density_socio,
        plot_col=p,
        scheme="quantiles",
        cx_tile=cx_tile_2,
        plot_na=True,
        cmap=pdict["pos"],
        edgecolor="none",
        title=plot_titles[i],
        fp=filepaths[i],
    )

# Relative network length
plot_cols = [
    "lts_1_length_rel",
    "lts_1_2_length_rel",
    "lts_1_3_length_rel",
    "lts_1_4_length_rel",
    "lts_7_length_rel",
    # "total_car_length_rel",
]
for p in plot_cols:
    density_socio[p] = density_socio[p] * 100

labels = [
    "LTS 1 (%)",
    "LTS 1-2 (%)",
    "LTS 1-3 (%)",
    "LTS 1-4 (%)",
    "No biking (%)",
    # "Total car (%)",
]

plot_titles = [f"Socio network length for: {l}" for l in labels]
filepaths = [f"../results/network_density/socio/{l}" for l in labels]

for i, p in enumerate(plot_cols):

    plot_func.plot_classified_poly(
        gdf=density_socio,
        plot_col=p,
        scheme="quantiles",
        cx_tile=cx_tile_2,
        plot_na=True,
        cmap=pdict["pos"],
        edgecolor="none",
        title=plot_titles[i],
        fp=filepaths[i],
    )

# %%
# H3

density_h3 = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM density_h3;",
    engine,
    crs=crs,
    geom_col="geometry",
)

density_h3.replace(0, np.nan, inplace=True)

# %%

plot_cols = [
    "lts_1_dens",
    "lts_2_dens",
    "lts_3_dens",
    "lts_4_dens",
    "total_car_dens",
    "total_network_dens",
]
labels = ["LTS 1", "LTS 2", "LTS 3", "LTS 4", "Total car", "Total network"]
plot_titles = [f"Local network density for: {l}" for l in labels]
filepaths = [f"../results/network_density/administrative/{l}.png" for l in labels]


for i, p in enumerate(plot_cols):

    plot_func.plot_classified_poly(
        gdf=density_h3,
        plot_col=p,
        scheme="quantiles",
        cx_tile=cx_tile_2,
        plot_na=False,
        cmap=pdict["pos"],
        edgecolor="none",
        title=plot_titles[i],
        fp=filepaths[i],
    )

# %%
# Stepwise density
plot_cols = [
    "lts_1_dens",
    "lts_1_2_dens",
    "lts_1_3_dens",
    "lts_1_4_dens",
    "total_car_dens",
    "total_network_dens",
]
labels = ["LTS 1", "LTS 1-2", "LTS 1-3", "LTS 1-4", "Total car", "Total network"]
plot_titles = [f"Local network density for: {l}" for l in labels]
filepaths = [f"../results/network_density/administrative/{l}.png" for l in labels]

for i, p in enumerate(plot_cols):

    plot_func.plot_classified_poly(
        gdf=density_h3,
        plot_col=p,
        scheme="quantiles",
        cx_tile=cx_tile_2,
        plot_na=True,
        cmap=pdict["pos"],
        edgecolor="none",
        title=plot_titles[i],
        fp=filepaths[i],
    )

# %%
# Relative network length
plot_cols = [
    "lts_1_length_rel",
    "lts_1_2_length_rel",
    "lts_1_3_length_rel",
    "lts_1_4_length_rel",
    "lts_7_length_rel",
    # "total_car_length_rel",
]
for p in plot_cols:
    density_h3[p] = density_h3[p] * 100

labels = [
    "LTS 1 (%)",
    "LTS 1-2 (%)",
    "LTS 1-3 (%)",
    "LTS 1-4 (%)",
    "No biking (%)",
    # "Total car (%)",
]

plot_titles = [f"Local network length for: {l}" for l in labels]
filepaths = [f"../results/network_density/administrative/{l}.png" for l in labels]


for i, p in enumerate(plot_cols):

    plot_func.plot_classified_poly(
        gdf=density_h3,
        plot_col=p,
        scheme="quantiles",
        cx_tile=cx_tile_2,
        plot_na=True,
        cmap=pdict["pos"],
        edgecolor="none",
        title=plot_titles[i],
        fp=filepaths[i],
    )

# %%
# TODO: Plot distribution of network densities for each lts

# TODO: Make distribution plots of each LTS combined and for each aggregation level

# TODO: make dataframe with lts in one col and network length in another

# transpose?

sns.displot(density_muni, x="network_length", hue="lts", kind="kde", multiple="stack")
# %%
sns.displot(density_muni, x="lts_1_dens", kde=True)

# %%

sns.histplot(density_muni, x="lts_1_dens", kde=True)

import seaborn as sns
import plotly.express as px

# %%

# TODO Make plotly express violin plot of density for each LTS
