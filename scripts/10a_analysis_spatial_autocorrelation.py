# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
from src import analysis_functions as analysis_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# import plotly_express as px

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

# %%

# ANALYSE CLUSTERING OFF:

# Global Moran's I

### DENSITY ###

## AT EACH AGGREGATION LEVEL:
# Density of each LTS type #OK
# Density of LTS stepwise # OK
# Share of each LTS type
# Share of LTS stepwise


# TODO: Store results: Moran's I for each type of spatial weight and result
# TODO: For LISA, join the value to the spatial unit, p-value, spatial weight type, and cluster type
# TODO: Sensitivity analysis: Test with different types of spatial weights to see if results change


# VIZ + EXPORT VALUES
# %%
### READ DATA ###
density_muni = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM density.density_municipality;",
    engine,
    crs=crs,
    geom_col="geometry",
)
# density_muni.replace(0, np.nan, inplace=True)

density_socio = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM density.density_socio;",
    engine,
    crs=crs,
    geom_col="geometry",
)

# density_socio.replace(0, np.nan, inplace=True)

density_hex = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM density.density_hex;",
    engine,
    crs=crs,
    geom_col="geometry",
)

# density_hex.replace(0, np.nan, inplace=True)

gdfs = [density_muni, density_socio, density_hex]

for gdf in gdfs:

    for p in length_relative_columns:
        gdf[p] = gdf[p] * 100

    for p in length_relative_steps_columns[1:-1]:
        gdf[p] = gdf[p] * 100

# %%
# Define K values for spatial weights
k_muni = 3
k_socio = 8
k_hex = 18
p = 0.05

w_muni = analysis_func.compute_spatial_weights(
    density_muni, "municipality", w_type="knn", dist=k_muni  # "knn", k=k_muni
)

w_socio = analysis_func.compute_spatial_weights(
    density_socio, "id", w_type="knn", k=k_socio
)

w_grid = analysis_func.compute_spatial_weights(
    density_hex, "id", w_type="knn", k=k_socio
)


# %%
# TODO: do for all aggregation levels

for i, gdf in enumerate(gdfs):

    global_morans_results = {}

    columns = density_columns

    # variable_names = [
    #     "LTS 1 density",
    #     "LTS 2 density",
    #     "LTS 3 density",
    #     "LTS 4 density",
    #     "car density",
    #     "total network density",
    # ]

    filepaths = [
        f"../results/spatial_autocorrelation/density/{v}.png".replace(" ", "_")
        for v in variable_names
    ]

    morans_results = analysis_func.compute_spatial_autocorrelation(
        columns, columns, density_muni, w_muni, filepaths
    )

    lisa_results = analysis_func.compute_lisa(
        columns, columns, density_muni, w_muni, filepaths
    )

    for key, value in morans_results.items():
        global_morans_results[key] = value.I

# %%
columns = density_steps_columns[1:-2]

variable_names = [
    # "LTS 1 density",
    "LTS 1-2 density",
    "LTS 1-3 density",
    "LTS 1-4 density",
    # "car density",
    # "total network density",
]

filepaths = [
    f"../results/spatial_autocorrelation/density/{v}.png".replace(" ", "_")
    for v in variable_names
]

# TODO: Store results, convert to table

morans_density_steps_muni = analysis_func.compute_spatial_autocorrelation(
    columns, variable_names, density_muni, w_muni, filepaths
)

# TODO: Store results, convert to table

columns = length_relative_columns

variable_names = [
    "LTS 1%",
    "LTS 2%",
    "LTS 3%",
    "LTS 4%",
    "car%",
]

filepaths = [
    f"../results/spatial_autocorrelation/density/{v}.png".replace(" ", "_")
    for v in variable_names
]

morans_density_muni = analysis_func.compute_spatial_autocorrelation(
    columns, variable_names, density_muni, w_muni, filepaths
)


columns = length_relative_steps_columns[1:-1]
variable_names = ["LTS 1-2%", "LTS 1-3%", "LTS 1-4%"]

filepaths = [
    f"../results/spatial_autocorrelation/density/{v}.png".replace(" ", "_")
    for v in variable_names
]

morans_density_muni = analysis_func.compute_spatial_autocorrelation(
    columns, variable_names, density_muni, w_muni, filepaths
)

# TODO: Store results, convert to table

# TODO: INCORPORATE LISA
# %%

filepaths = [
    f"../results/spatial_autocorrelation/density/{v}.png".replace(" ", "_")
    for v in variable_names
]

variable_names = [
    "LTS 1 density",
    "LTS 2 density",
    "LTS 3 density",
    "LTS 4 density",
    "car density",
    "total network density",
]

lisas_density = analysis_func.compute_lisa(
    density_columns, variable_names, density_muni, w_muni, filepaths, p=p
)

# %%
### FRAGMENTATION ###

## AT EACH AGGREGATION LEVEL:
# Component count of each LTS type
# Comp per km
# Comp per sqkm

### REACH #####

## Only at hex level
# Reach of each LTS step
# Diff in reach
