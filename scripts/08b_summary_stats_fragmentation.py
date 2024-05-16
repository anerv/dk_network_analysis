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

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)


# %%
component_size_all = pd.read_sql("SELECT * FROM component_size_all;", engine)
component_size_1 = pd.read_sql("SELECT * FROM component_size_1;", engine)
component_size_2 = pd.read_sql("SELECT * FROM component_size_2;", engine)
component_size_3 = pd.read_sql("SELECT * FROM component_size_3;", engine)
component_size_4 = pd.read_sql("SELECT * FROM component_size_4;", engine)
component_size_car = pd.read_sql("SELECT * FROM component_size_car;", engine)

compt_count_muni = pd.read_sql("SELECT * FROM comp_count_muni;", engine)
compt_count_socio = pd.read_sql("SELECT * FROM comp_count_socio;", engine)
compt_count_h3 = pd.read_sql("SELECT * FROM comp_count_h3;", engine)

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

for c, n in zip(comp_dfs, network_levels_steps):

    print(f"The {n} network is divided into {len(c):_} components.")

    print(
        f"The smallest component for the {n} network is {c['bike_length'].min()/1000:_.4f} km long."
    )

    print(
        f"The average component size for the {n} network is {c['bike_length'].mean()/1000:_.2f} km."
    )

    print(
        f"The largest component for the {n} network is {c['bike_length'].max()/1000:_.2f} km."
    )

    print("\n")
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

    for i, l in enumerate(network_levels_steps):

        min_comp_count = df[component_count_columns[i]].min()
        mean_comp_count = df[component_count_columns[i]].mean()
        max_comp_count = df[component_count_columns[i]].max()

        print(
            f"At the {a} level, the minimum component count for the {l} network is {min_comp_count}."
        )
        print(
            f"At the {a} level, the mean component count for the {l} network is {mean_comp_count:.0f}."
        )
        print(
            f"At the {a} level, the maximum component count for the {l} network is {max_comp_count}."
        )

    print("\n")

# %%
