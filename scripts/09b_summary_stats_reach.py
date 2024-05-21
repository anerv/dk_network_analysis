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
# Print absolute and relative differences for both reach len and area
# Min, max, average etc.

# Read data

hex_reach = gpd.read_postgis(
    "SELECT * FROM reach.hex_reach", connection, geom_col="geometry"
)

for p in reach_columns:
    hex_reach[p] = hex_reach[p] / 1000  # Convert to km

for p in reach_diff_columns:
    hex_reach[p] = hex_reach[p] / 1000  # Convert to km

hex_reach.replace(0, np.nan, inplace=True)

# %%
labels = [
    "LTS 1",
    "LTS 1-2",
    "LTS 1-3",
    "LTS 1-4",
    "car",
]

for i, r in enumerate(reach_columns):

    print(
        f"The minimum network reach for the {labels[i]} network is: {hex_reach[r].min():_.3f} km."
    )
    print(
        f"The maximum network reach for the {labels[i]} network is: {hex_reach[r].max():_.3f} km."
    )
    print(
        f"The average network reach for the {labels[i]} network is: {hex_reach[r].mean():_.3f} km."
    )
    print(
        f"The median network reach for the {labels[i]} network is: {hex_reach[r].median():_.3f} km."
    )
    print(
        f"The standard deviation in network reach network for: {labels[i]} is {hex_reach[r].std():_.2f} km."
    )

    print("\n")

# %%
for i, r in enumerate(reach_diff_columns):

    print(
        f"The minimum difference in network reach between the car and the {labels[i]} network is: {hex_reach[r].min():_.3f} km."
    )
    print(
        f"The maximum difference in network reach between the car and the {labels[i]} network is: {hex_reach[r].max():_.3f} km."
    )
    print(
        f"The average difference in network reach between the car and the {labels[i]} network is: {hex_reach[r].mean():_.3f} km."
    )
    print(
        f"The median difference in network reach between the car and the {labels[i]} network is: {hex_reach[r].median():_.3f} km."
    )
    print(
        f"The standard deviation in network reach difference between the car and the {labels[i]} network is: {hex_reach[r].std():_.2f} km."
    )

    print("\n")

# %%
for i, r in enumerate(reach_diff_pct_columns):

    print(
        f"The minimum difference in network reach between the car and the {labels[i]} network is: {hex_reach[r].min():_.3f}%."
    )
    print(
        f"The maximum difference in network reach between the car and the {labels[i]} network is: {hex_reach[r].max():_.3f}%."
    )
    print(
        f"The average difference in network reach between the car and the {labels[i]} network is: {hex_reach[r].mean():_.3f}%."
    )
    print(
        f"The median difference in network reach between the car and the {labels[i]} network is: {hex_reach[r].median():_.3f}%."
    )
    print(
        f"The standard deviation in network reach difference between the car and the {labels[i]} network is: {hex_reach[r].std():_.2f}%."
    )

    print("\n")

# %%
