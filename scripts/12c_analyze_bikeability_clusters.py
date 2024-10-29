# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd
from IPython.display import display
import seaborn as sns
import matplotlib.patches as mpatches

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

    q = "sql/12c_analyze_bikeability_clusters.sql"

    result = dbf.run_query_pg(q, connection)
    if result == "error":
        print("Please fix error before rerunning and reconnect to the database")

# %%
hex_cluster = gpd.read_postgis(
    "SELECT * FROM clustering.hex_clusters", engine, geom_col="geometry"
)

hex_cluster["area"] = hex_cluster["geometry"].area / 10**6

# compute urban and non-urban population
hex_cluster["urban_population"] = hex_cluster[hex_cluster.urban_pct > 0].population
hex_cluster["non_urban_population"] = hex_cluster[hex_cluster.urban_pct == 0].population

hex_cluster.fillna({"urban_population": 0}, inplace=True)
hex_cluster.fillna({"non_urban_population": 0}, inplace=True)

round(
    hex_cluster["urban_population"].sum() + hex_cluster["non_urban_population"].sum(), 0
) == round(hex_cluster["population"].sum(), 0)
# %%
hex_cluster["urban_area"] = hex_cluster[hex_cluster.urban_pct > 0]["area"]
hex_cluster["non_urban_area"] = hex_cluster[hex_cluster.urban_pct == 0]["area"]

hex_cluster.fillna({"urban_area": 0}, inplace=True)
hex_cluster.fillna({"non_urban_area": 0}, inplace=True)

round(
    hex_cluster["urban_area"].sum() + hex_cluster["non_urban_area"].sum(), 0
) == round(hex_cluster["area"].sum(), 0)
# %%
count_clusters = hex_cluster.groupby("cluster_label").size().reset_index(name="count")

cluster_sum = (
    hex_cluster[
        [
            "cluster_label",
            "population",
            "urban_population",
            "non_urban_population",
            "area",
            "urban_area",
            "non_urban_area",
        ]
    ]
    .groupby("cluster_label")
    .sum("population")
    .reset_index()
)

cluster_sum["population"] = cluster_sum["population"].astype(int)
cluster_sum["urban_population"] = cluster_sum["urban_population"].astype(int)
cluster_sum["non_urban_population"] = cluster_sum["non_urban_population"].astype(int)
cluster_sum["urban_area"] = cluster_sum["urban_area"].round(2)
cluster_sum["non_urban_area"] = cluster_sum["non_urban_area"].round(2)
cluster_sum.rename(columns={"population": "total_population"}, inplace=True)
cluster_sum.rename(columns={"area": "total_area"}, inplace=True)
# %%
cluster_ave = (
    hex_cluster.groupby("cluster_label")
    .mean(
        [
            "population",
            "population_density",
            "urban_pct",
            "area",
            "urban_population",
            "non_urban_population",
            "urban_area",
            "non_urban_area",
        ]
    )
    .reset_index()
)
# %%
cluster_ave.rename(
    columns={
        "population_density": "average_population_density",
        "population": "average_population_count",
        "urban_pct": "average_urban_pct",
        "urban_population": "average_urban_population",
        "non_urban_population": "average_non_urban_population",
        "urban_area": "average_urban_area",
        "non_urban_area": "average_non_urban_area",
        "area": "average_area",
    },
    inplace=True,
)
# %%

cluster_stats = pd.merge(count_clusters, cluster_sum, on="cluster_label")
# cluster_stats = pd.merge(cluster_stats, cluster_area, on="cluster_label")
cluster_stats = pd.merge(cluster_stats, cluster_ave, on="cluster_label")

cluster_stats["population_share"] = (
    cluster_stats.total_population / cluster_stats.total_population.sum() * 100
)

cluster_stats["area_share"] = (
    cluster_stats.total_area / cluster_stats.total_area.sum() * 100
)

cluster_stats.set_index("cluster_label", inplace=True)
# %%
y_labels = [
    "Count",
    "Total population",
    "Urban population",
    "Non-urban population",
    "Total area (km²)",
    "Urban area (km²)",
    "Non-urban area (km²)",
    "Average population count",
    "Average population density",
    "Average urban area (%)",
    "Average area (km²)",
    "Average urban population",
    "Average non-urban population",
    "Average urban area (km²)",
    "Average non-urban area (km²)",
    "Population share (%)",
    "Area share (%)",
]
plot_cols = [c for c in cluster_stats.columns if "kmeans" not in c]

assert len(y_labels) == len(plot_cols)

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

# Same plot, but population divided into urban and non-urban
fig, axes = plt.subplots(1, 2, figsize=(15, 7))

bar_width = 0.4
x = range(len(cluster_stats))

axes[0].bar(
    x,
    cluster_stats["urban_area"],
    color=colors,
    width=bar_width,
    label="Urban area",
)

# Plot non-urban population with hatch
axes[0].bar(
    x,
    cluster_stats["non_urban_area"],
    bottom=cluster_stats["urban_area"],
    color=colors,
    width=bar_width,
    hatch="//",
    label="Non-urban area",
)
axes[0].set_xticks(x)
axes[0].set_xticklabels(cluster_stats.cluster_no_str)
axes[0].set_xlabel("Cluster")
axes[0].set_ylabel("Total area (km²)")
axes[0].tick_params(axis="both", which="major", labelsize=pdict["fs_subplot"])

# Plot total population divided into urban and non-urban

# Plot urban population
axes[1].bar(
    x,
    cluster_stats["urban_population"],
    color=colors,
    width=bar_width,
    label="Urban population",
)

# Plot non-urban population with hatch
axes[1].bar(
    x,
    cluster_stats["non_urban_population"],
    bottom=cluster_stats["urban_population"],
    color=colors,
    width=bar_width,
    hatch="//",
    label="Non-urban population",
)

axes[1].set_xticks(x)
axes[1].set_xticklabels(cluster_stats.cluster_no_str)
axes[1].set_xlabel("Cluster")
axes[1].set_ylabel("Total population")
axes[1].tick_params(axis="both", which="major", labelsize=pdict["fs_subplot"])

no_urban_patch = mpatches.Patch(
    facecolor="none",
    edgecolor="grey",
    linewidth=0.5,
    label="Non-urban",
    hatch="///",
)

# Add legend
axes[1].legend(
    handles=[no_urban_patch],
    loc="upper right",
    frameon=False,
    fontsize=pdict["fs_subplot"],
)

sns.despine()

plt.savefig(
    fp_cluster_plots_base + f"hex_cluster_bar_area_pop_urban_nonurban.png",
    dpi=pdict["dpi"],
)


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
    axes[i].set_xlabel("Cluster")
    axes[i].set_ylabel(plot_labels[i])
    axes[i].tick_params(axis="both", which="major", labelsize=pdict["fs_subplot"])
    # axes[i].xaxis.set_tick_params(rotation=90)

    axes[i].spines["right"].set_visible(False)
    axes[i].spines["top"].set_visible(False)

fig.savefig(f"{fp_cluster_plots_base}hex_cluster_pop_urban_violin.png")

# %%
