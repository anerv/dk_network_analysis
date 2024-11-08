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

# %%

#### SOCIO CLUSTERING ####

exec(open("../helper_scripts/prepare_socio_cluster_data.py").read())

# %%
# SOCIO CLUSTERING: Socio-economic variables

# Use robust_scale to norm cluster variables
socio_socio_scaled = robust_scale(socio_socio_gdf[socio_socio_cluster_variables])

# Find appropriate number of clusters
m1, m2 = analysis_func.find_k_elbow_method(socio_socio_scaled, min_k=1, max_k=20)

for key, val in m1.items():
    print(f"{key} : {val:.2f}")

# Define K!
k = 5

# %%
##### K-Means #######

kmeans_col = f"kmeans_{k}"

k_labels = analysis_func.run_kmeans(k, socio_socio_scaled)

socio_socio_gdf[kmeans_col] = k_labels

fp_map = fp_cluster_maps_base + f"socio_socio_map_{kmeans_col}.png"
fp_size = fp_cluster_plots_base + f"socio_socio_size_{kmeans_col}.png"
fp_kde = fp_cluster_plots_base + f"socio_socio_kde_{kmeans_col}.png"

analysis_func.examine_cluster_results(
    socio_socio_gdf,
    kmeans_col,
    socio_socio_cluster_variables,
    fp_map,
    fp_size,
    fp_kde,
    cmap="viridis",
    palette="viridis",
)

#####  Hierarchical clustering #######
hier_col = f"hier_{k}"

hier_labels = analysis_func.run_agg_clustering(socio_socio_scaled, "ward", k)

socio_socio_gdf[hier_col] = hier_labels

fp_map = fp_cluster_maps_base + f"socio_socio_map_{hier_col}.png"
fp_size = fp_cluster_plots_base + f"socio_socio_size_{hier_col}.png"
fp_kde = fp_cluster_plots_base + f"socio_socio_kde_{hier_col}.png"

analysis_func.examine_cluster_results(
    socio_socio_gdf,
    hier_col,
    socio_socio_cluster_variables,
    fp_map,
    fp_size,
    fp_kde,
    cmap="viridis",
    palette="viridis",
)

##### Regionalization #######

reg_col = f"reg_{k}"

w = analysis_func.spatial_weights_combined(socio_socio_gdf, id_columns[1], k)

reg_labels = analysis_func.run_regionalization(socio_socio_scaled, w, k)

socio_socio_gdf[reg_col] = reg_labels


fp_map = fp_cluster_maps_base + f"socio_socio_map_{reg_col}.png"
fp_size = fp_cluster_plots_base + f"socio_socio_size_{reg_col}.png"
fp_kde = fp_cluster_plots_base + f"socio_socio_kde_{reg_col}.png"

analysis_func.examine_cluster_results(
    socio_socio_gdf,
    reg_col,
    socio_socio_cluster_variables,
    fp_map,
    fp_size,
    fp_kde,
    cmap="viridis",
    palette="viridis",
)

# Compare clustering results
cluster_columns = [kmeans_col, hier_col, reg_col]
plot_titles = ["K-Means", "Hierarchical", "Regionalization"]

fp_geo = fp_cluster_data_base + "socio_socio_geo.csv"
fp_feature = fp_cluster_data_base + "socio_socio_feature.csv"
fp_similarity = fp_cluster_data_base + "socio_socio_similarity.csv"
fp_map = fp_cluster_maps_base + "socio_socio_all_clusters_map.png"

analysis_func.compare_clustering(
    socio_socio_gdf,
    cluster_columns,
    socio_socio_cluster_variables,
    plot_titles,
    format_style_index,
    fp_geo,
    fp_feature,
    fp_similarity,
    fp_map,
)

# %%
##### HEX #######

exec(open("../helper_scripts/prepare_hex_cluster_data.py").read())

# %%
# Use robust_scale to norm cluster variables
hex_scaled = robust_scale(hex_gdf[hex_network_cluster_variables])

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
    hex_network_cluster_variables,
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
    hex_network_cluster_variables,
    fp_map,
    fp_size,
    fp_kde,
    cmap="viridis",
    palette="viridis",
)
# %%
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
    hex_network_cluster_variables,
    plot_titles,
    format_style_index,
    fp_geo,
    fp_feature,
    fp_similarity,
    fp_map,
)

# %%
