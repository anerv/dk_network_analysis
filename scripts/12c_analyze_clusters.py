# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
from src import analysis_functions as analysis_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import contextily as cx
from matplotlib.patches import Patch
from IPython.display import display
import plotly_express as px
import seaborn as sns

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/df_styler.py").read())
exec(open("../settings/filepaths.py").read())

plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

# %%
preprocess = False
if preprocess:

    q = "sql/12b_analysis_clustering.sql"

    result = dbf.run_query_pg(q, connection)
    if result == "error":
        print("Please fix error before rerunning and reconnect to the database")

# %%
hex_cluster = gpd.read_postgis(
    "SELECT * FROM clustering.hex_clusters", engine, geom_col="geometry"
)

count_clusters = hex_cluster.groupby("cluster_label").size().reset_index(name="count")

cluster_pop = (
    hex_cluster[["cluster_label", "population"]]
    .groupby("cluster_label")
    .sum("population")
    .reset_index()
)

cluster_pop["population"] = cluster_pop["population"].astype(int)
cluster_pop.rename(columns={"population": "total_population"}, inplace=True)

cluster_ave = (
    hex_cluster.groupby("cluster_label")
    .mean(["population_density", "population", "urban_pct"])
    .reset_index()
)

cluster_ave.rename(
    columns={
        "population_density": "average_population_density",
        "population": "average_population_count",
        "urban_pct": "average_urban_pct",
    },
    inplace=True,
)

hex_cluster["area"] = hex_cluster["geometry"].area / 10**6
cluster_area = (
    hex_cluster[["cluster_label", "area"]]
    .groupby("cluster_label")
    .sum("area")
    .reset_index()
)
cluster_area.rename(columns={"area": "total_area"}, inplace=True)

cluster_stats = pd.merge(count_clusters, cluster_pop, on="cluster_label")
cluster_stats = pd.merge(cluster_stats, cluster_area, on="cluster_label")
cluster_stats = pd.merge(cluster_stats, cluster_ave, on="cluster_label")

cluster_stats["population_share"] = (
    cluster_stats.total_population / cluster_stats.total_population.sum() * 100
)

cluster_stats["area_share"] = (
    cluster_stats.total_area / cluster_stats.total_area.sum() * 100
)

cluster_stats.set_index("cluster_label", inplace=True)

y_labels = [
    "Count",
    "Total population",
    "Total area (km²)",
    "Average population count",
    "Average population density",
    "Average urban area (%)",
    "Population share (%)",
    "Area share (%)",
]
plot_cols = [c for c in cluster_stats.columns if "kmeans" not in c]

display(cluster_stats[plot_cols].style.pipe(format_style_index))

cluster_stats["cluster_no_str"] = cluster_stats.kmeans_net_5.astype(int).astype(str)

# %%
# cluster_stats.sort_values("sort_column", inplace=True)
colors = [cluster_color_dict_labels[k] for k in cluster_stats.index]
colors = list(cluster_color_dict_labels.values())
cmap = plot_func.color_list_to_cmap(colors)

for i, c in enumerate(plot_cols):

    plt.figure(figsize=pdict["fsbar"])
    sns.barplot(
        x=cluster_stats.cluster_no_str,
        y=cluster_stats[c],
        hue=cluster_stats.cluster_no_str,
        palette=colors,
        width=0.4,
    )
    # plt.xticks(rotation=90)
    plt.xlabel("")
    plt.ylabel(y_labels[i])

    plt.tick_params(axis="both", which="major", labelsize=pdict["fs_subplot"])

    sns.despine()

    plt.savefig(fp_cluster_plots_base + f"hex_cluster_bar_{c}.png", dpi=pdict["dpi"])

    plt.show()

cluster_stats.to_csv(fp_cluster_data_base + "hex_cluster_stats.csv", index=True)
# %%
# Make plot with both area and population
fig, axes = plt.subplots(1, 2, figsize=pdict["fsbar_sub"])

axes = axes.flatten()

sns.barplot(
    x=cluster_stats.cluster_no_str,
    y=cluster_stats["total_area"],
    hue=cluster_stats.cluster_no_str,
    palette=colors,
    width=0.4,
    ax=axes[0],
)

axes[0].set_xlabel("")
axes[0].set_ylabel("Total area (km²)")
axes[0].tick_params(axis="both", which="major", labelsize=pdict["fs_subplot"])

sns.barplot(
    x=cluster_stats.cluster_no_str,
    y=cluster_stats["total_population"],
    hue=cluster_stats.cluster_no_str,
    palette=colors,
    width=0.4,
    ax=axes[1],
)

