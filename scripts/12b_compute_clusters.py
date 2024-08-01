# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
from src import analysis_functions as analysis_func
from sklearn.preprocessing import robust_scale
import numpy as np
import seaborn as sns

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/df_styler.py").read())

plot_func.set_renderer("png")
# %%
engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

# %%
#### SOCIO CLUSTERING ####

exec(open("../helper_scripts/prepare_socio_cluster_data.py").read())

# %%
# SOCIO CLUSTERING: Network variables

# Use robust_scale to norm cluster variables
socio_network_scaled = robust_scale(socio_cluster_gdf[socio_network_cluster_variables])

# %%
# Find appropriate number of clusters
m1, m2 = analysis_func.find_k_elbow_method(socio_network_scaled, min_k=1, max_k=20)

for key, val in m1.items():
    print(f"{key} : {val:.2f}")

# %%
# Define K!
k = 8
##### K-Means #######

kmeans_col_net_socio = f"kmeans_net_{k}"

k_labels = analysis_func.run_kmeans(k, socio_network_scaled)

socio_cluster_gdf[kmeans_col_net_socio] = k_labels

fp_map = fp_cluster_maps_base + f"socio_net_map_{kmeans_col_net_socio}.png"
fp_size = fp_cluster_plots_base + f"socio_net_size_{kmeans_col_net_socio}.png"
fp_kde = fp_cluster_plots_base + f"socio_net_kde_{kmeans_col_net_socio}.png"

colors = plot_func.get_hex_colors_from_colormap(pdict["cat"], k)
cmap = plot_func.color_list_to_cmap(colors)

cluster_means_soc_net = analysis_func.examine_cluster_results(
    socio_cluster_gdf,
    kmeans_col_net_socio,
    socio_network_cluster_variables,
    fp_map,
    fp_size,
    fp_kde,
    cmap=cmap,
    palette=colors,
)

plot_func.style_cluster_means(cluster_means_soc_net)

cluster_means_soc_net.to_csv(fp_soc_net_cluster_means, index=True)

# %%
# Label clusters after bikeability rank

socio_cluster_gdf["network_rank"] = None

rank = [1, 6, 7, 0, 5, 3, 4, 2]
assert len(rank) == k

for i, r in enumerate(rank):
    socio_cluster_gdf.loc[
        socio_cluster_gdf[kmeans_col_net_socio] == r,
        "network_rank",
    ] = (
        i + 1
    )

socio_cluster_gdf.network_rank = socio_cluster_gdf.network_rank.astype(int)
socio_cluster_gdf[
    [kmeans_col_net_socio] + ["geometry", id_columns[1], "network_rank"]
].to_file(fp_socio_network_clusters, driver="GPKG")


plot_func.plot_rank(socio_cluster_gdf, "network_rank")

# %%
# SOCIO CLUSTERING: Socio-economic variables

# Use robust_scale to norm cluster variables
socio_soc_scaled = robust_scale(socio_soc_gdf[socio_soc_cluster_variables])

# Find appropriate number of clusters
m1, m2 = analysis_func.find_k_elbow_method(socio_soc_scaled, min_k=1, max_k=20)

for key, val in m1.items():
    print(f"{key} : {val:.2f}")

# %%
# Define K!
k = 5

##### K-Means #######

kmeans_col_soc_soc = f"kmeans_soc_{k}"

k_labels = analysis_func.run_kmeans(k, socio_soc_scaled)

socio_soc_gdf[kmeans_col_soc_soc] = k_labels

fp_map = fp_cluster_maps_base + f"socio_soc_map_{kmeans_col_soc_soc}.png"
fp_size = fp_cluster_plots_base + f"socio_soc_size_{kmeans_col_soc_soc}.png"
fp_kde = fp_cluster_plots_base + f"socio_soc_kde_{kmeans_col_soc_soc}.png"

colors = plot_func.get_hex_colors_from_colormap(pdict["cat"], k)
cmap = plot_func.color_list_to_cmap(colors)

cluster_means_soc_soc = analysis_func.examine_cluster_results(
    socio_soc_gdf,
    kmeans_col_soc_soc,
    socio_soc_cluster_variables,
    fp_map,
    fp_size,
    fp_kde,
    cmap=cmap,
    palette=colors,
)

plot_func.style_cluster_means(cluster_means_soc_soc)

cluster_means_soc_soc.to_csv(fp_soc_soc_cluster_means, index=True)
# %%
# Label clusters after type

socio_soc_gdf["socio_label"] = None

