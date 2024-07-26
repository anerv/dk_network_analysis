# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
from src import analysis_functions as analysis_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly_express as px
import pandas as pd
from sklearn.preprocessing import robust_scale
from pysal.lib import weights

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/df_styler.py").read())

plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

# %%

#### SOCIO CLUSTERING ####

exec(open("../helper_scripts/prepare_socio_cluster_data.py").read())

# generate socio reach comparison columns
exec(open("../helper_scripts/generate_socio_reach_columns.py").read())

# %%
# SOCIO CLUSTERING: Network variables

# Define cluster variables
socio_network_cluster_variables = (
    density_columns
    + length_relative_columns
    + component_per_km_columns
    + socio_reach_median_columns
    + socio_reach_compare_columns
    # + ["urban_pct"]
)

# Use robust_scale to norm cluster variables
socio_network_scaled = robust_scale(socio_cluster_gdf[socio_network_cluster_variables])

# Find appropriate number of clusters
m1, m2 = analysis_func.find_k_elbow_method(socio_network_scaled, min_k=1, max_k=20)

for key, val in m1.items():
    print(f"{key} : {val:.2f}")

# Define K!
k = 8
# %%
##### K-Means #######

kmeans_col = f"kmeans_{k}"

k_labels = analysis_func.run_kmeans(k, socio_network_scaled)

socio_cluster_gdf[kmeans_col] = k_labels

fp_map = fp_cluster_maps_base + f"socio_net_map_{kmeans_col}.png"
fp_size = fp_cluster_plots_base + f"socio_net_size_{kmeans_col}.png"
fp_kde = fp_cluster_plots_base + f"socio_net_kde_{kmeans_col}.png"

analysis_func.examine_cluster_results(
    socio_cluster_gdf,
    kmeans_col,
    socio_network_cluster_variables,
    fp_map,
    fp_size,
    fp_kde,
    cmap="viridis",
    palette="viridis",
)

#####  Hierarchical clustering #######
hier_col = f"hier_{k}"

hier_labels = analysis_func.run_agg_clustering(socio_network_scaled, "ward", k)

socio_cluster_gdf[hier_col] = hier_labels

fp_map = fp_cluster_maps_base + f"socio_net_map_{hier_col}.png"
fp_size = fp_cluster_plots_base + f"socio_net_size_{hier_col}.png"
fp_kde = fp_cluster_plots_base + f"socio_net_kde_{hier_col}.png"

analysis_func.examine_cluster_results(
    socio_cluster_gdf,
    hier_col,
    socio_network_cluster_variables,
    fp_map,
    fp_size,
    fp_kde,
    cmap="viridis",
    palette="viridis",
)

##### Regionalization #######

reg_col = f"reg_{k}"

w = analysis_func.spatial_weights_combined(socio_cluster_gdf, id_columns[1], k)

reg_labels = analysis_func.run_regionalization(socio_network_scaled, w, k)

socio_cluster_gdf[reg_col] = reg_labels

fp_map = fp_cluster_maps_base + f"socio_net_map_{reg_col}.png"
fp_size = fp_cluster_plots_base + f"socio_net_size_{reg_col}.png"
fp_kde = fp_cluster_plots_base + f"socio_net_kde_{reg_col}.png"

analysis_func.examine_cluster_results(
    socio_cluster_gdf,
    reg_col,
    socio_network_cluster_variables,
    fp_map,
    fp_size,
    fp_kde,
    cmap="viridis",
    palette="viridis",
)

# Compare clustering results
cluster_columns = [kmeans_col, hier_col, reg_col]
plot_titles = ["K-Means", "Hierarchical", "Regionalization"]

fp_geo = fp_cluster_data_base + "soc_net_geo.csv"
fp_feature = fp_cluster_data_base + "soc_net_feature.csv"
fp_similarity = fp_cluster_data_base + "soc_net_similarity.csv"
fp_map = fp_cluster_maps_base + "soc_net_all_clusters_map.png"