axes[1].set_xlabel("")
axes[1].set_ylabel("Total population")
axes[1].tick_params(axis="both", which="major", labelsize=pdict["fs_subplot"])

sns.despine()

plt.savefig(fp_cluster_plots_base + f"hex_cluster_bar_area_pop.png", dpi=pdict["dpi"])

#
# %%
hex_cluster["cluster_no_str"] = hex_cluster["kmeans_net_5"].astype(int).astype(str)

plot_labels = ["Population density", "Urban area (%)"]

order = hex_cluster["cluster_no_str"].unique()
order.sort()

fig, axes = plt.subplots(1, 2, figsize=pdict["fsbar_sub"])

axes = axes.flatten()

for i, c in enumerate(["population_density", "urban_pct"]):

    sns.violinplot(
        x=hex_cluster["cluster_no_str"],  # hex_cluster["cluster_label"],
        y=hex_cluster[c],
        hue=hex_cluster["cluster_no_str"],  # hex_cluster["cluster_label"],
        palette=cluster_color_dict.values(),
        fill=False,
        cut=0,
        ax=axes[i],
        order=order,
    )
    axes[i].set_xlabel("")
    axes[i].set_ylabel(plot_labels[i])
    axes[i].tick_params(axis="both", which="major", labelsize=pdict["fs_subplot"])
    # axes[i].xaxis.set_tick_params(rotation=90)

    axes[i].spines["right"].set_visible(False)
    axes[i].spines["top"].set_visible(False)

fig.savefig(f"{fp_cluster_plots_base}hex_cluster_pop_urban_violin.png")

# %%


socio_hex_cluster = gpd.read_postgis(
    f"SELECT * FROM clustering.socio_cluster_results",
    engine,
    geom_col="geometry",
)


# %%

# cols = [c for c in socio_hex_cluster.columns.to_list() if "area_hex" in c]
# cols.append("id")
# cluster_gdf = socio_hex_cluster[cols].copy()

# cluster_gdf.replace(pd.NA, 0, inplace=True)

# # TODO: Make stacked bar chart of hex cluster shares in each socio cluster


# %%
# ### ************************************************
# socio_cluster_gdf = gpd.read_postgis(
#     "SELECT * FROM socio_cluster_results", engine, geom_col="geometry"
# )

# socio_cluster_gdf.rename(columns=population_rename_dict, inplace=True)

# # %%

# socio_cluster_gdf["share_low_income"] = (
#     socio_cluster_gdf["Income under 100k (share)"]
#     + socio_cluster_gdf["Income 100-150k (share)"]
#     + socio_cluster_gdf["Income 150-200k (share)"]
#     + socio_cluster_gdf["Income 200-300k (share)"]
# )


# # %%
# fig = px.scatter(
#     socio_cluster_gdf,
#     x="share_low_income",
#     y="Households w car (share)",
#     hover_data=["socio_label", "id"],
#     color="socio_label",
# )
# fig.show()

# # %%
# # Plot socio clusters and pop/urban density
# plt.figure(figsize=(15, 10))
# plt.scatter(
#     socio_cluster_gdf["socio_label"], socio_cluster_gdf["population_density"], alpha=0.5
# )
# plt.xlabel("Socio Label")
# plt.ylabel("Population Density")
# plt.title("Population Density by Socio Label")
# plt.xticks(rotation=45)
# plt.show()


# plt.figure(figsize=(15, 10))
# plt.scatter(socio_cluster_gdf["socio_label"], socio_cluster_gdf["urban_pct"], alpha=0.5)
# plt.xlabel("Socio Label")
# plt.ylabel("Urban pct")
# plt.title("Urban pct by Socio Label")
# plt.xticks(rotation=45)
# plt.show()


# # %%
# # Plot distribution of network rank in each socio cluster
# grouped = (
#     socio_cluster_gdf.groupby("socio_label")["network_rank"]
#     .value_counts()
#     .unstack(fill_value=0)
# )
# fig, axes = plt.subplots(len(grouped), 1, figsize=(15, 20))
# axes = axes.flatten()
# for i, (label, data) in enumerate(grouped.iterrows()):
#     axes[i].bar(data.index, data.values)
#     axes[i].set_title(f"Socio Label: {label}")
#     axes[i].set_xlabel("Network Rank")
#     axes[i].set_ylabel("Count")
#     axes[i].tick_params(labelsize=10)
# plt.tight_layout()
# plt.show()

