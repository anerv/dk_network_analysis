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
plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

# %%
#### CORRELATION BETWEEN SOCIO-ECO VARIABLES ####

socio = gpd.read_postgis("SELECT * FROM socio", engine, geom_col="geometry")

rename_dict = {
    "households_income_under_100k_share": "Income under 100k",
    "households_income_100_150k_share": "Income 100-150k",
    "households_income_150_200k_share": "Income 150-200k",
    "households_income_200_300k_share": "Income 200-300k",
    "households_income_300_400k_share": "Income 300-400k",
    "households_income_400_500k_share": "Income 400-500k",
    "households_income_500_750k_share": "Income 500-750k",
    "households_income_750k_share": "Income 750k",
    "households_with_car_share": "Households w car",
    "households_1car_share": "Households 1 car",
    "households_2cars_share": "Households 2 cars",
    "households_nocar_share": "Households no car",
}

socio.rename(columns=rename_dict, inplace=True)

socio_corr_variables = [
    "Income under 100k",
    "Income 100-150k",
    "Income 150-200k",
    "Income 200-300k",
    "Income 300-400k",
    "Income 400-500k",
    "Income 500-750k",
    "Income 750k",
    "Households w car",
    "Households 1 car",
    "Households 2 cars",
    "Households no car",
    "population_density",
    "urban_pct",
]

keep_columns = socio_corr_variables + ["id"]

socio = socio[keep_columns]

plot_func.plot_correlation(
    socio,
    socio_corr_variables,
    heatmap_fp="../results/socio_correlation/heatmap_socio_vars.png",
    pairplot_fp="../results/socio_correlation/pairplot_socio_vars.png",
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
# socio.drop(columns=["geometry", "area_name"], inplace=True)

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
for i, columns in enumerate(all_density_columns):

    corr_columns = socio_corr_variables + columns

    plot_func.plot_correlation(
        socio_density,
        corr_columns,
        heatmap_fp=f"../results/socio_correlation/heatmap_socio_{labels[i]}.png",
        pairplot_fp=f"../results/socio_correlation/pairplot_socio_{labels[i]}.png",
    )

# %%
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

keep_columns = socio_largest_component_columns + ["id"]
socio_components = socio_components.merge(
    socio_largest_components[keep_columns], on="id", how="inner"
)


all_fragmentation_columns = [
    component_count_columns,
    component_per_km_columns,
    socio_largest_component_columns,
]

labels = [
    "component_count",
    "component_per_km",
    "largest_local_component",
]

# %%
for i, columns in enumerate(all_fragmentation_columns):

    corr_columns = socio_corr_variables + columns

    plot_func.plot_correlation(
        socio_components,
        corr_columns,
        pair_plot_x_log=True,
        pair_plot_y_log=True,
        heatmap_fp=f"../results/socio_correlation/heatmap_socio_{labels[i]}.png",
        pairplot_fp=f"../results/socio_correlation/pairplot_socio_{labels[i]}.png",
    )

# %%
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
for i, columns in enumerate(all_reach_columns):

    corr_columns = socio_corr_variables + columns

    plot_correlation(
        socio_reach,
        corr_columns,
        heatmap_fp=f"../results/socio_correlation/heatmap_socio_{labels[i]}.png",
        pairplot_fp=f"../results/socio_correlation/pairplot_socio_{labels[i]}.png",
    )

# %%

for i, columns in enumerate(all_reach_columns):
    display(
        socio_reach[columns]
        .corr(method="spearman")
        .style.background_gradient(cmap="coolwarm")
    )
    display(socio_reach[columns].describe())

# %%
