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

plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

# %%
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
# Define cluster variables
socio_cluster_variables = (
    density_columns
    + length_relative_columns
    + component_per_km_columns
    + socio_corr_variables
    + socio_reach_median_columns
    + socio_reach_compare_columns
    + ["urban_pct"]
)

# Use robust_scale to norm cluster variables
socio_scaled = robust_scale(socio_cluster_gdf[socio_cluster_variables])

# %%
# Find appropriate number of clusters
m1, m2 = analysis_func.find_k_elbow_method(socio_scaled, min_k=1, max_k=20)

for key, val in m1.items():
    print(f"{key} : {val:.2f}")

# %%
# Define K!

k = 8
# %%
##### K-Means #######

kmeans_col = f"kmeans_{k}"

k_labels = analysis_func.run_kmeans(k, socio_scaled)

socio_cluster_gdf[kmeans_col] = k_labels

plot_func.plot_clustering(socio_cluster_gdf, kmeans_col)

kmean_sizes = analysis_func.evaluate_cluster_sizes(socio_cluster_gdf, kmeans_col)
kmean_areas = analysis_func.evaluate_cluster_areas(socio_cluster_gdf, kmeans_col)

plot_func.plot_cluster_sizes(kmean_sizes, kmean_areas)

analysis_func.get_mean_cluster_variables(
    socio_cluster_gdf, kmeans_col, socio_cluster_variables
)

plot_func.plot_cluster_variable_distributions(
    socio_cluster_gdf, kmeans_col, socio_cluster_variables
)
# %%
##### Hiearchical clustering #######
hier_col = f"hier_{k}"

hier_labels = analysis_func.run_agg_clustering(socio_scaled, "ward", k)

socio_cluster_gdf[hier_col] = hier_labels

plot_func.plot_clustering(socio_cluster_gdf, hier_col)

hier_sizes = analysis_func.evaluate_cluster_sizes(socio_cluster_gdf, hier_col)
hier_areas = analysis_func.evaluate_cluster_areas(socio_cluster_gdf, hier_col)

plot_func.plot_cluster_sizes(hier_sizes, hier_areas)

analysis_func.get_mean_cluster_variables(
    socio_cluster_gdf, hier_col, socio_cluster_variables
)

plot_func.plot_cluster_variable_distributions(
    socio_cluster_gdf, hier_col, socio_cluster_variables
)

# %%
##### Regionalization #######
reg_col = f"reg_{k}"

w_queen = analysis_func.compute_spatial_weights(
    socio_cluster_gdf, id_columns[1], "queen"
)
w_knn = analysis_func.compute_spatial_weights(
    socio_cluster_gdf, id_columns[1], w_type="knn", k=3
)
w = weights.set_operations.w_union(w_queen, w_knn)

assert len(w.islands) == 0


reg_labels = analysis_func.run_regionalization(socio_scaled, w, k)

socio_cluster_gdf[reg_col] = reg_labels

plot_func.plot_clustering(socio_cluster_gdf, reg_col)

reg_sizes = analysis_func.evaluate_cluster_sizes(socio_cluster_gdf, reg_col)
reg_areas = analysis_func.evaluate_cluster_areas(socio_cluster_gdf, reg_col)

plot_func.plot_cluster_sizes(reg_sizes, reg_areas)

analysis_func.get_mean_cluster_variables(
    socio_cluster_gdf, reg_col, socio_cluster_variables
)

plot_func.plot_cluster_variable_distributions(
    socio_cluster_gdf, reg_col, socio_cluster_variables
)

# %%

cluster_columns = [kmeans_col, hier_col, reg_col]
titles = ["K-Means", "Hierarchical", "Regionalization"]

analysis_func.evaluate_geographical_coherence(socio_cluster_gdf, cluster_columns)

analysis_func.evaluate_feature_coherence(
    socio_cluster_gdf, cluster_columns, socio_cluster_variables
)
analysis_func.evaluate_solution_similarity(socio_cluster_gdf)

plot_func.map_clusters(socio_cluster_gdf, cluster_columns, titles)

# %%

# TODO Make step that compares the fit etc based on clustering method and variables used
