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


socio_bikeability_cols = [c for c in socio_socio.columns if "share_hex_cluster" in c]

corr_columns = socio_corr_variables[7:-2] + socio_bikeability_cols
# %%
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

for socio_cluster in socio_socio.socio_label.unique():

    areas_below_median = socio_socio[socio_socio["socio_label"] == socio_cluster].loc[
        socio_socio["average_bikeability_rank"]
        < bikeability_stats.loc[socio_cluster, "median"]
    ]

    total_socio_label = socio_socio[socio_socio["socio_label"] == socio_cluster]

    print(
        f"{len(areas_below_median)} out of {len(total_socio_label)} areas are below the median for socio cluster {socio_cluster}"
    )

    areas_below_mean = socio_socio[socio_socio["socio_label"] == socio_cluster].loc[
        socio_socio["average_bikeability_rank"]
        < bikeability_stats.loc[socio_cluster, "mean"]
    ]
    print(
        f"{len(areas_below_mean)} out of {len(total_socio_label)} areas are below the mean for socio cluster {socio_cluster}"
    )

    areas_1std_below = socio_socio[socio_socio["socio_label"] == socio_cluster].loc[
        socio_socio["average_bikeability_rank"]
        < bikeability_stats.loc[socio_cluster, "mean"]
        - bikeability_stats.loc[socio_cluster, "std"]
    ]
    print(
        f"{len(areas_1std_below)} out of {len(total_socio_label)} areas are 1 std dev below the mean for socio cluster {socio_cluster}"
    )

    areas_1std_above = socio_socio[socio_socio["socio_label"] == socio_cluster].loc[
        socio_socio["average_bikeability_rank"]
        > bikeability_stats.loc[socio_cluster, "mean"]
        + bikeability_stats.loc[socio_cluster, "std"]
    ]

    print(
        f"{len(areas_1std_above)} out of {len(total_socio_label)} areas are 1 std dev above the mean for socio cluster {socio_cluster}"
    )

    print("\n")


# %%

socio_cluster_values = socio_socio.socio_label.unique()
socio_cluster_values.sort()

for socio_label in socio_cluster_values:

    socio_label_fp = analysis_func.clean_labels(socio_label)

    plot_func.plot_above_below_mean(
        socio_socio,
        socio_label=socio_label,
    )

    analysis_func.export_outliers(
        socio_socio,
        socio_label=socio_label,
        fp_above="../results/equity/data/outliers_above_mean_"
        + f"{socio_label_fp}.gpkg",
        fp_below="../results/equity/data/outliers_below_mean_"
        + f"{socio_label_fp}.gpkg",
    )

plot_func.make_combined_outlier_plot(
    socio_socio,
    "socio_label",
    "average_bikeability_rank",
    socio_cluster_colors_dict,
    "../results/equity/maps/outliers_combined.png",
)

# %%

socio_socio = analysis_func.label_above_below_mean(
    socio_socio, "socio_label", "average_bikeability_rank"
)

socio_cluster_values = socio_socio.socio_label.unique()
socio_cluster_values.sort()

for socio_label in socio_cluster_values:

    this_cluster = socio_socio[
        (socio_socio["socio_label"] == socio_label)
        & (socio_socio.above_mean == False)
        & (socio_socio.below_mean == False)
    ]

    this_cluster_above = socio_socio[
        (socio_socio["socio_label"] == socio_label) & (socio_socio.above_mean == True)
    ]

    this_cluster_below = socio_socio[
        (socio_socio["socio_label"] == socio_label) & (socio_socio.below_mean == True)
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
    plt.xticks(rotation=90, fontsize=pdict["fs_subplot"])
    plt.title(f"{socio_label}", fontsize=pdict["title_fs"])
    plt.xlabel("")
    plt.ylabel("")

    sns.despine(left=True)
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(
        by_label.values(), by_label.keys(), frameon=False, fontsize=pdict["fs_subplot"]
    )

    s = analysis_func.clean_labels(socio_label)
    plt.savefig("../results/equity/plots/stripplot_outlier_analysis_" + f"{s}.png")
    plt.show()

# %%
