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

#### CORRELATION BETWEEN SOCIO-ECO VARIABLES ####

socio_corr_variables = [
    "households_income_under_100k_share",
    "households_income_100_150k_share",
    "households_income_150_200k_share",
    "households_income_200_300k_share",
    "households_income_300_400k_share",
    "households_income_400_500k_share",
    "households_income_500_750k_share",
    "households_income_750k_share",
    "households_with_car_share",
    "households_1car_share",
    "households_2cars_share",
    "households_nocar_share",
    "population_density",
]

socio_corr = socio_density[socio_corr_variables].corr()

# Generate a mask for the upper triangle
mask = np.triu(np.ones_like(socio_corr, dtype=bool))

# Set up the matplotlib figure
f, ax = plt.subplots(figsize=(11, 9))

# Generate a custom diverging colormap
cmap = sns.diverging_palette(230, 20, as_cmap=True)

sns.heatmap(
    socio_corr,
    mask=mask,
    cmap=cmap,
    vmax=0.3,
    center=0,
    square=True,
    linewidths=0.5,
    cbar_kws={"shrink": 0.5},
)

sns.pairplot(
    socio_density[socio_corr_variables], kind="reg", diag_kind="kde", corner=True
)

# %%


# %%


def plot_correlation(
    df,
    corr_columns,
    pair_plot_type="reg",
    diag_kind="kde",
    corner=True,
    pair_plot_x_log=False,
    pair_plot_y_log=False,
    heatmap_fp=None,
    pairplot_fp=None,
):
    """
    Plots the correlation between columns in a DataFrame and generates a heatmap and pairplot.

    Parameters:
        df (pandas.DataFrame): The DataFrame containing the data.
        corr_columns (list): The list of column names to calculate correlation and plot.
        pair_plot_type (str, optional): The type of plot for the pairplot. Defaults to "reg".
        diag_kind (str, optional): The type of plot for the diagonal subplots in the pairplot. Defaults to "kde".
        corner (bool, optional): Whether to plot only the lower triangle of the heatmap and pairplot. Defaults to True.
        pair_plot_x_log (bool, optional): Whether to set the x-axis of the pairplot to a logarithmic scale. Defaults to False.
        pair_plot_y_log (bool, optional): Whether to set the y-axis of the pairplot to a logarithmic scale. Defaults to False.
        heatmap_fp (str, optional): The file path to save the heatmap plot. Defaults to None.
        pairplot_fp (str, optional): The file path to save the pairplot. Defaults to None.

    Returns:
        None
    """

    df_corr = df[corr_columns].corr()

    # Generate a mask for the upper triangle
    mask = np.triu(np.ones_like(df_corr, dtype=bool))

    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(11, 9))

    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(230, 20, as_cmap=True)

    hm = sns.heatmap(
        df_corr,
        mask=mask,
        cmap=cmap,
        vmax=0.3,
        center=0,
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.5},
    )

    if heatmap_fp is not None:
        # Save heatmap
        hm.get_figure().savefig(heatmap_fp)

    if pair_plot_x_log is False and pair_plot_y_log is False:

        pp = sns.pairplot(
            df[corr_columns], kind=pair_plot_type, diag_kind=diag_kind, corner=corner
        )
    else:
        pp = sns.pairplot(
            df[corr_columns], kind=pair_plot_type, diag_kind=diag_kind, corner=False
        )

    if pair_plot_x_log is True:
        for ax in pp.axes.flat:
            ax.set(xscale="log")

    if pair_plot_y_log is True:
        for ax in pp.axes.flat:
            ax.set(yscale="log")

    if pairplot_fp is not None:
        # Save pairplot
        pp.savefig(pairplot_fp)


# %%


###### NETWORK DENSITY #########
################################

all_density_columns = [
    # length_columns,
    # length_steps_columns,
    density_columns,
    density_steps_columns,
    length_relative_columns,
    length_relative_steps_columns,
]
# %%
###### NETWORK DENSITY AND POP DENSITY ######

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

    socio_density[
        columns
        + [
            "population_density",
            "households_1car_share",
            "households_2cars_share",
            "households_nocar_share",
            "households_income_under_100k_share",
            "households_income_100_150k_share",
            "households_income_150_200k_share",
            "households_income_200_300k_share",
            "households_income_300_400k_share",
            "households_income_400_500k_share",
            "households_income_500_750k_share",
            "households_income_750k_share",
            "households_with_car",
            "households_with_car_share",
        ]
    ].corr()


# %%
###### NETWORK DENSITY AND INCOME ######
socio_density["household_share_low_income"] = (
    socio_density.households_income_under_100k_share
    + socio_density.households_income_100_150k_share
)

