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

# TODO Make step that compares the fit etc based on clustering method and variables used

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

analysis_func.examine_cluster_results(
    socio_cluster_gdf, kmeans_col, socio_network_cluster_variables
)

##### Hiearchical clustering #######
hier_col = f"hier_{k}"

hier_labels = analysis_func.run_agg_clustering(socio_network_scaled, "ward", k)

socio_cluster_gdf[hier_col] = hier_labels

analysis_func.examine_cluster_results(
    socio_cluster_gdf, hier_col, socio_network_cluster_variables
)

##### Regionalization #######

reg_col = f"reg_{k}"

w = analysis_func.spatial_weights_combined(socio_cluster_gdf, id_columns[1], k)

reg_labels = analysis_func.run_regionalization(socio_network_scaled, w, k)

socio_cluster_gdf[reg_col] = reg_labels

analysis_func.examine_cluster_results(
    socio_cluster_gdf, reg_col, socio_network_cluster_variables
)

# Compare clustering results
cluster_columns = [kmeans_col, hier_col, reg_col]
plot_titles = ["K-Means", "Hierarchical", "Regionalization"]

analysis_func.compare_clustering(
    socio_cluster_gdf,
    cluster_columns,
    socio_network_cluster_variables,
    plot_titles,
    format_style_index,
)

socio_cluster_gdf[cluster_columns + ["geometry", id_columns[1]]].to_file(
    "../results/clustering/socio_network_clusters.gpkg", driver="GPKG"
)
# %%
# SOCIO CLUSTERING: Socio-economic variables

# Define cluster variables
socio_soc_cluster_variables = socio_corr_variables
# socio_soc_cluster_variables = [
#     c for c in socio_soc_cluster_variables if "1 car" not in c and "2 cars" not in c
# ]

# Use robust_scale to norm cluster variables
socio_soc_scaled = robust_scale(socio_cluster_gdf[socio_soc_cluster_variables])

# Find appropriate number of clusters
m1, m2 = analysis_func.find_k_elbow_method(socio_soc_scaled, min_k=1, max_k=20)

for key, val in m1.items():
    print(f"{key} : {val:.2f}")

# %%
# Define K!
k = 9

##### K-Means #######

kmeans_col = f"kmeans_{k}"

k_labels = analysis_func.run_kmeans(k, socio_soc_scaled)

socio_cluster_gdf[kmeans_col] = k_labels

analysis_func.examine_cluster_results(
    socio_cluster_gdf, kmeans_col, socio_soc_cluster_variables
)

##### Hiearchical clustering #######
hier_col = f"hier_{k}"

hier_labels = analysis_func.run_agg_clustering(socio_soc_scaled, "ward", k)

socio_cluster_gdf[hier_col] = hier_labels

analysis_func.examine_cluster_results(
    socio_cluster_gdf, hier_col, socio_soc_cluster_variables
)

##### Regionalization #######

reg_col = f"reg_{k}"

w = analysis_func.spatial_weights_combined(socio_cluster_gdf, id_columns[1], k)

reg_labels = analysis_func.run_regionalization(socio_soc_scaled, w, k)

socio_cluster_gdf[reg_col] = reg_labels

analysis_func.examine_cluster_results(
    socio_cluster_gdf, reg_col, socio_soc_cluster_variables
)

# Compare clustering results
cluster_columns = [kmeans_col, hier_col, reg_col]
plot_titles = ["K-Means", "Hierarchical", "Regionalization"]

analysis_func.compare_clustering(
    socio_cluster_gdf,
    cluster_columns,
    socio_soc_cluster_variables,
    plot_titles,
    format_style_index,
)

socio_cluster_gdf[cluster_columns + ["geometry", id_columns[1]]].to_file(
    "../results/clustering/socio_socioeconomic_clusters.gpkg", driver="GPKG"
)
# %%
##### HEX #######

# Read data
exec(open("../settings/read_hex_results.py").read())

hex_gdf.replace(np.nan, 0, inplace=True)

exec(open("../settings/read_reach_comparison.py").read())
hex_reach_comp_cols = [c for c in hex_reach_comparison.columns if "pct_diff" in c]
hex_reach_comp_cols = [
    c for c in hex_reach_comp_cols if "10_15" not in c and "5_15" not in c
]
del hex_reach_comparison

# %%
# define cluster variables

hex_cluster_variables = (
    density_columns
    + density_steps_columns[1:4]
    + length_relative_columns
    # + component_count_columns
    + component_per_km_columns
    + largest_local_component_len_columns
    + reach_columns
    + hex_reach_comp_cols
    # + ["urban_pct"]
)

# %%
# Use robust_scale to norm cluster variables
hex_scaled = robust_scale(hex_gdf[hex_cluster_variables])

# Find appropriate number of clusters
m1, m2 = analysis_func.find_k_elbow_method(hex_scaled, min_k=1, max_k=30)

for key, val in m1.items():
    print(f"{key} : {val:.2f}")
# %%
# Define K!
k = 5

##### K-Means #######

kmeans_col = f"kmeans_{k}"

k_labels = analysis_func.run_kmeans(k, hex_scaled)

hex_gdf[kmeans_col] = k_labels

analysis_func.examine_cluster_results(hex_gdf, kmeans_col, hex_cluster_variables)

# %%
##### Hiearchical clustering #######
hier_col = f"hier_{k}"

hier_labels = analysis_func.run_agg_clustering(hex_scaled, "ward", k)

hex_gdf[hier_col] = hier_labels

analysis_func.examine_cluster_results(hex_gdf, hier_col, hex_cluster_variables)

# %%
##### Regionalization #######

reg_col = f"reg_{k}"

w = analysis_func.spatial_weights_combined(hex_gdf, id_columns[2], k)

reg_labels = analysis_func.run_regionalization(hex_scaled, w, k)

hex_gdf[reg_col] = reg_labels

analysis_func.examine_cluster_results(hex_gdf, reg_col, hex_cluster_variables)

# Compare clustering results
cluster_columns = [kmeans_col, hier_col, reg_col]
plot_titles = ["K-Means", "Hierarchical", "Regionalization"]

analysis_func.compare_clustering(
    hex_gdf, cluster_columns, hex_cluster_variables, plot_titles, format_style_index
)

hex_gdf[cluster_columns + ["geometry", id_columns[0]]].to_file(
    "../results/clustering/hex_network_clusters.gpkg", driver="GPKG"
)

# %%
