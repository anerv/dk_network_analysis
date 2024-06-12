# %%

from src import db_functions as dbf
from src import plotting_functions as plot_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly_express as px
import pandas as pd
import seaborn as sns

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/df_styler.py").read())
exec(open("../settings/filepaths.py").read())
plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

# %%

#### HEX #####
hex_gdf = gpd.read_postgis(
    "SELECT hex_id, urban_pct, geometry FROM hex_grid;", engine, geom_col="geometry"
)

hex_density = gpd.read_postgis(
    "SELECT * FROM density.density_hex;", engine, geom_col="geometry"
)
hex_density = hex_density[
    ["hex_id"] + density_columns + density_steps_columns[1:4] + length_relative_columns
]
# hex_components = gpd.read_postgis(
#     "SELECT * FROM fragmentation.comp_count_hex;", engine, geom_col="geometry"
# )
hex_components = gpd.read_postgis(
    "SELECT * FROM fragmentation.component_length_hex;", engine, geom_col="geometry"
)
hex_components = hex_components[
    ["hex_id"] + component_count_columns + component_per_km_columns
]

hex_largest_components = gpd.read_postgis(
    "SELECT * FROM fragmentation.hex_largest_components;", engine, geom_col="geometry"
)
hex_largest_components = hex_largest_components[
    largest_local_component_len_columns + ["hex_id"]
]
hex_reach = gpd.read_postgis(
    f"SELECT * FROM reach.hex_reach_{reach_dist};", engine, geom_col="geometry"
)

hex_reach = hex_reach[["hex_id"] + reach_columns]

exec(open("../settings/read_reach_comparison.py").read())

hex_reach_comp_cols = [c for c in hex_reach_comparison.columns if "pct_diff" in c]

hex_reach_comparison = hex_reach_comparison[["hex_id"] + hex_reach_comp_cols]

hex_gdf = hex_gdf.merge(hex_density, on="hex_id", how="left")
hex_gdf = hex_gdf.merge(hex_components, on="hex_id", how="left")
hex_gdf = hex_gdf.merge(hex_reach, on="hex_id", how="left")
hex_gdf = hex_gdf.merge(hex_reach_comparison, on="hex_id", how="left")
hex_gdf = hex_gdf.merge(hex_largest_components, on="hex_id", how="left")

assert hex_gdf.shape[0] == hex_density.shape[0]

# %%
hex_corr_variables = (
    density_columns
    + density_steps_columns[1:4]
    + length_relative_columns
    + component_count_columns
    + component_per_km_columns
    + largest_local_component_len_columns
    + reach_columns
    + hex_reach_comp_cols
    + ["urban_pct"]
)

# %%
display(
    hex_gdf[hex_corr_variables]
    .corr(method="spearman")
    .style.background_gradient(cmap="coolwarm")
)
display(hex_gdf[hex_corr_variables].describe().style.pipe(format_style_index))

# %%
plot_func.plot_correlation(
    hex_gdf,
    hex_corr_variables,
    heatmap_fp=fp_hex_network_heatmap,
    pairplot_fp=fp_hex_network_pairplot,
)
# %%
##### SOCIO #####

socio = gpd.read_postgis(
    "SELECT id, urban_pct, geometry FROM socio;", engine, geom_col="geometry"
)

socio_density = gpd.read_postgis(
    "SELECT * FROM density.density_socio", engine, geom_col="geometry"
)
socio_density = socio_density[
    density_columns + density_steps_columns[1:4] + length_relative_columns + ["id"]
]

socio_components = gpd.read_postgis(
    "SELECT * FROM fragmentation.component_length_socio;", engine, geom_col="geometry"
)
socio_components = socio_components[
    component_count_columns + component_per_km_columns + ["id"]
]

socio_largest_components = gpd.read_postgis(
    "SELECT * FROM fragmentation.socio_largest_component;", engine, geom_col="geometry"
)

socio_largest_components = socio_largest_components[
    socio_largest_component_columns_median + ["id"]
]

socio_reach = gpd.read_postgis(
    f"SELECT * FROM reach.socio_reach_{reach_dist}", engine, geom_col="geometry"
)

socio_reach = socio_reach[socio_reach_median_columns + socio_reach_max_columns + ["id"]]

socio_reach_comparison = gpd.read_postgis(
    "SELECT * FROM reach.socio_reach_comparison", engine, geom_col="geometry"
)
exec(open("../settings/read_reach_comparison.py").read())
hex_reach_comp_cols = [c for c in hex_reach_comparison.columns if "pct_diff" in c]
socio_reach_compare_columns = [c + "_median" for c in hex_reach_comp_cols]
socio_reach_comparison = socio_reach_comparison[socio_reach_compare_columns + ["id"]]

socio_gdf = socio.merge(socio_density, on="id", how="left")
socio_gdf = socio_gdf.merge(socio_components, on="id", how="left")
socio_gdf = socio_gdf.merge(socio_largest_components, on="id", how="left")
socio_gdf = socio_gdf.merge(socio_reach, on="id", how="left")
socio_gdf = socio_gdf.merge(socio_reach_comparison, on="id", how="left")

assert socio_density.shape[0] == socio_gdf.shape[0]

socio_corr_variables = (
    density_columns
    + density_steps_columns[1:4]
    + length_relative_columns
    + component_count_columns
    + component_per_km_columns
    + socio_largest_component_columns_median
    + socio_reach_median_columns
    + socio_reach_max_columns
    + socio_reach_compare_columns
    + ["urban_pct"]
)
# %%
display(
    socio_gdf[socio_corr_variables]
    .corr(method="spearman")
    .style.background_gradient(cmap="coolwarm")
)
display(socio_gdf[socio_corr_variables].describe().style.pipe(format_style_index))

# %%

# SOCIO
plot_func.plot_correlation(
    socio_gdf,
    socio_corr_variables,
    heatmap_fp=fp_socio_network_heatmap,
    pairplot_fp=fp_socio_network_pairplot,
)

# %%
