# %%
import numpy as np

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())

# Read socio pop
exec(open("../helper_scripts/read_socio_pop.py").read())
exec(open("../helper_scripts/read_socio_results.py").read())

socio_density = socio_density[socio_density.total_network_length > 0]

# Merge all
socio_cluster_gdf = socio.merge(socio_density, on="id", how="inner")
socio_cluster_gdf = socio_cluster_gdf.merge(socio_components, on="id", how="inner")
socio_cluster_gdf = socio_cluster_gdf.merge(
    socio_largest_components, on="id", how="inner"
)
socio_cluster_gdf = socio_cluster_gdf.merge(socio_reach, on="id", how="inner")
socio_cluster_gdf = socio_cluster_gdf.merge(
    socio_reach_comparison, on="id", how="inner"
)

assert len(socio_density) == len(socio_cluster_gdf)

duplicates = [
    c for c in socio_cluster_gdf.columns if c.endswith("_x") or c.endswith("_y")
]
assert len(duplicates) == 0

socio_cluster_gdf.replace(np.nan, 0, inplace=True)

# %%
#### Socio network cluster variables

exec(open("../helper_scripts/generate_socio_reach_columns.py").read())

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
#### Socio socio cluster variables

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
# %%
