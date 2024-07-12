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
# Read data
exec(open("../helper_scripts/read_reach.py").read())

hex_reach.replace(0, np.nan, inplace=True)

hex_reach.describe().style.pipe(format_style_index)
# %%
labels = labels_step

min_reach = []
mean_reach = []
median_reach = []
std_reach = []
max_reach = []

for i, r in enumerate(reach_columns):

    min_reach.append(hex_reach[r].min())
    mean_reach.append(hex_reach[r].mean())
    median_reach.append(hex_reach[r].median())
    std_reach.append(hex_reach[r].std())
    max_reach.append(hex_reach[r].max())

df = pd.DataFrame(
    index=labels,
    data={
        "min (km)": min_reach,
        "mean (km)": mean_reach,
        "median (km)": median_reach,
        "max (km)": max_reach,
        "std (km)": std_reach,
    },
)

df.to_csv(filepath_summary_stats_reach, index=True)

display(df.style.pipe(format_style_index))

# %%

min_reach_diff = []
mean_reach_diff = []
median_reach_diff = []
std_reach_diff = []
max_reach_diff = []


for i, r in enumerate(reach_diff_columns):

    min_reach_diff.append(hex_reach[r].min())
    mean_reach_diff.append(hex_reach[r].mean())
    median_reach_diff.append(hex_reach[r].median())
    std_reach_diff.append(hex_reach[r].std())
    max_reach_diff.append(hex_reach[r].max())

df = pd.DataFrame(
    index=labels[:-1],
    data={
        "min diff (km)": min_reach_diff,
        "mean diff (km)": mean_reach_diff,
        "median diff (km)": median_reach_diff,
        "max diff (km)": max_reach_diff,
        "std diff (km)": std_reach_diff,
    },
)

df.to_csv(filepath_summary_stats_reach_diff, index=True)

display(df.style.pipe(format_style_index))
# %%

min_reach_diff_pct = []
mean_reach_diff_pct = []
median_reach_diff_pct = []
std_reach_diff_pct = []
max_reach_diff_pct = []

for i, r in enumerate(reach_diff_pct_columns):

    min_reach_diff_pct.append(hex_reach[r].min())
    mean_reach_diff_pct.append(hex_reach[r].mean())
    median_reach_diff_pct.append(hex_reach[r].median())
    std_reach_diff_pct.append(hex_reach[r].std())
    max_reach_diff_pct.append(hex_reach[r].max())

df = pd.DataFrame(
    index=labels[:-1],
    data={
        "min diff (%)": min_reach_diff_pct,
        "mean diff (%)": mean_reach_diff_pct,
        "median diff (%)": median_reach_diff_pct,
        "max diff (%)": max_reach_diff_pct,
        "std diff (%)": std_reach_diff_pct,
    },
)


df.to_csv(filepath_summary_stats_reach_diff_pct, index=True)

display(df.style.pipe(format_style_index))
# %%
# Increases in reach at different distance thresholds

exec(open("../helper_scripts/read_reach_comparison.py").read())

columns = [c for c in hex_reach_comparison.columns if "pct_diff" in c]

display(hex_reach_comparison[columns].describe().style.pipe(format_style_index))

lts_1_d5_10 = len(
    hex_reach_comparison[hex_reach_comparison["lts_1_pct_diff_5_10"] == 0]
)
lts_1_d10_15 = len(
    hex_reach_comparison[hex_reach_comparison["lts_1_pct_diff_10_15"] == 0]
)
lts_1_2_d5_10 = len(
    hex_reach_comparison[hex_reach_comparison["lts_1_2_pct_diff_5_10"] == 0]
)
lts_1_2_d10_15 = len(
    hex_reach_comparison[hex_reach_comparison["lts_1_2_pct_diff_10_15"] == 0]
)
lts_1_3_d5_10 = len(
    hex_reach_comparison[hex_reach_comparison["lts_1_3_pct_diff_5_10"] == 0]
)
lts_1_3_d10_15 = len(
    hex_reach_comparison[hex_reach_comparison["lts_1_3_pct_diff_10_15"] == 0]
)
lts_1_4_d5_10 = len(
    hex_reach_comparison[hex_reach_comparison["lts_1_4_pct_diff_5_10"] == 0]
)
lts_1_4_d10_15 = len(
    hex_reach_comparison[hex_reach_comparison["lts_1_4_pct_diff_10_15"] == 0]
)
car_d5_10 = len(hex_reach_comparison[hex_reach_comparison["car_pct_diff_5_10"] == 0])
car_d10_15 = len(hex_reach_comparison[hex_reach_comparison["car_pct_diff_10_15"] == 0])

values = [
    (lts_1_d5_10, lts_1_d10_15),
    (lts_1_2_d10_15, lts_1_2_d10_15),
    (lts_1_3_d5_10, lts_1_3_d10_15),
    (lts_1_4_d5_10, lts_1_4_d10_15),
    (car_d5_10, car_d10_15),
]

for l, n, v in zip(labels_step, network_levels, values):

    total_count = len(hex_reach_comparison[hex_reach_comparison[f"{n}_reach_5"] > 0])
    print(
        f"{v[0]/total_count*100:.2f}% of {l} cells have no improvements in reach when increasing distance from 5 to 10 km"
    )
    print(
        f"{v[1]/total_count*100:.2f}% of {l} cells have no improvements in reach when increasing distance from 10 to 15 km"
    )

    print("\n")

# %%
