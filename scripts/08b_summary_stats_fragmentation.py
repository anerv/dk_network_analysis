# %%
import pandas as pd
from IPython.display import display
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

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
df_density = pd.read_csv(filepath_summmary_stats_network_length_steps)

merged_df = pd.merge(
    df[["component count", "largest component size (km)"]].reset_index(),
    df_density[["length (km)", "network_type"]],
    left_on="index",
    right_on="network_type",
)

merged_df.drop(columns=["index"], inplace=True)

merged_df["lcc_share"] = (
    merged_df["largest component size (km)"] / merged_df["length (km)"] * 100
)

display(merged_df.style.pipe(format_style_no_index))

sns.scatterplot(
    data=merged_df,
    x="length (km)",
    y="component count",
    hue="network_type",
    palette=lts_color_dict.values(),
)

# %%

# Create a figure and primary axis
fig, ax1 = plt.subplots(figsize=(8, 8))

colors = {}
for e, color in enumerate(lts_color_dict.values()):
    k = merged_df.network_type[e]
    colors[k] = color

# Define network types and colors
network_types = merged_df["network_type"].unique()

# Create a secondary y-axis
ax2 = ax1.twinx()

# Plot 'length' values on the primary y-axis
for network_type in network_types:
    subset = merged_df[merged_df["network_type"] == network_type]
    ax1.scatter(
        [0] * len(subset),
        subset["length (km)"],
        color=colors[network_type],
        label=f"{network_type}",
    )

# ax1.set_ylabel("Length")
ax1.tick_params(
    axis="y",
)

# Plot 'component count' values on the secondary y-axis
for network_type in network_types:
    subset = merged_df[merged_df["network_type"] == network_type]
    ax2.scatter(
        [1] * len(subset),
        subset["component count"],
        color=colors[network_type],
    )

# ax2.set_ylabel("Component Count")
ax2.tick_params(
    axis="y",
)

# Combine legends from both axes
handles1, labels1 = ax1.get_legend_handles_labels()
ax1.legend(handles1, labels1, bbox_to_anchor=(0.99, 1), loc="upper right")

legend = ax1.get_legend()
if legend:
    legend.set_frame_on(False)

# Set x-ticks to be the network types
ax1.set_xticks([0, 1])
ax1.set_xticklabels(
    ["Length (km)", "Component Count"],
)

# Manually draw dotted lines between marks of the same color
for network_type in network_types:
    subset = merged_df[merged_df["network_type"] == network_type]
    ax1.plot(
        [subset["length (km)"].iloc[0], subset["component count"].iloc[0]],
        color=colors[network_type],
        linestyle="dotted",
    )
    ax2.plot(
        [subset["length (km)"].iloc[0], subset["component count"].iloc[0]],
        color=colors[network_type],
        linestyle="dotted",
    )

# Find the maximum value for the component count
# max_component_count = merged_df["component count"].max()

# Set the y-axis limit for ax2 to be the maximum component count
# ax2.set_ylim(0, max_component_count)

# Title and show plot
# plt.title("Network length and component count", fontdict={"size": 12})
plt.tight_layout()
sns.despine(left=False, right=False, bottom=True)
plt.savefig(
    filepath_summary_compare_length_components, bbox_inches="tight", dpi=pdict["dpi"]
)
plt.show()

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
