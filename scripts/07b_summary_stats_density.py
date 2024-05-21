#

# **** SUMMARY STATS: DENSITY ****

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

plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)


# %%
density_muni = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM density_municipality;",
    engine,
    crs=crs,
    geom_col="geometry",
)
density_muni.replace(0, np.nan, inplace=True)

density_socio = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM density_socio;",
    engine,
    crs=crs,
    geom_col="geometry",
)

density_socio.replace(0, np.nan, inplace=True)

density_h3 = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM density_h3;",
    engine,
    crs=crs,
    geom_col="geometry",
)

density_h3.replace(0, np.nan, inplace=True)

density_data = [density_muni, density_socio, density_h3]

for df in density_data:

    for c in length_relative_columns:
        df[c] = df[c] * 100

    for c in length_relative_steps_columns[1:-1]:
        df[c] = df[c] * 100


# %%

## ** TOTAL NETWORK LEVELS ****

total_network_length = density_muni.total_network_length.sum()
lts_1_length = density_muni.lts_1_length.sum()
lts_2_length = density_muni.lts_2_length.sum()
lts_3_length = density_muni.lts_3_length.sum()
lts_4_length = density_muni.lts_4_length.sum()
lts_car_length = density_muni.total_car_length.sum()

network_levels = [
    "full",
    "LTS 1",
    "LTS 2",
    "LTS 3",
    "LTS 4",
    "car",
]
network_lengths = [
    total_network_length,
    lts_1_length,
    lts_2_length,
    lts_3_length,
    lts_4_length,
    lts_car_length,
]

for n, l in zip(network_levels, network_lengths):

    print(
        f"The total length of the {n} network is {l:_.2f} km or {(l/total_network_length*100):.2f}%"
    )


# %%
### VALUE RANGES FOR EACH LTS LEVEL FOR EACH AGGREGATION LEVEL

aggregation_levels = ["municipal", "local", "grid"]


network_levels = [
    "full",
    "LTS 1",
    "LTS 2",
    "LTS 3",
    "LTS 4",
    "car",
]

network_levels_steps = [
    "full",
    "LTS 1",
    "LTS 1-2",
    "LTS 1-3",
    "LTS 1-4",
    "car",
]


# For each stepwise level
for a, df in zip(aggregation_levels, density_data):

    for i, l in enumerate(network_levels_steps[1:]):

        min_share = df[length_relative_steps_columns[i]].min()
        max_share = df[length_relative_steps_columns[i]].max()
        mean_share = df[length_relative_steps_columns[i]].mean()
        median_share = df[length_relative_steps_columns[i]].median()
        print(
            f"At the {a} level, the {l} network is between {min_share:.2f} % and {max_share:.2f} % of the full network length. 
            The average share is {mean_share:.2f}% and the median share is {median_share:.2f}%."
        )

    print("\n")

# %%
# For each level

for a, df in zip(aggregation_levels, density_data):

    for i, l in enumerate(network_levels[1:]):

        min_share = df[length_relative_columns[i]].min()
        max_share = df[length_relative_columns[i]].max()
        mean_share = df[length_relative_columns[i]].mean()
        median_share = df[length_relative_columns[i]].median()
        print(
            f"At the {a} level, the {l} network is between {min_share:.2f} % and {max_share:.2f}% of the full network length. 
            The average share is {mean_share:.2f}% and the median share is {median_share:.2f}%."
        )

    print("\n")


# %%
# How many have more bikeable network than car network?

for a, df in zip(aggregation_levels, density_data):
    more_lts_1 = df[df["lts_1_length"] > df["total_car_length"]].shape[0]
    more_lts_1_2 = df[df["lts_1_2_length"] > df["total_car_length"]].shape[0]
    more_lts_1_3 = df[df["lts_1_3_length"] > df["total_car_length"]].shape[0]
    more_lts_1_4 = df[df["lts_1_4_length"] > df["total_car_length"]].shape[0]

    more_lts_1_percent = more_lts_1 / df.shape[0] * 100
    more_lts_1_2_percent = more_lts_1_2 / df.shape[0] * 100
    more_lts_1_3_percent = more_lts_1_3 / df.shape[0] * 100
    more_lts_1_4_percent = more_lts_1_4 / df.shape[0] * 100

    print(
        f"At the {a} level, {more_lts_1_percent:.2f}% have more LTS 1 network than car network."
    )
    print(
        f"At the {a} level, {more_lts_1_2_percent:.2f}% have more LTS 1-2 network than car network."
    )
    print(
        f"At the {a} level, {more_lts_1_3_percent:.2f}% have more LTS 1-3 network than car network."
    )
    print(
        f"At the {a} level, {more_lts_1_4_percent:.2f}% have more LTS 1-4 network than car network."
    )


# %%
