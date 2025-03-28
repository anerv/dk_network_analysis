# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
from src import analysis_functions as analysis_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd
from IPython.display import display
import seaborn as sns
from shapely.geometry import Polygon

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/df_styler.py").read())
exec(open("../settings/filepaths.py").read())

plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

# %%

socio_hex_cluster = gpd.read_postgis(
    "SELECT * FROM clustering.socio_socio_clusters", engine, geom_col="geometry"
)
socio_hex_cluster.fillna(0, inplace=True)

exec(open("../helper_scripts/read_socio_pop.py").read())

socio_hex_cluster.drop(columns=["geometry"], inplace=True)

socio_socio = socio.merge(socio_hex_cluster, on="id")

# socio_socio = socio_socio.drop(columns=["geometry_x", "geometry_y"])

assert len(socio_socio) == len(socio) == len(socio_hex_cluster)
# %%

bikeability_rename_dict = {
    "share_hex_cluster_1": "Share bikeability 1",
    "share_hex_cluster_2": "Share bikeability 2",
    "share_hex_cluster_3": "Share bikeability 3",
    "share_hex_cluster_4": "Share bikeability 4",
    "share_hex_cluster_5": "Share bikeability 5",
}
socio_socio.rename(columns=bikeability_rename_dict, inplace=True)

socio_bikeability_cols = [c for c in socio_socio.columns if "Share bikeability" in c]

corr_columns = socio_corr_variables[7:-2] + socio_bikeability_cols
# %%

plot_corr = False  # Slow!

if plot_corr:
    plot_func.plot_correlation(
        socio_socio,
        corr_columns,
        heatmap_fp=fp_socio_bikeability_heatmap,
        pairplot_fp=fp_socio_bikeability_pairplot,
        pair_plot_x_log=True,
        pair_plot_y_log=True,
    )

    display(socio_socio[corr_columns].corr().style.background_gradient(cmap="coolwarm"))
    display(socio_socio[corr_columns])

# %%

preprocess = False

if preprocess:

    q = "sql/12f_process_hexcluster_socio.sql"

    result = dbf.run_query_pg(q, connection)
    if result == "error":
        print("Please fix error before rerunning and reconnect to the database")


# %%
# Get hex bikeability clusters with socio data
pop_keys = list(population_rename_dict.keys())
pop_keys = pop_keys[7:23]
pop_keys.remove("households_income_under_150k_pct")

population_keys_string = ", ".join(pop_keys)

hex_bike_socio = pd.read_sql(
    f"""SELECT cluster_label, {population_keys_string} FROM clustering.hex_bikeability_socio""",
    engine,
)

hex_bike_socio["households_income_under_150k_pct"] = (
    hex_bike_socio.households_income_under_100k_pct
    + hex_bike_socio.households_income_100_150k_pct
)

hex_bike_socio.rename(columns=population_rename_dict, inplace=True)


# %%

bikeability_values = sorted(list(hex_bike_socio.cluster_label.unique()))

for s in socio_corr_variables[7:-2]:

    fig, ax = plt.subplots(figsize=pdict["fsbar"])
    sns.boxplot(
        x="cluster_label",
        y=s,
        data=hex_bike_socio,
        palette=bikeability_cluster_color_dict_labels.values(),
        hue="cluster_label",
        order=bikeability_values,
    )

    plt.yrange = [0, 100]
    plt.xlabel("")
    plt.ylabel(s)
    plt.yticks([0, 100])
    # plt.yticks([min(hex_bike_socio[s]), max(hex_bike_socio[s])])

    plt.xticks(rotation=90)

    sns.despine(left=True)

    s_fp = s.replace(" ", "_")
    plt.savefig(
        fp_cluster_plots_base + f"{s_fp}_hex_bikeability_boxplot.png", dpi=pdict["dpi"]
    )

    plt.show()

# %%