label_dict = {
    0: "Medium income - medium car",
    1: "Low income - low car",
    2: "Highest income - highest car",
    3: "Medium income - low car",
    4: "High income - high car",
}
assert len(label_dict) == k

for key, val in label_dict.items():
    socio_soc_gdf.loc[
        socio_soc_gdf[kmeans_col_soc_soc] == key,
        "socio_label",
    ] = val


socio_soc_gdf[
    [kmeans_col_soc_soc] + ["geometry", id_columns[1], "socio_label"]
].to_file(fp_socio_socio_clusters, driver="GPKG")

# %%
# HEX CLUSTERING: Network variables

exec(open("../helper_scripts/prepare_hex_cluster_data.py").read())

# %%
# Use robust_scale to norm cluster variables
hex_network_scaled = robust_scale(hex_gdf[hex_network_cluster_variables])

# Find appropriate number of clusters
m1, m2 = analysis_func.find_k_elbow_method(hex_network_scaled, min_k=1, max_k=20)

for key, val in m1.items():
    print(f"{key} : {val:.2f}")

# %%
# Define K!
k = 5
##### K-Means #######

kmeans_col_net_hex = f"kmeans_net_{k}"

k_labels = analysis_func.run_kmeans(k, hex_network_scaled)

hex_gdf[kmeans_col_net_hex] = k_labels

fp_map = fp_cluster_maps_base + f"hex_net_map_{kmeans_col_net_hex}.png"
fp_size = fp_cluster_plots_base + f"hex_net_size_{kmeans_col_net_hex}.png"
fp_kde = fp_cluster_plots_base + f"hex_net_kde_{kmeans_col_net_hex}.png"

colors = list(cluster_color_dict_labels.values())
cmap = plot_func.color_list_to_cmap(colors)

cluster_means_hex = analysis_func.examine_cluster_results(
    hex_gdf,
    kmeans_col_net_hex,
    hex_network_cluster_variables,
    fp_map,
    fp_size,
    fp_kde,
    cmap=cmap,
    palette=colors,
)

plot_func.style_cluster_means(cluster_means_hex)

cluster_means_hex.to_csv(fp_hex_network_cluster_means, index=True)

# %%
# Make polished cluster map
fp = fp_cluster_maps_base + "hex_cluster_map.png"
plot_func.plot_hex_clusters(hex_gdf, "kmeans_net_5", cmap, fp)


# Make zoomed cluster map

fp = fp_cluster_maps_base + "hex_cluster_map_zoom.png"

xmin, ymin = (689922.425333, 6161099.004817)
xmax, ymax = (734667.301464 - 900, 6202301.965700)

plot_func.plot_hex_zoom_categorical(
    hex_gdf, "kmeans_net_5", cmap, fp, xmin, xmax, ymin, ymax
)

# %%
# Label clusters after bikeability rank
hex_gdf["cluster_label"] = None


label_dict = {
    0: "0: Highest stress - lowest density - lowest reach",
    1: "1: Low stress - medium density - medium reach",
    2: "2: High stress - medium density - low reach - local connectivity",
    3: "3: High stress - medium density - low reach - regional connectivity",
    4: "4: Lowest Stress - highest density - highest reach",
}

assert len(label_dict) == k

for key, val in label_dict.items():
    hex_gdf.loc[
        hex_gdf[kmeans_col_net_hex] == key,
        "cluster_label",
    ] = val


hex_gdf[[kmeans_col_net_hex] + ["geometry", id_columns[2], "cluster_label"]].to_parquet(
    fp_hex_network_clusters
)

# %%
# ANALYSE CLUSTERS

# EXPORT CLUSTER RESULTS TO POSTGIS
schema_queries = [
    "DROP SCHEMA IF EXISTS clustering CASCADE;",
    "CREATE SCHEMA clustering;",
]
for q in schema_queries:
    result = dbf.run_query_pg(q, connection)
    if result == "error":
        print("Please fix error before rerunning and reconnect to the database")

# %%
socio_cluster_gdf[["id", "network_rank", kmeans_col_net_socio, "geometry"]].to_postgis(
    "socio_network_clusters",
    engine,
    schema="clustering",
    if_exists="replace",
    index=False,
)
socio_soc_gdf[["id", "socio_label", kmeans_col_soc_soc, "geometry"]].to_postgis(
    "socio_socio_clusters",
    engine,
    schema="clustering",
    if_exists="replace",
    index=False,
)
# %%
hex_gdf[["hex_id", "cluster_label", kmeans_col_net_hex, "geometry"]].to_postgis(
    "hex_clusters", engine, schema="clustering", if_exists="replace", index=False
)

print("Clusters exported!")

connection.close()
# %%