analysis_func.compare_clustering(
    socio_cluster_gdf,
    cluster_columns,
    socio_network_cluster_variables,
    plot_titles,
    format_style_index,
    fp_geo,
    fp_feature,
    fp_similarity,
    fp_map,
)

# %%
# SOCIO CLUSTERING: Socio-economic variables

# Define cluster variables
# socio_soc_cluster_variables = socio_corr_variables
# Drop households with cars variable
socio_soc_cluster_variables = [c for c in socio_corr_variables if "w car" not in c]

# Use robust_scale to norm cluster variables
socio_soc_scaled = robust_scale(socio_cluster_gdf[socio_soc_cluster_variables])

# Find appropriate number of clusters
m1, m2 = analysis_func.find_k_elbow_method(socio_soc_scaled, min_k=1, max_k=20)

for key, val in m1.items():
    print(f"{key} : {val:.2f}")

# Define K!
k = 9

##### K-Means #######

kmeans_col = f"kmeans_{k}"

k_labels = analysis_func.run_kmeans(k, socio_soc_scaled)

socio_cluster_gdf[kmeans_col] = k_labels

fp_map = fp_cluster_maps_base + f"socio_socio_map_{kmeans_col}.png"
fp_size = fp_cluster_plots_base + f"socio_socio_size_{kmeans_col}.png"
fp_kde = fp_cluster_plots_base + f"socio_socio_kde_{kmeans_col}.png"

analysis_func.examine_cluster_results(
    socio_cluster_gdf,
    kmeans_col,
    socio_soc_cluster_variables,
    fp_map,
    fp_size,
    fp_kde,
    cmap="viridis",
    palette="viridis",
)

#####  Hierarchical clustering #######
hier_col = f"hier_{k}"

hier_labels = analysis_func.run_agg_clustering(socio_soc_scaled, "ward", k)

socio_cluster_gdf[hier_col] = hier_labels

fp_map = fp_cluster_maps_base + f"socio_socio_map_{hier_col}.png"
fp_size = fp_cluster_plots_base + f"socio_socio_size_{hier_col}.png"
fp_kde = fp_cluster_plots_base + f"socio_socio_kde_{hier_col}.png"

analysis_func.examine_cluster_results(
    socio_cluster_gdf,
    hier_col,
    socio_soc_cluster_variables,
    fp_map,
    fp_size,
    fp_kde,
    cmap="viridis",
    palette="viridis",
)

##### Regionalization #######

reg_col = f"reg_{k}"

w = analysis_func.spatial_weights_combined(socio_cluster_gdf, id_columns[1], k)

reg_labels = analysis_func.run_regionalization(socio_soc_scaled, w, k)

socio_cluster_gdf[reg_col] = reg_labels


fp_map = fp_cluster_maps_base + f"socio_socio_map_{reg_col}.png"
fp_size = fp_cluster_plots_base + f"socio_socio_size_{reg_col}.png"
fp_kde = fp_cluster_plots_base + f"socio_socio_kde_{reg_col}.png"

analysis_func.examine_cluster_results(
    socio_cluster_gdf,
    reg_col,
    socio_soc_cluster_variables,
    fp_map,
    fp_size,
    fp_kde,
    cmap="viridis",
    palette="viridis",
)

# Compare clustering results
cluster_columns = [kmeans_col, hier_col, reg_col]
plot_titles = ["K-Means", "Hierarchical", "Regionalization"]

fp_geo = fp_cluster_data_base + "soc_soc_geo.csv"
fp_feature = fp_cluster_data_base + "soc_soc_feature.csv"
fp_similarity = fp_cluster_data_base + "soc_soc_similarity.csv"
fp_map = fp_cluster_maps_base + "soc_soc_all_clusters_map.png"

analysis_func.compare_clustering(
    socio_cluster_gdf,
    cluster_columns,
    socio_soc_cluster_variables,
    plot_titles,
    format_style_index,
    fp_geo,
    fp_feature,
    fp_similarity,
    fp_map,
)