# Compute mean, median, and standard deviation for 'average_bikeability_rank' grouped by 'socio_cluster'
bikeability_stats = socio_socio.groupby("socio_label")["average_bikeability_rank"].agg(
    ["mean", "median", "std"]
)

display(bikeability_stats)

# %%

# Label outliers
# socio_socio = analysis_func.label_outliers_iqr(
#     socio_socio, "socio_label", "average_bikeability_rank"
# )

socio_socio = analysis_func.label_outliers_custom_std(
    socio_socio, "socio_label", "average_bikeability_rank", std_multiplier=1
)

for i in socio_socio["socio_label"].unique():
    print(
        f"{i}: Total: {len(socio_socio[socio_socio['socio_label'] == i])} - Above: {len(socio_socio[(socio_socio['socio_label'] == i) & (socio_socio['outlier_above'] == True)])} - Below: {len(socio_socio[(socio_socio['socio_label'] == i) & (socio_socio['outlier_below'] == True)])}"
    )

# %%

socio_cluster_values = socio_socio.socio_label.unique()
socio_cluster_values.sort()

for socio_label in socio_cluster_values:

    socio_label_fp = analysis_func.clean_labels(socio_label)

    plot_func.plot_above_below_mean(
        socio_socio,
        socio_label,
    )

    analysis_func.export_outliers(
        socio_socio,
        socio_label=socio_label,
        fp_above=fp_equity_outliers_above + f"{socio_label_fp}.gpkg",
        fp_below=fp_equity_outliers_below + f"{socio_label_fp}.gpkg",
    )

# %%

plot_func.make_combined_outlier_plot(
    socio_socio,
    "socio_label",
    socio_cluster_colors_dict,
    fp=fp_equity_outliers_map,
    fontsize=14,
)

# %%

socio_cluster_values = socio_socio.socio_label.unique()
socio_cluster_values.sort()

fontsize = 14

for socio_label in socio_cluster_values:

    this_cluster = socio_socio[
        (socio_socio["socio_label"] == socio_label)
        & (socio_socio.outlier_above == False)
        & (socio_socio.outlier_below == False)
    ]

    this_cluster_above = socio_socio[
        (socio_socio["socio_label"] == socio_label)
        & (socio_socio.outlier_above == True)
    ]

    this_cluster_below = socio_socio[
        (socio_socio["socio_label"] == socio_label)
        & (socio_socio.outlier_below == True)
    ]

    # Define cluster variables
    socio_socio_cluster_variables = [
        c for c in socio_corr_variables if "w car" not in c
    ]
    socio_socio_cluster_variables = socio_socio_cluster_variables[8:-2]
    socio_socio_cluster_variables.remove(
        "Household income 50th percentile",
    )
    socio_socio_cluster_variables.remove(
        "Household income 80th percentile",
    )

    fig, ax = plt.subplots(figsize=pdict["fsbar"])
    sns.stripplot(
        data=this_cluster[socio_socio_cluster_variables],
        size=5,
        jitter=True,
        ax=ax,
        color="#BBBBBB",
        label="Non-outlier",
    )
    sns.stripplot(
        data=this_cluster_above[socio_socio_cluster_variables],
        size=5,
        jitter=True,
        ax=ax,
        color="#882255",
        alpha=0.5,
        label="Outlier above mean",
    )
    sns.stripplot(
        data=this_cluster_below[socio_socio_cluster_variables],
        size=5,
        jitter=True,
        ax=ax,
        color="#009988",
        label="Outlier below mean",
    )
    plt.xticks(rotation=90, fontsize=fontsize)
    plt.title(f"{socio_label}", fontsize=fontsize)
    plt.xlabel("")
    plt.ylabel("")
    ax.tick_params(axis="both", which="major", labelsize=fontsize)

    sns.despine(left=True)
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), frameon=False, fontsize=fontsize)

    s = analysis_func.clean_labels(socio_label)
    plt.savefig(fp_equity_outlier_stripplot + f"{s}.png")
    plt.show()

# %%

