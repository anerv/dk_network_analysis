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
hex_reach_component_cols = [c for c in hex_reach_comparison.columns if "pct_diff" in c]
del hex_reach_comparison

hex_corr_variables = (
    density_columns
    + density_steps_columns[1:4]
    + length_relative_columns
    + component_count_columns
    + component_per_km_columns
    + largest_local_component_len_columns
    + reach_columns
    + hex_reach_component_cols
    + ["urban_pct"]
)

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
    + socio_reach_max_columns
    + socio_reach_compare_columns
    + ["urban_pct"]
)

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