# %%
##### HEX #######

# Read data
exec(open("../helper_scripts/read_hex_results.py").read())

hex_gdf.replace(np.nan, 0, inplace=True)

# exec(open("../helper_scripts/generate_socio_reach_columns.py").read())

reach_compare_columns = [c for c in hex_gdf.columns if "pct_diff" in c]

reach_compare_columns = [
    c for c in reach_compare_columns if any(r in c for r in reach_comparisons)
]

# define cluster variables
# %%
hex_cluster_variables = (
    density_columns
    + density_steps_columns[1:4]
    + length_relative_columns
    # + component_count_columns
    + component_per_km_columns
    + largest_local_component_len_columns
    + reach_columns
    + reach_compare_columns
    # + ["urban_pct"]
)


# Use robust_scale to norm cluster variables
hex_scaled = robust_scale(hex_gdf[hex_cluster_variables])

# Find appropriate number of clusters
m1, m2 = analysis_func.find_k_elbow_method(hex_scaled, min_k=1, max_k=30)

for key, val in m1.items():
    print(f"{key} : {val:.2f}")

# Define K!
k = 5

##### K-Means #######

kmeans_col = f"kmeans_{k}"

k_labels = analysis_func.run_kmeans(k, hex_scaled)

hex_gdf[kmeans_col] = k_labels

fp_map = fp_cluster_maps_base + f"hex_net_map_{kmeans_col}.png"
fp_size = fp_cluster_plots_base + f"hex_net_size_{kmeans_col}.png"
fp_kde = fp_cluster_plots_base + f"hex_net_kde_{kmeans_col}.png"

analysis_func.examine_cluster_results(
    hex_gdf,
    kmeans_col,
    hex_cluster_variables,
    fp_map,
    fp_size,
    fp_kde,
    cmap="viridis",
    palette="viridis",
)


# ##### Hierarchical clustering #######
# hier_col = f"hier_{k}"

# hier_labels = analysis_func.run_agg_clustering(hex_scaled, "ward", k)

# hex_gdf[hier_col] = hier_labels

# fp_map = fp_cluster_maps_base + f"hex_net_map_{hier_col}.png"
# fp_size = fp_cluster_plots_base + f"hex_net_size_{hier_col}.png"
# fp_kde = fp_cluster_plots_base + f"hex_net_kde_{hier_col}.png"

# analysis_func.examine_cluster_results(
#     hex_gdf, hier_col, hex_cluster_variables, fp_map, fp_size, fp_kde
# )

##### Regionalization #######

reg_col = f"reg_{k}"

w = analysis_func.spatial_weights_combined(hex_gdf, id_columns[2], k)

reg_labels = analysis_func.run_regionalization(hex_scaled, w, k)

fp_map = fp_cluster_maps_base + f"hex_net_map_{reg_col}.png"
fp_size = fp_cluster_plots_base + f"hex_net_size_{reg_col}.png"
fp_kde = fp_cluster_plots_base + f"hex_net_kde_{reg_col}.png"

hex_gdf[reg_col] = reg_labels

analysis_func.examine_cluster_results(
    hex_gdf,
    reg_col,
    hex_cluster_variables,
    fp_map,
    fp_size,
    fp_kde,
    cmap="viridis",
    palette="viridis",
)

# Compare clustering results
cluster_columns = [kmeans_col, reg_col]
plot_titles = ["K-Means", "Regionalization"]

fp_geo = fp_cluster_data_base + "hex_geo.csv"
fp_feature = fp_cluster_data_base + "hex_feature.csv"
fp_similarity = fp_cluster_data_base + "hex_similarity.csv"
fp_map = fp_cluster_maps_base + "hex_all_clusters_map.png"

analysis_func.compare_clustering(
    hex_gdf,
    cluster_columns,
    hex_cluster_variables,
    plot_titles,
    format_style_index,
    fp_geo,
    fp_feature,
    fp_similarity,
    fp_map,
)


# %%