# Based on outliers present in zoomed in areas
socio_outliers_below = socio_socio[
    (socio_socio.outlier_below == True) & (socio_socio.kmeans_socio.isin([5]))  # 6, 7
]

socio_outliers_above = socio_socio[
    (socio_socio.outlier_above == True) & (socio_socio.kmeans_socio.isin([1, 2, 4, 5]))
]

active_labels_below = list(socio_outliers_below["socio_label"].unique())
active_labels_below.sort()
colors_below = [socio_cluster_colors_dict[l] for l in active_labels_below]
cmap_below = plot_func.color_list_to_cmap(colors_below)

active_labels_above = list(socio_outliers_above["socio_label"].unique())
active_labels_above.sort()
colors_above = [socio_cluster_colors_dict[l] for l in active_labels_above]
cmap_above = plot_func.color_list_to_cmap(colors_above)

# %%

squares = []

xmin, ymin = 705086, 6163309  # 708757, 6164597
xmax, ymax = (
    737729,
    6190758,
)  # 739359, 6188364

squares.append(Polygon([(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]))

plot_func.plot_outliers_zoom(
    socio_outliers_above,
    socio_socio,
    cmap_above,
    xmin,
    xmax,
    ymin,
    ymax,
    filepath=fp_equity_outliers_above_zoom,
    bbox_to_anchor=(0.65, 0.99),
    fontsize=16,
)

# %%
xmin, ymin = 626468, 6052735
xmax, ymax = 677547, 6094376

squares.append(Polygon([(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]))

plot_func.plot_outliers_zoom(
    socio_outliers_below,
    socio_socio,
    cmap_below,
    xmin,
    xmax,
    ymin,
    ymax,
    filepath=fp_equity_outliers_below_zoom,
    bbox_to_anchor=(0.1, 0.07),
    fontsize=16,
)

# %%
squares_gdf = gpd.GeoDataFrame(geometry=squares)

fig, ax = plt.subplots(figsize=pdict["fsmap"])

socio_socio.plot(ax=ax, color="#DDDDDD", linewidth=0.0)
squares_gdf.plot(ax=ax, facecolor="none", edgecolor="red", linewidth=2.5)

ax.set_axis_off()

plt.tight_layout()
plt.savefig(fp_equity_outliers_context, dpi=pdict["dpi"])
plt.show()
plt.close()

# %%
# Average bikeability rank per socio clsuters
ave_socio_bike = pd.read_sql("SELECT * FROM clustering.socio_socio_clusters", engine)
# Order rows by socio_label and average_bikeability_rank
ave_socio_bike.sort_values(by=["socio_label", "average_bikeability_rank"], inplace=True)
ave_socio_bike.reset_index(drop=True, inplace=True)

# %%

## Label outliers
# ave_socio_bike = analysis_func.label_outliers_iqr(
#     ave_socio_bike, "socio_label", "average_bikeability_rank"
# )

ave_socio_bike = analysis_func.label_outliers_custom_std(
    ave_socio_bike, "socio_label", "average_bikeability_rank", 1
)

for i in ave_socio_bike["socio_label"].unique():
    print(
        f"{i}: Total: {len(ave_socio_bike[ave_socio_bike['socio_label'] == i])} - Above: {len(ave_socio_bike[(ave_socio_bike['socio_label'] == i) & (ave_socio_bike['outlier_above'] == True)])} - Below: {len(ave_socio_bike[(ave_socio_bike['socio_label'] == i) & (ave_socio_bike['outlier_below'] == True)])}"
    )

# %%

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

plot_func.make_stripplot_w_outliers(
    data=ave_socio_bike,
    x="average_bikeability_rank",
    y="socio_label",
    hue_col="socio_label",
    palette=list(socio_cluster_colors_dict.values()),
    xlabel="Average bikeability rank",
    xticks=[i for i in range(1, 6)],
    fp=fp_cluster_plots_base + "average_bikeability_rank_by_socio_label_outliers.png",
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