# # %%

# input_colors = plot_func.get_hex_colors_from_colormap("viridis", 6)
# input_colors.reverse()


# # Plot proporiton of network rank in each socio cluster
# correlation = (
#     socio_cluster_gdf.groupby(["socio_label", "network_rank"])
#     .size()
#     .unstack(fill_value=0)
# )
# correlation = correlation.div(correlation.sum(axis=1), axis=0)
# plt.figure(figsize=(15, 15))
# correlation.plot(
#     kind="bar", stacked=True, color=input_colors
# )  # lts_color_dict.values()
# plt.ylabel("Proportion", fontsize=12)
# plt.title("Correlation between Socio Label and Network Rank", fontsize=14)
# plt.legend(bbox_to_anchor=(1, 1), fontsize=12, title="Network Rank", title_fontsize=10)
# plt.tick_params(
#     labelsize=10,
# )
# plt.xlabel("", fontsize=12)
# plt.show()


# # %%
# x_col = "network_rank"
# cols = [
#     "Income under 100k (share)",
#     "Income 100-150k (share)",
#     "Income 150-200k (share)",
#     "Income 200-300k (share)",
#     "Income 300-400k (share)",
#     "Income 400-500k (share)",
#     "Income 500-750k (share)",
#     "Income 750k (share)",
#     "share_low_income",
#     "Households w car (share)",
#     "Households 1 car (share)",
#     "Households 2 cars (share)",
#     "Households no car (share)",
#     "urban_pct",
#     "population_density",
# ]

# fig, ax = plt.subplots(4, 4, figsize=(20, 20))
# ax = ax.flatten()
# ax[-1].set_visible(False)
# for c in cols:
#     ax[cols.index(c)].scatter(socio_cluster_gdf[x_col], socio_cluster_gdf[c], alpha=0.5)
#     ax[cols.index(c)].set_title(c)
#     ax[cols.index(c)].set_xlabel(x_col)
#     ax[cols.index(c)].set_ylabel(c)

# # %%
# # # input = [v for v in lts_color_dict.values()]
# # input_colors = plot_func.get_hex_colors_from_colormap("viridis", k)
# # input_colors.reverse()
# # test_colors = plot_func.color_list_to_cmap(input_colors)

# # plot_func.plot_rank(socio_cluster_gdf, "network_rank", cmap=test_colors)

# # plot_func.plot_labels(socio_cluster_gdf, "network_rank", cmap=test_colors)
# # %%

# for sc in socio_cluster_gdf["socio_label"].unique():
#     print(sc)
#     display(socio_cluster_gdf[socio_cluster_gdf["socio_label"] == sc].describe())

# # %%
# sc_values = socio_cluster_gdf["socio_label"].unique()
# household_counts = []
# people_counts = []
# households_with_car = []
# households_without_car = []


# for sc in socio_cluster_gdf["socio_label"].unique():
#     household_count = socio_cluster_gdf[socio_cluster_gdf["socio_label"] == sc][
#         "households"
#     ].sum()

#     print(f"Socio Cluster '{sc}' has {household_count:,.0f} households.")

#     household_counts.append(household_count)

#     people_count = socio_cluster_gdf[socio_cluster_gdf["socio_label"] == sc][
#         "population"
#     ].sum()

#     print(f"Socio Cluster '{sc}' has {people_count:,.0f} people.")

#     people_counts.append(people_count)

#     count_households_car = socio_cluster_gdf[socio_cluster_gdf["socio_label"] == sc][
#         "households_with_car"
#     ].sum()

#     print(
#         f"Socio Cluster '{sc}' has {count_households_car:,.0f} households with at least one car."
#     )

#     households_with_car.append(count_households_car)

#     count_households_no_car = socio_cluster_gdf[socio_cluster_gdf["socio_label"] == sc][
#         "households_without_car"
#     ].sum()

#     print(
#         f"Socio Cluster '{sc}' has {count_households_no_car:,.0f} households without a car."
#     )

#     households_without_car.append(count_households_no_car)

# df = pd.DataFrame(
#     {
#         "Socio Cluster": sc_values,
#         "Households": household_counts,
#         "People": people_counts,
#         "Households with car": households_with_car,
#         "Households without car": households_without_car,
#     }
# )

# # %%
# display(df.style.pipe(format_style_no_index))

# # %%

# # - [ ] how many low income, car-free?
# # - [ ] find areas with high car ownership and low income
# # etc

# # %%
# connection.close()