socio_density["household_share_medium_income"] = (
    socio_density.households_income_150_200k_share
    + socio_density.households_income_200_300k_share
    + socio_density.households_income_300_400k_share
    + socio_density.households_income_400_500k_share
)

socio_density["household_share_high_income"] = (
    socio_density.households_income_500_750k_share,
    socio_density.households_income_750k_share,
)

income_columns = [
    # "households_income_under_100k_share",
    # "households_income_100_150k_share",
    # "households_income_150_200k_share",
    # "households_income_200_300k_share",
    # "households_income_300_400k_share",
    # "households_income_400_500k_share",
    # "households_income_500_750k_share",
    # "households_income_750k_share",
    "household_share_low_income",
    "household_share_medium_income",
    "household_share_high_income",
]
# %%
for i in income_columns:

    for columns in all_density_columns:

        fig, axs = plt.subplots(2, 3, figsize=(15, 10))

        axs = axs.flatten()

        if len(axs) > len(columns):
            axs[-1].set_visible(False)  # to remove last plot

        for ax, col_name in zip(axs, columns):

            ax.scatter(socio_density[i], socio_density[col_name])
            ax.set_xscale("log")
            ax.set_yscale("log")
            ax.set_xlabel(i)
            ax.set_ylabel(col_name)

        fig.suptitle(f"Correlation between {i} and network density", fontsize=20)

        plt.tight_layout()

        plt.show()

        plt.close()

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
###### NETWORK DENSITY AND CAR OWNERSHIP (no car) ######
for columns in all_density_columns:

    fig, axs = plt.subplots(2, 3, figsize=(15, 10))

    axs = axs.flatten()

    if len(axs) > len(columns):
        axs[-1].set_visible(False)  # to remove last plot

    for ax, col_name in zip(axs, columns):

        ax.scatter(socio_density["households_nocar_share"], socio_density[col_name])
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("share of households with NO car")
        ax.set_ylabel(col_name)

    fig.suptitle(f"Correlation between population and car ownership", fontsize=20)

    plt.tight_layout()

# %%

socio_density_corr = socio_density[
    density_columns
    + length_relative_columns
    + [
        "households_income_under_100k_share",
        "households_income_100_150k_share",
        "households_income_150_200k_share",
        "households_income_200_300k_share",
        "households_income_300_400k_share",
        "households_income_400_500k_share",
        "households_income_500_750k_share",
        "households_income_750k_share",
        "households_with_car_share",
        "households_1car_share",
        "households_2cars_share",
        "households_nocar_share",
        "population_density",
    ]
].corr()
# Generate a mask for the upper triangle
mask = np.triu(np.ones_like(socio_density_corr, dtype=bool))

# Set up the matplotlib figure
f, ax = plt.subplots(figsize=(11, 9))

# Generate a custom diverging colormap
cmap = sns.diverging_palette(230, 20, as_cmap=True)

sns.heatmap(
    socio_density_corr,
    mask=mask,
    cmap=cmap,
    vmax=0.3,
    center=0,
    square=True,
    linewidths=0.5,
    cbar_kws={"shrink": 0.5},
)

# %%
###### FRAGMENTATION ######
##########################

socio_components = gpd.read_postgis(
    "SELECT * FROM fragmentation.component_length_socio;", engine, geom_col="geometry"
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

# %%
cols = [
    # "comp_all_count",
    # "comp_1_count",
    # "comp_2_count",
    # "comp_3_count",
    # "comp_4_count",
    # "comp_car_count",
    "component_per_length_all",
    "component_per_length_1",
    "component_per_length_2",
    "component_per_length_3",
    "component_per_length_4",
    "component_per_length_car",
    "population_density",
    "households_1car_share",
    "households_2cars_share",
    "households_nocar_share",
    "households_income_under_100k_share",
    "households_income_100_150k_share",
    "households_income_150_200k_share",
    "households_income_200_300k_share",
    "households_income_300_400k_share",
    "households_income_400_500k_share",
    "households_income_500_750k_share",
    "households_income_750k_share",
    "households_with_car_share",
]

socio_components_corr = socio_components[cols].corr()
# Generate a mask for the upper triangle
mask = np.triu(np.ones_like(socio_components_corr, dtype=bool))

# Set up the matplotlib figure
f, ax = plt.subplots(figsize=(11, 9))

# Generate a custom diverging colormap
cmap = sns.diverging_palette(230, 20, as_cmap=True)

sns.heatmap(
    socio_components_corr,
    mask=mask,
    cmap=cmap,
    vmax=0.3,
    center=0,
    square=True,
    linewidths=0.5,
    cbar_kws={"shrink": 0.5},
)
# %%


# %%
##### REACH ###########
######################
