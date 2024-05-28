# %%

from src import db_functions as dbf
from src import plotting_functions as plot_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly_express as px
import pandas as pd

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)
# %%

# Load socio density data
socio = gpd.read_postgis("SELECT * FROM socio", engine, geom_col="geometry")
socio_density = gpd.read_postgis(
    "SELECT * FROM density.density_socio", engine, geom_col="geometry"
)

socio.dropna(subset=["population_density"], inplace=True)
socio.drop(columns=["geometry", "area_name"], inplace=True)

socio_density = socio_density.merge(socio, on="id", how="inner")

assert socio_density.shape[0] == socio.shape[0]
# %%

###### NETWORK DENSITY AND POP DENSITY ######

all_density_columns = [
    # length_columns,
    # length_steps_columns,
    density_columns,
    density_steps_columns,
    length_relative_columns,
    length_relative_steps_columns,
]

for columns in all_density_columns:

    fig, axs = plt.subplots(2, 3, figsize=(15, 10))

    axs = axs.flatten()

    if len(axs) > len(columns):
        axs[-1].set_visible(False)  # to remove last plot

    for ax, col_name in zip(axs, columns):

        ax.scatter(socio_density["population_density"], socio_density[col_name])
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("population_density")
        ax.set_ylabel(col_name)

    fig.suptitle(f"Correlation between population and network density", fontsize=20)

    plt.tight_layout()

# %%
###### NETWORK DENSITY AND INCOME DENSITY ######

for columns in all_density_columns:

    fig, axs = plt.subplots(2, 3, figsize=(15, 10))

    axs = axs.flatten()

    if len(axs) > len(columns):
        axs[-1].set_visible(False)  # to remove last plot

    for ax, col_name in zip(axs, columns):

        ax.scatter(socio_density["population_density"], socio_density[col_name])
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("population_density")
        ax.set_ylabel(col_name)

    fig.suptitle(f"Correlation between population and network density", fontsize=20)

    plt.tight_layout()

# %%
###### NETWORK DENSITY AND CAR OWNERSHIP ######
for columns in all_density_columns:

    fig, axs = plt.subplots(2, 3, figsize=(15, 10))

    axs = axs.flatten()

    if len(axs) > len(columns):
        axs[-1].set_visible(False)  # to remove last plot

    for ax, col_name in zip(axs, columns):

        ax.scatter(socio_density["households_with_car_share"], socio_density[col_name])
        # ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("share of households with car")
        ax.set_ylabel(col_name)

    fig.suptitle(f"Correlation between population and car ownership", fontsize=20)

    plt.tight_layout()

# %%


## CORR BETWEEN DENSITY AND POP

# Make small multiple plot with corr between pop density and all different density metrics (length ind an step, density, relative length etc.)

## CORR BETWEEN DENSITY AND car ownership

## CORR BETWEEN DENSITY AND income
