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

# %%
socio_density = gpd.read_postgis(
    "SELECT * FROM density.density_socio", engine, geom_col="geometry"
)

socio.dropna(subset=["population_density"], inplace=True)
# socio.drop(columns=["geometry", "area_name"], inplace=True)

socio_density = socio_density.merge(socio, on="id", how="inner")

assert socio_density.shape[0] == socio.shape[0]


plot_correlation(
    socio_density,
    socio_corr_variables,
    heatmap_fp="../results/socio_correlation/heatmap_socio_vars.png",
    pairplot_fp="../results/socio_correlation/pairplot_socio_vars.png",
)
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

labels = ["density", "density_steps", "length_relative", "length_relative_steps"]

for i, columns in enumerate(all_density_columns):

    corr_columns = socio_corr_variables + columns

    plot_correlation(
        socio_density,
        corr_columns,
        heatmap_fp=f"../results/socio_correlation/heatmap_socio_{labels[i]}.png",
        pairplot_fp=f"../results/socio_correlation/pairplot_socio_{labels[i]}.png",
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

for i, columns in enumerate(all_fragmentation_columns):

    corr_columns = socio_corr_variables + columns

    plot_correlation(
        socio_components,
        corr_columns,
        heatmap_fp=f"../results/socio_correlation/heatmap_socio_{labels[i]}.png",
        pairplot_fp=f"../results/socio_correlation/pairplot_socio_{labels[i]}.png",
    )

# %%
# Fragmentation largest local component

socio_components = gpd.read_postgis(
    "SELECT * FROM fragmentation.component_length_socio;", engine, geom_col="geometry"
)

largest_local_component_len_columns,
##### REACH ###########
######################