# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly_express as px
import pandas as pd

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/filepaths.py").read())
exec(open("../settings/df_styler.py").read())

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)


# %%
component_size_all = pd.read_sql(
    "SELECT * FROM fragmentation.component_size_all;", engine
)
component_size_1 = pd.read_sql("SELECT * FROM fragmentation.component_size_1;", engine)
component_size_2 = pd.read_sql("SELECT * FROM fragmentation.component_size_2;", engine)
component_size_3 = pd.read_sql("SELECT * FROM fragmentation.component_size_3;", engine)
component_size_4 = pd.read_sql("SELECT * FROM fragmentation.component_size_4;", engine)
component_size_car = pd.read_sql(
    "SELECT * FROM fragmentation.component_size_car;", engine
)

compt_count_muni = pd.read_sql("SELECT * FROM fragmentation.comp_count_muni;", engine)
compt_count_socio = pd.read_sql("SELECT * FROM fragmentation.comp_count_socio;", engine)
compt_count_h3 = pd.read_sql("SELECT * FROM fragmentation.comp_count_h3;", engine)

# %%

comp_dfs = [
    component_size_all,
    component_size_1,
    component_size_2,
    component_size_3,
    component_size_4,
    component_size_car,
]

network_levels_steps = [
    "full",
    "LTS 1",
    "LTS 1-2",
    "LTS 1-3",
    "LTS 1-4",
    "car",
]

comp_count = []
smallest_comp_size = []
mean_comp_size = []
median_comp_size = []
max_comp_size = []
std_dev_comp_size = []

for c, n in zip(comp_dfs, network_levels_steps):

    comp_count.append(len(c))
    smallest_comp_size.append(c["bike_length"].min())
    mean_comp_size.append(c["bike_length"].mean())
    median_comp_size.append(c["bike_length"].median())
    max_comp_size.append(c["bike_length"].max())
    std_dev_comp_size.append(c["bike_length"].std())

df = pd.DataFrame(
    index=network_levels_steps,
    data={
        "component count": comp_count,
        "smallest component size (km)": smallest_comp_size,
        "mean component size (km)": mean_comp_size,
        "median component size (km)": median_comp_size,
        "largest component size (km)": max_comp_size,
        "standard deviation of component size (km)": std_dev_comp_size,
    },
)

df.to_csv(filepath_sum_fragmentation_summary_stats, index=True)
display(df.style.pipe(format_style_index))
# %%
aggregation_levels = ["municipal", "local", "grid"]

comp_dfs = [compt_count_muni, compt_count_socio, compt_count_h3]

network_levels_steps = [
    "LTS 1",
    "LTS 1-2",
    "LTS 1-3",
    "LTS 1-4",
    "car",
    "full",
]

for a, df in zip(aggregation_levels, comp_dfs):

    min_comp_counts = []
    mean_comp_counts = []
    median_comp_counts = []
    max_comp_counts = []
    std_comp_counts = []

    for i, l in enumerate(network_levels_steps):

        min_comp_counts.append(df[component_count_columns[i]].min())
        mean_comp_counts.append(df[component_count_columns[i]].mean())
        median_comp_counts.append(df[component_count_columns[i]].median())
        max_comp_counts.append(df[component_count_columns[i]].max())
        std_comp_counts.append(df[component_count_columns[i]].std())

    df = pd.DataFrame(
        data={
            "min": min_comp_counts,
            "mean": mean_comp_counts,
            "median": median_comp_counts,
            "max": max_comp_counts,
            "std": std_comp_counts,
        }
    )

    df.to_csv(
        filepath_sum_fragmentation_component_count + a + ".csv",
        index=False,
    )

    print(f"Summary statistics for local component count at the {a} level:")

    display(df.style.pipe(format_style_no_index))

# %%
