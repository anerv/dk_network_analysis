# %%

import pandas as pd
import numpy as np
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

df.to_csv(fp_summary_stats_reach, index=True)

print(f"Reach summary stats for reach at distance {reach_dist} km:")
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

print(
    f"Summary stats for reach differences between bike and car reach at distance {reach_dist} km:"
)
df.to_csv(fp_summary_stats_reach_diff, index=True)

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


df.to_csv(fp_summary_stats_reach_diff_pct, index=True)

print(
    f"Summary stats for reach differences between bike and car reach at distance {reach_dist} km:"
)

display(df.style.pipe(format_style_index))
# %%
# Increases in reach at different distance thresholds

exec(open("../helper_scripts/read_reach_comparison.py").read())

columns = [c for c in hex_reach_comparison.columns if "pct_diff" in c]

display(hex_reach_comparison[columns].describe().T.style.pipe(format_style_index))

# %%
selected_columns = [c for c in columns if "2_5" in c or "5_10" in c]

display(
    hex_reach_comparison[selected_columns].describe().T.style.pipe(format_style_index)
)
# %%

combis = [(1, 5), (5, 10), (10, 15)]

for c in combis:

    for i, n in enumerate(network_levels_step):
        no_impro = len(
            hex_reach_comparison[
                hex_reach_comparison[f"{n}_pct_diff_{c[0]}_{c[1]}"] == 0
            ]
        )

        total_count = len(
            hex_reach_comparison[hex_reach_comparison[f"{n}_reach_{c[0]}"] > 0]
        )

        print(
            f"{no_impro:,.0f} ({no_impro/total_count*100:.2f}%) of {labels_step[i]} cells have no improvements in reach when increasing distance from {c[0]} to {c[1]} km"
        )

    print("\n")
# %%
