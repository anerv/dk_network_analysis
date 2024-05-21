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
# read data

hex_reach = gpd.read_postgis(
    "SELECT * FROM reach.hex_reach", connection, geom_col="geometry"
)

for p in reach_columns:
    hex_reach[p] = hex_reach[p] / 1000  # Convert to km

for p in reach_diff_columns:
    hex_reach[p] = hex_reach[p] / 1000  # Convert to km

# %%
####### MAPS ##############################
###########################################

# Absolute reach length

# Use norm/same color scale for all maps?

plot_titles = [
    "Network reach: LTS 1",
    "Network reach: LTS 2",
    "Network reach: LTS 3",
    "Network reach: LTS 4",
    "Network reach: Car network",
]
file_paths = []

plot_columns = reach_columns


for i, p in enumerate(plot_columns):

    plot_func.plot_classified_poly(
        gdf=hex_reach,
        plot_col=p,
        scheme=scheme,
        k=k,
        cx_tile=cx_tile_2,
        plot_na=True,
        cmap=pdict["pos"],
        edgecolor="none",
        title=plot_titles[i],
        fp=filepaths[i],
    )

# %%
# Absolute reach differences

# Use diverging color map
# Use norm/same color scale for all maps?

plot_titles = []
file_paths = []
plot_columns = reach_diff_columns

for i, p in enumerate(plot_columns):

    plot_func.plot_classified_poly(
        gdf=hex_reach,
        plot_col=p,
        scheme=scheme,
        k=k,
        cx_tile=cx_tile_2,
        plot_na=True,
        cmap=pdict["pos"],
        edgecolor="none",
        title=plot_titles[i],
        fp=filepaths[i],
    )

# %%
# Pct differences between LTS and car reach

# Use diverging color map
# Use norm/same color scale for all maps?

plot_titles = []
file_paths = []
plot_columns = reach_diff_pct_columns

for i, p in enumerate(plot_columns):

    plot_func.plot_classified_poly(
        gdf=hex_reach,
        plot_col=p,
        scheme=scheme,
        k=k,
        cx_tile=cx_tile_2,
        plot_na=True,
        cmap=pdict["pos"],
        edgecolor="none",
        title=plot_titles[i],
        fp=filepaths[i],
    )

# %%
# ***** Histograms *****


# %%
# ***** KDE PLOTS *****

# TODO: Make stacked df?

for label, df in stacked_dfs.items():

    df.rename(columns={"lts": "Network level"}, inplace=True)

    fig = sns.kdeplot(
        data=df,
        x="length",
        hue="Network level",
        # multiple="stack",
        # fill=True,
        log_scale=True,
        palette=lts_color_dict.values(),
    )

    fig.set_xlabel("Length (km)")
    fig.set_title(f"Network length KDE at the {label.lower()} level")
    plt.savefig(filepaths_kde_length[list(stacked_dfs.keys()).index(label)])

    plt.show()

    plt.close()


# %%

# Corr plots

# Corr between reach length and density?? (if so, join with density data)


# Corr with components?
