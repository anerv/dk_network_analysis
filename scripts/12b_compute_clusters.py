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
#### SOCIO CLUSTERING ####

exec(open("../settings/prepare_socio_cluster_data.py").read())

# generate socio reach comparison columns
exec(open("../settings/read_reach_comparison.py").read())
hex_reach_comp_cols = [c for c in hex_reach_comparison.columns if "pct_diff" in c]
hex_reach_comp_cols = [
    c for c in hex_reach_comp_cols if "10_15" not in c and "5_15" not in c
]
socio_reach_compare_columns = [c + "_median" for c in hex_reach_comp_cols]
del hex_reach_comparison


# %%
# SOCIO CLUSTERING: Network variables

# Define cluster variables
socio_network_cluster_variables = (
    density_columns
    + length_relative_columns
    + component_per_km_columns
    + socio_reach_median_columns
    + socio_reach_compare_columns
    # + ["urban_pct", "population_density"]
)

# Use robust_scale to norm cluster variables
socio_network_scaled = robust_scale(socio_cluster_gdf[socio_network_cluster_variables])

# Find appropriate number of clusters
m1, m2 = analysis_func.find_k_elbow_method(socio_network_scaled, min_k=1, max_k=20)

for key, val in m1.items():
    print(f"{key} : {val:.2f}")

# %%
# Define K!
k = 6
##### K-Means #######

kmeans_col_net = f"kmeans_net_{k}"

k_labels = analysis_func.run_kmeans(k, socio_network_scaled)

socio_cluster_gdf[kmeans_col_net] = k_labels

fp_map = fp_socio_network_cluster_base + f"_map_{kmeans_col_net}.png"
fp_size = fp_socio_network_cluster_base + f"_size_{kmeans_col_net}.png"
fp_kde = fp_socio_network_cluster_base + f"_kde_{kmeans_col_net}.png"

colors = plot_func.get_hex_colors_from_colormap("Set2", k)
cmap = plot_func.color_list_to_cmap(colors)

cluster_means_soc_net = analysis_func.examine_cluster_results(
    socio_cluster_gdf,
    kmeans_col_net,
    socio_network_cluster_variables,
    fp_map,
    fp_size,
    fp_kde,
    cmap=cmap,
    palette=colors,
)

plot_func.style_cluster_means(cluster_means_soc_net)

# %%
# Label clusters after bikeability rank

socio_cluster_gdf["network_rank"] = None

rank = [1, 2, 5, 4, 3, 0]
assert len(rank) == k

for i, r in enumerate(rank):
    socio_cluster_gdf.loc[
        socio_cluster_gdf[kmeans_col_net] == r,
        "network_rank",
    ] = (
        i + 1
    )

socio_cluster_gdf.network_rank = socio_cluster_gdf.network_rank.astype(int)
socio_cluster_gdf[
    [kmeans_col_net] + ["geometry", id_columns[1], "network_rank"]
].to_file(fp_socio_network_clusters, driver="GPKG")


plot_func.plot_rank(socio_cluster_gdf, "network_rank")


# %%
plot_func.set_renderer("svg")
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
# SOCIO CLUSTERING: Socio-economic variables

socio_cluster_gdf = socio_cluster_gdf[
    socio_cluster_gdf["population_density"] > 0
].copy()

socio_cluster_gdf["Income -150k"] = (
    socio_cluster_gdf["Income 100-150k"] + socio_cluster_gdf["Income under 100k"]
)

# Define cluster variables
socio_soc_cluster_variables = [c for c in socio_corr_variables if "w car" not in c]
socio_soc_cluster_variables = ["Income -150k"] + socio_soc_cluster_variables
socio_soc_cluster_variables.remove("Income 100-150k")
socio_soc_cluster_variables.remove("Income under 100k")
socio_soc_cluster_variables.remove("urban_pct")
socio_soc_cluster_variables.remove("population_density")

# Use robust_scale to norm cluster variables
socio_soc_scaled = robust_scale(socio_cluster_gdf[socio_soc_cluster_variables])

# Find appropriate number of clusters
m1, m2 = analysis_func.find_k_elbow_method(socio_soc_scaled, min_k=1, max_k=20)

for key, val in m1.items():
    print(f"{key} : {val:.2f}")

# %%
# Define K!
k = 5

##### K-Means #######

kmeans_col_soc = f"kmeans_soc_{k}"

k_labels = analysis_func.run_kmeans(k, socio_soc_scaled)

socio_cluster_gdf[kmeans_col_soc] = k_labels

fp_map = fp_socio_socio_cluster_base + f"__map_{kmeans_col_soc}.png"
fp_size = fp_socio_socio_cluster_base + f"_size_{kmeans_col_soc}.png"
fp_kde = fp_socio_socio_cluster_base + f"_kde_{kmeans_col_soc}.png"

colors = plot_func.get_hex_colors_from_colormap("Set2", k)
cmap = plot_func.color_list_to_cmap(colors)

cluster_means_soc_soc = analysis_func.examine_cluster_results(
    socio_cluster_gdf,
    kmeans_col_soc,
    socio_soc_cluster_variables,
    fp_map,
    fp_size,
    fp_kde,
    cmap=cmap,
    palette=colors,
)

plot_func.style_cluster_means(cluster_means_soc_soc)
# %%
# Label clusters after type

socio_cluster_gdf["socio_label"] = None

# label_dict = {
#     0: "Medium income - high car - rural",
#     1: "Low income - low car - urban",
#     2: "High income - low car - urban",
#     3: "Very high income - very high car - rural",
#     4: "Low-medium income - low-medium car - suburban",
# }
label_dict = {
    0: "Medium income - low car",
    1: "High income - high car",
    2: "Low income - low car",
    3: "Medium income - medium-high car",
    4: "Highest income - highest car",
}
assert len(label_dict) == k

for key, val in label_dict.items():
    socio_cluster_gdf.loc[
        socio_cluster_gdf[kmeans_col_soc] == key,
        "socio_label",
    ] = val


socio_cluster_gdf[
    [kmeans_col_soc] + ["geometry", id_columns[1], "socio_label"]
].to_file(fp_socio_socio_clusters, driver="GPKG")

# %%
# EXPORT CLUSTER RESULTS TO POSTGIS
socio_cluster_gdf[["id", "network_rank", "socio_label", "geometry"]].to_postgis(
    "socio_clusters",
    engine,
    if_exists="replace",
    index=False,
)

q = "sql/12b_analysis_clustering.sql"

result = dbf.run_query_pg(q, connection)
if result == "error":
    print("Please fix error before rerunning and reconnect to the database")
# %%
