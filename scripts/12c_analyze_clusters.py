# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
from src import analysis_functions as analysis_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.preprocessing import robust_scale
import contextily as cx
from matplotlib.patches import Patch
from IPython.display import display

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/df_styler.py").read())

plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

# %%

socio_cluster_gdf = gpd.read_postgis(
    "SELECT * FROM socio_cluster_results", engine, geom_col="geometry"
)

socio_cluster_gdf.rename(columns=population_rename_dict, inplace=True)

# %%

socio_cluster_gdf["share_low_income"] = (
    socio_cluster_gdf["Income under 100k (share)"]
    + socio_cluster_gdf["Income 100-150k (share)"]
    + socio_cluster_gdf["Income 150-200k (share)"]
    + socio_cluster_gdf["Income 200-300k (share)"]
)


# %%
import plotly_express as px

fig = px.scatter(
    socio_cluster_gdf,
    x="share_low_income",
    y="Households w car (share)",
    hover_data=["socio_label", "id"],
    color="socio_label",
)
fig.show()

# %%
# Plot socio clusters and pop/urban density
plt.figure(figsize=(15, 10))
plt.scatter(
    socio_cluster_gdf["socio_label"], socio_cluster_gdf["population_density"], alpha=0.5
)
plt.xlabel("Socio Label")
plt.ylabel("Population Density")
plt.title("Population Density by Socio Label")
plt.xticks(rotation=45)
plt.show()


plt.figure(figsize=(15, 10))
plt.scatter(socio_cluster_gdf["socio_label"], socio_cluster_gdf["urban_pct"], alpha=0.5)
plt.xlabel("Socio Label")
plt.ylabel("Urban pct")
plt.title("Urban pct by Socio Label")
plt.xticks(rotation=45)
plt.show()


# %%
# Plot distribution of network rank in each socio cluster
grouped = (
    socio_cluster_gdf.groupby("socio_label")["network_rank"]
    .value_counts()
    .unstack(fill_value=0)
)
fig, axes = plt.subplots(len(grouped), 1, figsize=(15, 20))
axes = axes.flatten()
for i, (label, data) in enumerate(grouped.iterrows()):
    axes[i].bar(data.index, data.values)
    axes[i].set_title(f"Socio Label: {label}")
    axes[i].set_xlabel("Network Rank")
    axes[i].set_ylabel("Count")
    axes[i].tick_params(labelsize=10)
plt.tight_layout()
plt.show()

# %%

input_colors = plot_func.get_hex_colors_from_colormap("viridis", 6)
input_colors.reverse()


# Plot proporiton of network rank in each socio cluster
correlation = (
    socio_cluster_gdf.groupby(["socio_label", "network_rank"])
    .size()
    .unstack(fill_value=0)
)
correlation = correlation.div(correlation.sum(axis=1), axis=0)
plt.figure(figsize=(15, 15))
correlation.plot(
    kind="bar", stacked=True, color=input_colors
)  # lts_color_dict.values()
plt.ylabel("Proportion", fontsize=12)
plt.title("Correlation between Socio Label and Network Rank", fontsize=14)
plt.legend(bbox_to_anchor=(1, 1), fontsize=12, title="Network Rank", title_fontsize=10)
plt.tick_params(
    labelsize=10,
)
plt.xlabel("", fontsize=12)
plt.show()


# %%
x_col = "network_rank"
cols = [
    "Income under 100k (share)",
    "Income 100-150k (share)",
    "Income 150-200k (share)",
    "Income 200-300k (share)",
    "Income 300-400k (share)",
    "Income 400-500k (share)",
    "Income 500-750k (share)",
    "Income 750k (share)",
    "share_low_income",
    "Households w car (share)",
    "Households 1 car (share)",
    "Households 2 cars (share)",
    "Households no car (share)",
    "urban_pct",
    "population_density",
]

fig, ax = plt.subplots(4, 4, figsize=(20, 20))
ax = ax.flatten()
ax[-1].set_visible(False)
for c in cols:
    ax[cols.index(c)].scatter(socio_cluster_gdf[x_col], socio_cluster_gdf[c], alpha=0.5)
    ax[cols.index(c)].set_title(c)
    ax[cols.index(c)].set_xlabel(x_col)
    ax[cols.index(c)].set_ylabel(c)

# %%
# input = [v for v in lts_color_dict.values()]
input_colors = plot_func.get_hex_colors_from_colormap("viridis", k)
input_colors.reverse()
test_colors = plot_func.color_list_to_cmap(input_colors)


def plot_rank(gdf, label_col, cmap="viridis"):
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    ax.set_axis_off()
    gdf.plot(
        column=label_col,
        legend=True,
        ax=ax,
        cmap=cmap,
        linewidth=0.1,
        categorical=True,
    )
    plt.tight_layout()


plot_rank(socio_cluster_gdf, "network_rank", cmap=test_colors)

# %%
