# %%
import numpy as np

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())

# %%
exec(open("../helper_scripts/read_hex_results.py").read())

exec(open("../helper_scripts/read_reach_comparison.py").read())

reach_compare_columns = [c for c in hex_reach_comparison.columns if "pct_diff" in c]

reach_compare_columns = [
    c for c in reach_compare_columns if any(r in c for r in reach_comparisons)
]

hex_gdf.replace(np.nan, 0, inplace=True)

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
