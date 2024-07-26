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

exec(open("../helper_scripts/generate_socio_reach_columns.py").read())
# %%
# SOCIO CLUSTERING: Network variables

# Define cluster variables
socio_network_cluster_variables_org = (
    density_columns
    + length_relative_columns
    + component_per_km_columns
    + socio_reach_median_columns
    + socio_reach_compare_columns
    # + ["urban_pct", "population_density"]
)

rename_socio_dict = (
    rename_index_dict_density
    | rename_index_dict_fragmentation
    | rename_index_dict_largest_comp
    | rename_index_dict_reach
    | rename_socio_reach_dict
)
rename_socio_dict["urban_pct"] = "Urban %"

socio_cluster_gdf.rename(rename_socio_dict, inplace=True, axis=1)

socio_network_cluster_variables = []
for key, value in rename_socio_dict.items():
    if key in socio_network_cluster_variables_org:
        socio_network_cluster_variables.append(value)

assert len(socio_network_cluster_variables) == len(socio_network_cluster_variables_org)
# %%
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

socio_soc_gdf = socio_cluster_gdf[socio_cluster_gdf["population_density"] > 0].copy()

socio_soc_gdf["Income -150k (share)"] = (
    socio_soc_gdf["Income 100-150k (share)"]
    + socio_soc_gdf["Income under 100k (share)"]
)

# Define cluster variables
socio_soc_cluster_variables = [c for c in socio_corr_variables if "w car" not in c]
socio_soc_cluster_variables = ["Income -150k (share)"] + socio_soc_cluster_variables
socio_soc_cluster_variables.remove("Income 100-150k (share)")
socio_soc_cluster_variables.remove("Income under 100k (share)")
socio_soc_cluster_variables.remove("urban_pct")
socio_soc_cluster_variables.remove("population_density")

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

exec(open("../helper_scripts/read_hex_results.py").read())

exec(open("../helper_scripts/read_reach_comparison.py").read())
reach_compare_columns = [c for c in hex_reach_comparison.columns if "pct_diff" in c]

reach_compare_columns = [
    c for c in reach_compare_columns if any(r in c for r in reach_comparisons)
]

hex_gdf.replace(np.nan, 0, inplace=True)
# %%

selected_reach_comp_columns = [r for r in reach_compare_columns if "5_10" not in r]

# Define cluster variables
hex_network_cluster_variables_org = (
    density_columns
    # + length_relative_columns
    + ["total_car_pct"]
    # + component_per_km_columns
    # + largest_local_component_len_columns
    + reach_columns
    + reach_compare_columns
)

rename_hex_dict = (
    rename_index_dict_density
    | rename_index_dict_fragmentation
    | rename_index_dict_largest_comp
    | rename_index_dict_reach
    | rename_hex_reach_dict
)
rename_hex_dict["urban_pct"] = "Urban %"
hex_gdf.rename(rename_hex_dict, inplace=True, axis=1)

hex_network_cluster_variables = []
for key, value in rename_hex_dict.items():
    if key in hex_network_cluster_variables_org:
        hex_network_cluster_variables.append(value)

assert len(hex_network_cluster_variables) == len(hex_network_cluster_variables_org)
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

colors = plot_func.get_hex_colors_from_colormap(pdict["cat"], k)
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
hex_gdf["cluster_label"] = None


label_dict = {
    0: "Highest stress - lowest density - lowest reach",
    1: "Low stress - medium density - medium reach",
    2: "High stress - medium density - low reach - local connectivity",
    3: "High stress - medium density - low reach - regional connectivity",
    4: "Lowest Stress - highest density - highest reach",
}
assert len(label_dict) == k

for key, val in label_dict.items():
    hex_gdf.loc[
        hex_gdf[kmeans_col_net_hex] == key,
        "cluster_label",
    ] = val


# hex_gdf.network_rank = hex_gdf.network_rank.astype(int)
hex_gdf[[kmeans_col_net_hex] + ["geometry", id_columns[2], "cluster_label"]].to_parquet(
    fp_hex_network_clusters
)

# TODO: update colors
cluster_map = plot_func.plot_labels(hex_gdf, "cluster_label", cmap=cmap)

cluster_map.savefig(fp_cluster_maps_base + "_hex_cluster_label.png", dpi=300)

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

hex_gdf[["hex_id", "cluster_label", kmeans_col_net_hex, "geometry"]].to_postgis(
    "hex_clusters", engine, schema="clustering", if_exists="replace", index=False
)

print("Clusters exported!")

connection.close()
# %%
