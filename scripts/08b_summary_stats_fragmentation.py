# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly_express as px
import pandas as pd
from IPython.display import display

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/filepaths.py").read())
exec(open("../settings/df_styler.py").read())

# %%
exec(open("../helper_scripts/read_component_sizes.py").read())

exec(open("../helper_scripts/read_components.py").read())
# %%

component_dfs = [
    component_size_1,
    component_size_1_2,
    component_size_1_3,
    component_size_1_4,
    component_size_car,
    component_size_all,
]

network_levels_steps = labels_step_all

component_count = []
smallest_component_size = []
mean_component_size = []
median_component_size = []
max_component_size = []
std_dev_component_size = []

for c, n in zip(component_dfs, network_levels_steps):

    component_count.append(len(c))
    smallest_component_size.append(c["infra_length"].min())
    mean_component_size.append(c["infra_length"].mean())
    median_component_size.append(c["infra_length"].median())
    max_component_size.append(c["infra_length"].max())
    std_dev_component_size.append(c["infra_length"].std())

df = pd.DataFrame(
    index=network_levels_steps,
    data={
        "component count": component_count,
        "smallest component size (km)": smallest_component_size,
        "mean component size (km)": mean_component_size,
        "median component size (km)": median_component_size,
        "largest component size (km)": max_component_size,
        "standard deviation of component size (km)": std_dev_component_size,
    },
)

df.to_csv(filepath_sum_fragmentation_summary_stats, index=True)
display(df.style.pipe(format_style_index))
# %%

component_dfs = [muni_components, socio_components, hex_components]

network_levels_steps = labels_step_all

for a, df in zip(aggregation_levels, component_dfs):

    min_component_counts = []
    mean_component_counts = []
    median_component_counts = []
    max_component_counts = []
    std_component_counts = []

    for i, l in enumerate(network_levels_steps):

        min_component_counts.append(df[component_count_columns[i]].min())
        mean_component_counts.append(df[component_count_columns[i]].mean())
        median_component_counts.append(df[component_count_columns[i]].median())
        max_component_counts.append(df[component_count_columns[i]].max())
        std_component_counts.append(df[component_count_columns[i]].std())

    df = pd.DataFrame(
        index=network_levels_steps,
        data={
            "min": min_component_counts,
            "mean": mean_component_counts,
            "median": median_component_counts,
            "max": max_component_counts,
            "std": std_component_counts,
        },
    )

    df.to_csv(
        filepath_sum_fragmentation_component_count + a + ".csv",
        index=False,
    )

    print(f"Summary statistics for local component count at the {a} level:")

    display(df.style.pipe(format_style_index))

# %%
