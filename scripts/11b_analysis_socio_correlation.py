# %%

from src import db_functions as dbf
from src import plotting_functions as plot_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly_express as px
import pandas as pd
import seaborn as sns

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/df_styler.py").read())
exec(open("../settings/filepaths.py").read())
plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

# %%
###### SOCIO-ECO VARIABLES #####
################################

exec(open("../settings/read_socio_pop.py").read())

plot_func.plot_correlation(
    socio,
    socio_corr_variables,
    heatmap_fp=fp_socio_vars_heatmap,
    pairplot_fp=fp_socio_vars_pairplot,
)

display(socio[socio_corr_variables].corr().style.background_gradient(cmap="coolwarm"))
display(socio[socio_corr_variables].describe())

# %%
###### NETWORK DENSITY #########
################################

socio_density = gpd.read_postgis(
    "SELECT * FROM density.density_socio", engine, geom_col="geometry"
)

socio.dropna(subset=["population_density"], inplace=True)

socio_density = socio_density.merge(socio, on="id", how="inner")

assert socio_density.shape[0] == socio.shape[0]

all_density_columns = [
    # length_columns,
    # length_steps_columns,
    density_columns,
    density_steps_columns,
    length_relative_columns,
    length_relative_steps_columns,
]

labels = ["density", "density_steps", "length_relative", "length_relative_steps"]
# %%
# Density plot correlation
for i, columns in enumerate(all_density_columns):

    corr_columns = socio_corr_variables + columns

    plot_func.plot_correlation(
        socio_density,
        corr_columns,
        heatmap_fp=fp_socio_heatmap + f"{labels[i]}.png",
        pairplot_fp=fp_socio_pairplot + f"{labels[i]}.png",
    )

# %%
# Density display correlation
for i, columns in enumerate(all_density_columns):
    display(
        socio_density[columns]
        .corr(method="spearman")
        .style.background_gradient(cmap="coolwarm")
    )
    display(socio_density[columns].describe())
# %%
###### FRAGMENTATION ######
##########################

socio_components = gpd.read_postgis(
    "SELECT * FROM fragmentation.component_length_socio;", engine, geom_col="geometry"
)

socio_largest_components = gpd.read_postgis(
    "SELECT * FROM fragmentation.socio_largest_component;", engine, geom_col="geometry"
)

socio_components = socio_components[
    [
        "comp_all_count",
        "comp_1_count",
        "comp_2_count",
        "comp_3_count",
        "comp_4_count",
        "comp_car_count",
        "component_per_length_all",
        "component_per_length_1",
        "component_per_length_2",
        "component_per_length_3",
        "component_per_length_4",
        "component_per_length_car",
        "id",
    ]
].merge(socio, on="id", how="inner")

keep_columns = socio_largest_component_columns_ave + ["id"]
socio_components = socio_components.merge(
    socio_largest_components[keep_columns], on="id", how="inner"
)


all_fragmentation_columns = [
    component_count_columns,
    component_per_km_columns,
    socio_largest_component_columns_ave,
]

labels = [
    "component_count",
    "component_per_km",
    "largest_local_component",
]

# %%
# Fragmentation plot correlation
for i, columns in enumerate(all_fragmentation_columns):

    corr_columns = socio_corr_variables + columns

    plot_func.plot_correlation(
        socio_components,
        corr_columns,
        pair_plot_x_log=True,
        pair_plot_y_log=True,
        heatmap_fp=fp_socio_heatmap + f"{labels[i]}.png",
        pairplot_fp=fp_socio_pairplot + f"{labels[i]}.png",
    )

# %%
# Fragmentation display correlation
for i, columns in enumerate(all_fragmentation_columns):
    display(
        socio_components[columns]
        .corr(method="spearman")
        .style.background_gradient(cmap="coolwarm")
    )
    display(socio_components[columns].describe())

# %%
##### REACH ###########
######################

socio_reach = gpd.read_postgis(
    f"SELECT * FROM reach.socio_reach_{reach_dist}", engine, geom_col="geometry"
)

socio_reach = socio_reach.merge(socio, on="id", how="inner")

all_reach_columns = [
    socio_reach_average_columns,
    socio_reach_median_columns,
]

labels = [
    "average_reach",
    "median_reach",
]

# %%
# Reach plot correlation
for i, columns in enumerate(all_reach_columns):

    corr_columns = socio_corr_variables + columns

    plot_func.plot_correlation(
        socio_reach,
        corr_columns,
        heatmap_fp=fp_socio_heatmap + f"{labels[i]}.png",
        pairplot_fp=fp_socio_pairplot + f"{labels[i]}.png",
    )

# %%
# Reach display correlation
for i, columns in enumerate(all_reach_columns):
    display(
        socio_reach[columns]
        .corr(method="spearman")
        .style.background_gradient(cmap="coolwarm")
    )
    display(socio_reach[columns].describe())

# %%

# TODO: ALL NETWORK VARIABLES**
