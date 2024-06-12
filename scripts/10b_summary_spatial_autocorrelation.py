# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
from src import analysis_functions as analysis_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import plotly.express as px
from IPython.display import display

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/df_styler.py").read())
exec(open("../settings/filepaths.py").read())
plot_func.set_renderer("png")

# %%
k_values = [k_muni, k_socio, k_hex]
spatial_weights_values = [f"queen_{k}" for k in k_values]
rename_dicts = [
    rename_index_dict_density,
    rename_index_dict_fragmentation,
    rename_index_dict_reach,
]

metrics = ["density", "fragmentation", "reach"]
# %%

# DENSITY AND FRAGMENTATION

for i, metric in enumerate(metrics[:-1]):

    dfs = []

    for e, a in enumerate(aggregation_levels):

        fp = (
            fp_spatial_auto_base
            + f"{metric}/{a}/global_moransi_{spatial_weights_values[e]}.json"
        )

        df = plot_func.process_plot_moransi(fp, metric, a, rename_dicts[i])

        dfs.append(df)

    joined_df = pd.concat(dfs, axis=1)

    display(joined_df.style.pipe(format_style_index))


# %%
# FRAGMENTATION COMPONENT SIZE

fp = (
    fp_spatial_auto_fragmentation
    + f"hexgrid/global_moransi_largest_comp_size_{spatial_weights_values[e]}.json"
)
df = plot_func.process_plot_moransi(
    fp=fp,
    metric="largest component size",
    aggregation_level="hexgrid",
    rename_dict=rename_index_dict_largest_comp,
)

display(df.style.pipe(format_style_index))


# %%
# REACH

fp = fp_spatial_auto_reach + f"hexgrid/global_moransi_{spatial_weights_values[e]}.json"
df = plot_func.process_plot_moransi(
    fp=fp,
    metric="network reach",
    aggregation_level="hexgrid",
    rename_dict=rename_dicts[2],
)

display(df.style.pipe(format_style_index))

# %%

# DENSITY AND FRAGMENTATION
for i, metric in enumerate(metrics[:-1]):

    for e, a in enumerate(aggregation_levels):

        fp = fp_spatial_auto_base + f"{metric}/{a}/lisas.parquet"

        plot_func.compare_lisa_results(
            fp, metric, a, rename_dicts[i], format_style_index
        )


# LARGEST COMPONENT SIZE
fp = fp_spatial_auto_fragmentation + f"hexgrid/lisas_largest_comp_size_.parquet"

plot_func.compare_lisa_results(
    fp,
    metric="largest component size",
    aggregation_level=aggregation_levels[-1],
    rename_dict=rename_index_dict_largest_comp,
    format_style=format_style_index,
)


# REACH
fp = fp_spatial_auto_reach + f"hexgrid/lisas.parquet"

plot_func.compare_lisa_results(
    fp,
    metric="network reach",
    aggregation_level=aggregation_levels[-1],
    rename_dict=rename_dicts[2],
    format_style=format_style_index,
)

# %%
