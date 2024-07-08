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
from IPython.display import display

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
# %%
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
socio.drop(columns=["geometry"], inplace=True)

socio_density = socio_density.merge(socio, on="id", how="inner")

assert socio_density.shape[0] == socio.shape[0]
# %%
all_density_columns = [
    # length_columns,
    # length_steps_columns,
    density_columns,
    density_steps_columns,
    length_relative_columns,
    length_relative_steps_columns,
]

metric_labels = ["density", "density_steps", "length_relative", "length_relative_steps"]
# %%
# Density plot correlation
for i, columns in enumerate(all_density_columns):

    corr_columns = socio_corr_variables + columns

    plot_func.plot_correlation(
        socio_density,
        corr_columns,
        heatmap_fp=fp_socio_heatmap + f"{metric_labels[i]}.png",
        pairplot_fp=fp_socio_pairplot + f"{metric_labels[i]}.png",
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


# %% JUST POP DENSITY AND URB PCT

all_labels = [labels_all, labels_step_all, labels_pct, labels_pct_step]

axis_labels = ["km/sqkm", "km/sqkm", "%", "%"]

for i, columns in enumerate(all_density_columns[:-2]):

    for e, c in enumerate(columns):

        plt.figure(figsize=(8, 6))
        fig = sns.scatterplot(
            data=socio_density,
            x="population_density",
            y=c,
            hue="urban_pct",
        )
        fig.get_legend().set_title("Pct urban")
        plt.xscale("log")
        plt.xlabel("People per sqkm")
        plt.ylabel(all_labels[i][e] + " " + axis_labels[i])
        # plt.title()
        plt.savefig(fp_socio_pop_corr + f"{c}.png")
        plt.show()


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
    component_count_columns + component_per_km_columns + ["id"]
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

metric_labels = [
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
        heatmap_fp=fp_socio_heatmap + f"{metric_labels[i]}.png",
        pairplot_fp=fp_socio_pairplot + f"{metric_labels[i]}.png",
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
# %% JUST POP DENSITY AND URB PCT

all_labels = [labels_all, labels_step_all, labels_pct, labels_pct_step]

axis_labels = ["component count", "component per km", "ave size of largest component"]

for i, columns in enumerate(all_fragmentation_columns):

    for e, c in enumerate(columns):

        plt.figure(figsize=(8, 6))
        figg = sns.scatterplot(
            data=socio_components,
            x="population_density",
            y=c,
            hue="urban_pct",
        )
        figg.get_legend().set_title("Pct urban")
        plt.xscale("log")
        plt.xlabel("People per sqkm")
        plt.ylabel(all_labels[i][e] + " " + axis_labels[i])
        # plt.title()
        plt.savefig(fp_socio_pop_corr + f"{c}.png")
        plt.show()


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

metric_labels = [
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
        heatmap_fp=fp_socio_heatmap + f"{metric_labels[i]}.png",
        pairplot_fp=fp_socio_pairplot + f"{metric_labels[i]}.png",
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
all_labels = [labels_all, labels_step_all, labels_pct, labels_pct_step]

axis_labels = ["average reach (km)", "median reach (km)"]

for i, columns in enumerate(all_fragmentation_columns):

    for e, c in enumerate(columns):

        plt.figure(figsize=(8, 6))
        figg = sns.scatterplot(
            data=socio_reach,
            x="population_density",
            y=c,
            hue="urban_pct",
        )
        figg.get_legend().set_title("Pct urban")
        plt.xscale("log")
        plt.xlabel("People per sqkm")
        plt.ylabel(all_labels[i][e] + " " + axis_labels[i])
        # plt.title()
        plt.savefig(fp_socio_pop_corr + f"{c}.png")
        plt.show()
