# %%

from src import db_functions as dbf
from src import plotting_functions as plot_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import matplotlib.patches as mpatches
import matplotlib as mpl

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

    q = "sql/12d_process_socio_clusters.sql"

    result = dbf.run_query_pg(q, connection)
    if result == "error":
        print("Please fix error before rerunning and reconnect to the database")

# %%
socio_hex_cluster = gpd.read_postgis(
    "SELECT * FROM clustering.socio_socio_clusters", engine, geom_col="geometry"
)
socio_hex_cluster.fillna(0, inplace=True)

area_columns = [c for c in socio_hex_cluster.columns if "area" in c]
area_columns.append("socio_label")
grouped_socio_clusters = socio_hex_cluster[area_columns].groupby("socio_label").sum()

# Normalize the data to get proportions
hex_type_proportions = grouped_socio_clusters.div(
    grouped_socio_clusters.sum(axis=1), axis=0
)

colors = list(bikeability_cluster_color_dict.values())
cmap = plot_func.color_list_to_cmap(colors)

# Plot the stacked bar chart
ax = hex_type_proportions.plot(
    kind="bar", stacked=True, figsize=pdict["fsbar"], cmap=cmap
)

# Add labels and title
ax.set_xlabel("")
ax.set_ylabel("Proportion")

ax.set_yticks([0, 1])

ax.set_xticklabels(
    ax.get_xticklabels(),
    rotation=30,
    ha="right",
    fontdict={"fontsize": pdict["fontsize"] + 2},
)
sns.despine(left=True)

# turn off legend
ax.get_legend().remove()

# handles, labels = ax.get_legend_handles_labels()
# labels = list(bikeability_cluster_color_dict_labels.keys())
# plt.legend(handles, labels, bbox_to_anchor=(1.05, 1), loc="upper left", frameon=False)

# Show plot
plt.tight_layout()
plt.savefig(fp_cluster_plots_base + "socio_clusters_proportions.png", dpi=pdict["dpi"])
plt.show()
# %%

# Average bikeability rank per socio clsuters
ave_socio_bike = pd.read_sql("SELECT * FROM clustering.socio_socio_clusters", engine)
# Order rows by socio_label and average_bikeability_rank
ave_socio_bike.sort_values(by=["socio_label", "average_bikeability_rank"], inplace=True)
ave_socio_bike.reset_index(drop=True, inplace=True)

# %%
# For each socio area

plot_func.make_stripplot(
    ave_socio_bike,
    "average_bikeability_rank",
    "socio_label",
    "socio_label",
    list(socio_cluster_colors_dict.values()),
    xlabel="Average bikeability rank",
    xticks=[i for i in range(1, 6)],
    fp=fp_cluster_plots_base + "average_bikeability_rank_by_socio_label.png",
)

plot_func.make_barplot(
    ave_socio_bike,
    "socio_label",
    "average_bikeability_rank",
    "socio_label",
    list(socio_cluster_colors_dict.values()),
    xlabel="",
    fp=fp_cluster_plots_base + "average_bikeability_rank_by_socio_label_grouped.png",
)

# %%
# Correlation between socio variables and bikeability rank

socio_bike = pd.read_sql("SELECT * FROM clustering.socio_socio_clusters", engine)

exec(open("../helper_scripts/read_socio_pop.py").read())

socio.drop(columns=["geometry"], inplace=True)

socio_socio_bike = socio_bike.merge(socio, on="id")

socio_socio_bike.sort_values(
    by=["socio_label", "average_bikeability_rank"], inplace=True
)

# %%
# Correlation between socio variables and average bikeability rank

for c in socio_corr_variables:

    plot_func.sns_scatter(
        socio_socio_bike,
        c,
        "average_bikeability_rank",
        "socio_label",
        list(socio_cluster_colors_dict.values()),
        yticks=[i for i in range(1, 6)],
    )

# %%
# Share of students

plot_func.make_barplot(
    socio_socio_bike,
    "socio_label",
    "Students (share)",
    "socio_label",
    list(socio_cluster_colors_dict.values()),
    xlabel="",
)

plot_func.make_stripplot(
    socio_socio_bike,
    "Students (share)",
    "socio_label",
    "socio_label",
    list(socio_cluster_colors_dict.values()),
    xlabel="Share of students",
)

# %%
# Share of population and pct urban areas in each socio cluster

socio_bike = gpd.read_postgis(
    "SELECT * FROM clustering.socio_socio_clusters", engine, geom_col="geometry"
)

socio = pd.read_sql("SELECT id, population, households, urban_pct FROM socio", engine)

socio_socio_bike = socio_bike.merge(socio, on="id")

socio_socio_bike.sort_values(
    by=["socio_label", "average_bikeability_rank"], inplace=True
)

# %%
# Share of population

fig, ax = plt.subplots(figsize=pdict["fsbar"])

sns.barplot(
    data=socio_socio_bike,
    x="socio_label",
    y="population",
    hue="socio_label",
    estimator=sum,
    palette=list(socio_cluster_colors_dict.values()),
    width=0.4,
    ax=ax,
    errorbar=None,
)

ax.set_xlabel("")
ax.set_ylabel("Population (mill.)")
plt.xticks(rotation=45, ha="right")
plt.yticks([0, 1200000])
labels = ["0", "1.2"]
ax.set_yticklabels(labels)
ax.tick_params(axis="both", which="major", labelsize=pdict["fontsize"])

sns.despine(left=True, bottom=True)

plt.tight_layout()

plt.savefig(fp_cluster_plots_base + "population_by_socio_label.png", dpi=pdict["dpi"])

# %%

socio_socio_bike["area_sqkm"] = socio_socio_bike.geometry.area / 10**6

socio_socio_bike["urban_area"] = (socio_socio_bike.area_sqkm) * (
    socio_socio_bike["urban_pct"] / 100
)

socio_socio_bike["non_urban_area"] = (
    socio_socio_bike.area_sqkm - socio_socio_bike["urban_area"]
)

socio_grouped = (
    socio_socio_bike[["socio_label", "urban_area", "non_urban_area"]]
    .groupby("socio_label")
    .sum()
)

# %%
colors = list(socio_cluster_colors_dict.values())

fig, ax = plt.subplots(figsize=pdict["fsbar"])

bar_width = 0.4
x = range(len(socio_grouped))

ax.bar(
    x,
    socio_grouped["urban_area"],
    color=colors,
    width=bar_width,
    label="Urban area",
)

# Plot non-urban population with hatch
ax.bar(
    x,
    socio_grouped["non_urban_area"],
    bottom=socio_grouped["urban_area"],
    color=colors,
    width=bar_width,
    hatch="//",
    label="Non-urban area",
)
ax.set_xticks(x)
ax.set_xticklabels(socio_grouped.index)
plt.xticks(rotation=45, ha="right")
ax.set_xlabel("")
ax.set_ylabel("Area (km²)")
ax.tick_params(axis="both", which="major")
ax.set_yticks([0, 15000])
ax.get_yaxis().set_major_formatter(
    mpl.ticker.FuncFormatter(lambda x, p: format(int(x), ","))
)
sns.despine(left=True, bottom=True)

no_urban_patch = mpatches.Patch(
    facecolor="none",
    edgecolor="grey",
    linewidth=0.5,
    label="Non-urban",
    hatch="///",
)

# Add legend
ax.legend(
    handles=[no_urban_patch],
    loc="upper right",
    frameon=False,
    fontsize=pdict["fs_subplot"],
)
plt.tight_layout()
plt.savefig(
    fp_cluster_plots_base + "urban_non_urban_area_by_socio_label.png", dpi=pdict["dpi"]
)

# %%
