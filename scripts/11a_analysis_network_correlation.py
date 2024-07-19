# %%

from src import db_functions as dbf
from src import plotting_functions as plot_func
from IPython.display import display

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/df_styler.py").read())
exec(open("../settings/filepaths.py").read())
plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

# %%
exec(open("../helper_scripts/read_hex_results.py").read())

exec(open("../helper_scripts/read_reach_comparison.py").read())
reach_compare_columns = [c for c in hex_reach_comparison.columns if "pct_diff" in c]

reach_compare_columns = [
    c for c in reach_compare_columns if any(r in c for r in reach_comparisons)
]
hex_corr_variables = (
    density_columns
    + density_steps_columns[1:4]
    + length_relative_columns
    + component_count_columns
    + component_per_km_columns
    + largest_local_component_len_columns
    + reach_columns
    + reach_compare_columns
    + ["urban_pct"]
)

hex_gdf = hex_gdf[hex_corr_variables]

rename_hex_dict = (
    rename_index_dict_density
    | rename_index_dict_fragmentation
    | rename_index_dict_largest_comp
    | rename_index_dict_reach
    | rename_hex_reach_dict
)
rename_hex_dict["urban_pct"] = "Urban %"
hex_gdf.rename(rename_hex_dict, inplace=True, axis=1)

display(hex_gdf.corr(method="spearman").style.background_gradient(cmap="coolwarm"))
display(hex_gdf.describe().style.pipe(format_style_index))

# %%
# HEX PLOT

plot_func.plot_correlation(
    hex_gdf,
    hex_gdf.columns,
    heatmap_fp=fp_hex_network_heatmap,
    pairplot_fp=fp_hex_network_pairplot,
    mask=False,
    corner=False,
    pairplot=False,
)
# %%
##### SOCIO #####

exec(open("../helper_scripts/prepare_socio_network_corr_data.py").read())

# generate socio reach comparison columns
exec(open("../helper_scripts/generate_socio_reach_columns.py").read())

socio_corr_variables = (
    density_columns
    + density_steps_columns[1:4]
    + length_relative_columns
    + component_count_columns
    + component_per_km_columns
    + socio_largest_component_columns_median
    + socio_reach_median_columns
    # + socio_reach_max_columns
    + socio_reach_compare_columns
    + ["urban_pct"]
)

socio_gdf = socio_gdf[socio_corr_variables]

rename_socio_dict = (
    rename_index_dict_density
    | rename_index_dict_fragmentation
    | rename_index_dict_largest_comp
    | rename_index_dict_reach
    | rename_socio_reach_dict
)
rename_socio_dict["urban_pct"] = "Urban %"
socio_gdf.rename(rename_socio_dict, inplace=True, axis=1)

display(socio_gdf.corr(method="spearman").style.background_gradient(cmap="coolwarm"))
display(socio_gdf.describe().style.pipe(format_style_index))

# %%

# SOCIO PLOT
plot_func.plot_correlation(
    socio_gdf,
    socio_gdf.columns,
    heatmap_fp=fp_socio_network_heatmap,
    pairplot_fp=fp_socio_network_pairplot,
    mask=False,
    corner=False,
    pairplot=False,
)

# %%
