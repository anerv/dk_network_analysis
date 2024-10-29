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
exec(open("../settings/filepaths.py").read())

plot_func.set_renderer("png")
# %%
engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

# %%
#### SOCIO CLUSTERING ####

exec(open("../helper_scripts/prepare_socio_cluster_data.py").read())

# %%
# SOCIO CLUSTERING: Socio-economic variables

socio_socio_cluster_variables = socio_socio_cluster_variables[6:-2]

# Use robust_scale to norm cluster variables
socio_socio_scaled = robust_scale(socio_socio_gdf[socio_socio_cluster_variables])

# Find appropriate number of clusters
m1, m2 = analysis_func.find_k_elbow_method(socio_socio_scaled, min_k=1, max_k=20)

for key, val in m1.items():
    print(f"{key} : {val:.2f}")

# %%
# Define K!
k = 5

##### K-Means #######

kmeans_col_socio_soc = f"kmeans_socio_{k}"

k_labels = analysis_func.run_kmeans(k, socio_socio_scaled)

socio_socio_gdf[kmeans_col_socio_soc] = k_labels

fp_map = fp_cluster_maps_base + f"socio_socio_map_{kmeans_col_socio_soc}.png"
fp_size = fp_cluster_plots_base + f"socio_socio_size_{kmeans_col_socio_soc}.png"
fp_kde = fp_cluster_plots_base + f"socio_socio_kde_{kmeans_col_socio_soc}.png"

colors = plot_func.get_hex_colors_from_colormap(pdict["cat"], k)
cmap = plot_func.color_list_to_cmap(colors)

cluster_means_socio_soc = analysis_func.examine_cluster_results(
    socio_socio_gdf,
    kmeans_col_socio_soc,
    socio_socio_cluster_variables,
    fp_map,
    fp_size,
    fp_kde,
    cmap=cmap,
    palette=colors,
)

plot_func.style_cluster_means(cluster_means_socio_soc)

cluster_means_socio_soc.to_csv(fp_socio_socio_cluster_means, index=True)
# %%
# Label clusters after type

# NOTE Assumes this is known already!
socio_socio_gdf["socio_label"] = None

label_dict = {
    0: "High income - high car",
    1: "Highest income - high car",
    2: "Low income - lowest car - many students",
    3: "Medium income - medium car",
    4: "Medium income - low car",
}
assert len(label_dict) == k

for key, val in label_dict.items():
    socio_socio_gdf.loc[
        socio_socio_gdf[kmeans_col_socio_soc] == key,
        "socio_label",
    ] = val


# TODO: MAKE A NICE CLUSTER MAP HERE
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

# %%
# Label clusters after bikeability rank # NOTE Assumes this is known already!
cluster_dict = {0: 1, 1: 4, 2: 2, 3: 3, 4: 5}

hex_gdf.replace({kmeans_col_net_hex: cluster_dict}, inplace=True)

# %%

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

plot_func.plot_zoom_categorical(
    hex_gdf, "kmeans_net_5", cmap, fp, xmin, xmax, ymin, ymax
)

# %%
# Label clusters after bikeability rank

# NOTE Assumes this is known already!
hex_gdf["cluster_label"] = None

label_dict = {
    1: "1: Highest stress - lowest density - lowest reach",
    2: "2: High stress - medium density - low reach - local connectivity",
    3: "3: High stress - medium density - low reach - regional connectivity",
    4: "4: Low stress - high density - medium reach - regional low stress connectivity",
    5: "5: Lowest Stress - highest density - highest reach",
}

assert len(label_dict) == k

for key, val in label_dict.items():
    hex_gdf.loc[
        hex_gdf[kmeans_col_net_hex] == key,
        "cluster_label",
    ] = val


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

socio_socio_gdf[["id", "socio_label", kmeans_col_socio_soc, "geometry"]].to_postgis(
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
