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

socio_socio_cluster_variables = socio_socio_cluster_variables[8:-2]

socio_socio_cluster_variables.remove(
    "Household income 50th percentile",
)
socio_socio_cluster_variables.remove(
    "Household income 80th percentile",
)

# Use robust_scale to norm cluster variables
socio_socio_scaled = robust_scale(socio_socio_gdf[socio_socio_cluster_variables])

# Find appropriate number of clusters
m1, m2 = analysis_func.find_k_elbow_method(socio_socio_scaled, min_k=1, max_k=20)

for key, val in m1.items():
    print(f"{key} : {val:.2f}")

# %%
# Define K!
k = 7

##### K-Means #######

kmeans_col_socio_soc = f"kmeans_socio"

k_labels = analysis_func.run_kmeans(k, socio_socio_scaled)

socio_socio_gdf[kmeans_col_socio_soc] = k_labels

# Label clusters after car ownership # NOTE Assumes this is known already!
cluster_dict = {0: 5, 1: 4, 2: 6, 3: 3, 4: 2, 5: 7, 6: 1}

socio_socio_gdf.replace({kmeans_col_socio_soc: cluster_dict}, inplace=True)

# %%

socio_cluster_colors_dict = {
    "1: High income - 2 cars": "#77AADD",  # light blue
    "2: Very high income - 2 cars": "#99DDFF",  # light cyan
    "3: Medium income - high car": "#44BB99",  # mint
    "4: Medium/high income - medium car": "#AAAA00",  # olive
    "5: Medium/low income - 1 car": "#BBCC33",  # pear
    "6: Very low income - low car": "#FFAABB",  # pink
    "7: Medium income - very low car": "#EE8866",  # orange
}

fp_map = fp_cluster_maps_base + f"socio_socio_map_{kmeans_col_socio_soc}.png"
fp_size = fp_cluster_plots_base + f"socio_socio_size_{kmeans_col_socio_soc}.png"
fp_kde = fp_cluster_plots_base + f"socio_socio_kde_{kmeans_col_socio_soc}.png"

colors = list(socio_cluster_colors_dict.values())
cmap = plot_func.color_list_to_cmap(colors)
# colors = sns.color_palette("Set2", k)

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


# 0/5 medium income - 2 cars is the largest group - but relatively high share of 1 car households
# 1/4 a very average household - lower side on no car ownership
# 2/6 very low income - very low high income - low car ownership
# 3/3 relative high shares of medium income - relative high share of 1 car household - lower share of no car ownership
# 4/2 very high income - highest rate of 2 car ownership - second lowest rate of no car ownership
# 5/7 medium/high income - but fairly low rate of very high income - highest rate of no car ownership!
# 6/1 high income - high rate of 2 car ownership - lowest rate of no car ownership

# OBS 1 car does not mean that it is the majority - only that it is relatively high!

label_dict = {
    1: "1: High income - 2 cars",
    2: "2: Very high income - 2 cars",
    3: "3: Medium income - high car",
    4: "4: Medium/high income - medium car",
    5: "5: Medium/low income - 1 car",
    6: "6: Very low income - low car",
    7: "7: Medium income - very low car",
}
assert len(label_dict) == k


for key, val in label_dict.items():
    socio_socio_gdf.loc[
        socio_socio_gdf[kmeans_col_socio_soc] == key,
        "socio_label",
    ] = val

# %%

colors = list(socio_cluster_colors_dict.values())
cmap = plot_func.color_list_to_cmap(colors)

fp = fp_cluster_maps_base + "socio_cluster_map.png"
plot_func.make_cluster_map(
    socio_socio_gdf, "socio_label", cmap, fp, attr="Statistics Denmark", fontsize=16
)

# %%
# Make zoomed cluster map
fp = fp_cluster_maps_base + "socio_cluster_map_zoom.png"

xmin, ymin = (689922.425333, 6161099.004817)
xmax, ymax = (734667.301464 - 900, 6202301.965700)

plot_func.plot_zoom_categorical(
    socio_socio_gdf,
    "socio_label",
    cmap,
    fp,
    xmin,
    xmax,
    ymin,
    ymax,
    add_attribution=False,
)

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

kmeans_col_net_hex = f"kmeans_net"

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

colors = list(bikeability_cluster_color_dict_labels.values())
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
# Label clusters after bikeability rank

# NOTE Assumes this is known already!
hex_gdf["cluster_label"] = None

label_dict = {
    1: "1: High stress",
    2: "2: Local low stress connectivity",
    3: "3: Regional low stress connectivity",
    4: "4: High bikeability",
    5: "5: Highest bikeability and high density",
}

assert len(label_dict) == k

for key, val in label_dict.items():
    hex_gdf.loc[
        hex_gdf[kmeans_col_net_hex] == key,
        "cluster_label",
    ] = val

# %%

# Make polished cluster map
# No labels
fp = fp_cluster_maps_base + "hex_cluster_map.png"
plot_func.make_cluster_map(hex_gdf, "kmeans_net", cmap, fp)

# Labels
fp = fp_cluster_maps_base + "hex_cluster_map_labels.png"
plot_func.make_cluster_map(hex_gdf, "cluster_label", cmap, fp, fontsize=16)

# Make zoomed cluster map
fp = fp_cluster_maps_base + "hex_cluster_map_zoom.png"

xmin, ymin = (689922.425333, 6161099.004817)
xmax, ymax = (734667.301464 - 900, 6202301.965700)

plot_func.plot_zoom_categorical(hex_gdf, "kmeans_net", cmap, fp, xmin, xmax, ymin, ymax)


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
