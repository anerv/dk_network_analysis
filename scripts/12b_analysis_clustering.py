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

socio_cluster_gdf[[kmeans_col_net] + ["geometry", id_columns[1]]].to_file(
    fp_socio_network_clusters, driver="GPKG"
)

plot_func.style_cluster_means(cluster_means_soc_net)


# %%
# SOCIO CLUSTERING: Socio-economic variables

socio_cluster_gdf = socio_cluster_gdf[socio_cluster_gdf["population_density"] > 0]

# Define cluster variables
socio_soc_cluster_variables = [c for c in socio_corr_variables if "w car" not in c]

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

socio_cluster_gdf[[kmeans_col_soc] + ["geometry", id_columns[1]]].to_file(
    fp_socio_socio_clusters, driver="GPKG"
)

plot_func.style_cluster_means(cluster_means_soc_soc)
# %%
# ###### PLOT CLUSTER OVERLAY ######

# based on https://darribas.org/gds_course/content/bG/lab_G.html


socio_network_clusters = socio_cluster_gdf.dissolve(by=kmeans_col_net)
socio_network_clusters.reset_index(inplace=True)

socio_socio_clusters = socio_cluster_gdf.dissolve(by=kmeans_col_soc)
socio_socio_clusters.reset_index(inplace=True)

socio_network_clusters[["geometry", id_columns[1], kmeans_col_net]].to_file(
    fp_socio_network_clusters, driver="GPKG"
)

socio_socio_clusters[["geometry", id_columns[1], kmeans_col_soc]].to_file(
    fp_socio_socio_clusters, driver="GPKG"
)

f, ax = plt.subplots(1, figsize=(15, 15))

labels = [
    "Socio-Network",
    "Socio-Socio",
]  # "Hex-Network"
colors = ["xkcd:salmon", "xkcd:lime"]  #  "xkcd:sky blue",

for i, cluster in enumerate(
    [
        socio_network_clusters,
        socio_socio_clusters,
    ]  # hex_network_clusters
):
    cluster.plot(
        ax=ax,
        edgecolor=colors[i],
        facecolor="none",
        # hatch="//",
        linewidth=1,
        label=labels[i],
    )

legend_handles = [
    Patch(edgecolor=colors[i], fill=False, linewidth=1.5, label=labels[i])
    for i in range(len(labels))
]

ax.legend(handles=legend_handles, loc="upper right")


cx.add_basemap(
    ax, crs=socio_network_clusters.crs, source=cx.providers.CartoDB.DarkMatterNoLabels
)

ax.set_axis_off()

plt.savefig(fp_cluster_map_overlay, dpi=300)

plt.show()

# %%
# Compute cluster intersections

socio_cluster_gdf["network_cluster"] = socio_cluster_gdf[kmeans_col_net]
socio_cluster_gdf["socio_cluster"] = socio_cluster_gdf[kmeans_col_soc]

intersections = gpd.overlay(
    socio_cluster_gdf[["network_cluster", "geometry"]],
    socio_cluster_gdf[["socio_cluster", "geometry"]],
    how="intersection",
    keep_geom_type=True,
)

intersections["cluster_combinations"] = (
    intersections.network_cluster.astype(str)
    + "_"
    + intersections.socio_cluster.astype(str)
)

inter_dissolved = intersections.dissolve(by="cluster_combinations")

inter_dissolved.reset_index(inplace=True)

inter_dissolved["area_sqkm"] = inter_dissolved.geometry.area / 1000000


intersecting_clusters = inter_dissolved[inter_dissolved.area_sqkm > 0.1]

display(
    intersecting_clusters[["cluster_combinations", "area_sqkm"]]
    .sort_values(by="area_sqkm", ascending=False)
    .style.pipe(format_style_index)
)

# %%
inter_dissolved.to_file("test.gpkg", driver="GPKG")

# %%
# ##### HEX #######

# Read data
exec(open("../settings/read_hex_results.py").read())

hex_gdf.replace(np.nan, 0, inplace=True)

exec(open("../settings/read_reach_comparison.py").read())
hex_reach_comp_cols = [c for c in hex_reach_comparison.columns if "pct_diff" in c]
hex_reach_comp_cols = [
    c for c in hex_reach_comp_cols if "10_15" not in c and "5_15" not in c
]
del hex_reach_comparison


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

# Use robust_scale to norm cluster variables
hex_scaled = robust_scale(hex_gdf[hex_cluster_variables])

# Find appropriate number of clusters
m1, m2 = analysis_func.find_k_elbow_method(hex_scaled, min_k=1, max_k=30)

for key, val in m1.items():
    print(f"{key} : {val:.2f}")

# Define K!
k = 5
# %%
##### K-Means #######

kmeans_col = f"kmeans_{k}"

k_labels = analysis_func.run_kmeans(k, hex_scaled)

hex_gdf[kmeans_col] = k_labels

fp_map = fp_hex_network_cluster_base + f"_map_{kmeans_col}.png"
fp_size = fp_hex_network_cluster_base + f"_size_{kmeans_col}.png"
fp_kde = fp_hex_network_cluster_base + f"_kde_{kmeans_col}.png"

colors = plot_func.get_hex_colors_from_colormap("Set2", k)
cmap = plot_func.color_list_to_cmap(colors)

cluster_means_hex = analysis_func.examine_cluster_results(
    hex_gdf,
    kmeans_col,
    hex_cluster_variables,
    fp_map,
    fp_size,
    fp_kde,
    cmap=cmap,
    palette=colors,
)

hex_gdf[[kmeans_col] + ["geometry", id_columns[2]]].to_parquet(fp_hex_network_clusters)

plot_func.style_cluster_means(cluster_means_hex)

# %

# %%


# %%
