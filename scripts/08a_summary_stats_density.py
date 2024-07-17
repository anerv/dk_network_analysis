# **** SUMMARY STATS: DENSITY ****

# %%
from src import plotting_functions as plot_func
import pandas as pd
import plotly_express as px
import pandas as pd
from IPython.display import display

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/filepaths.py").read())
exec(open("../settings/df_styler.py").read())

plot_func.set_renderer("png")

# %%
exec(open("../helper_scripts/read_density.py").read())

density_data = [density_muni, density_socio, density_hex]

# %%
for i, df in enumerate(density_data):
    print(f"For {aggregation_levels[i]}:")
    display(df.describe().style.pipe(format_style_index))
# %%
## ** TOTAL NETWORK LEVELS ****

lts_1_length = density_muni.lts_1_length.sum()
lts_2_length = density_muni.lts_2_length.sum()
lts_3_length = density_muni.lts_3_length.sum()
lts_4_length = density_muni.lts_4_length.sum()
lts_car_length = density_muni.total_car_length.sum()
total_network_length = density_muni.total_network_length.sum()

network_levels = labels_all

network_lengths = [
    lts_1_length,
    lts_2_length,
    lts_3_length,
    lts_4_length,
    lts_car_length,
    total_network_length,
]

network_shares = [l / total_network_length * 100 for l in network_lengths]

df_single = pd.DataFrame(
    data={
        "network_type": network_levels,
        "length (km)": network_lengths,
        "share (%)": network_shares,
    }
)

df_single.to_csv(filepath_summmary_stats_network_length, index=False)

display(df_single.style.pipe(format_style_no_index))

# %%

network_levels = labels_step_all

lts_1_2_length = lts_1_length + lts_2_length
lts_1_3_length = lts_1_length + lts_2_length + lts_3_length
lts_1_4_length = lts_1_length + lts_2_length + lts_3_length + lts_4_length

network_lengths = [
    lts_1_length,
    lts_1_2_length,
    lts_1_3_length,
    lts_1_4_length,
    lts_car_length,
    total_network_length,
]

network_shares = [l / total_network_length * 100 for l in network_lengths]

df_steps = pd.DataFrame(
    data={
        "network_type": network_levels,
        "length (km)": network_lengths,
        "share (%)": network_shares,
    }
)

df.to_csv(filepath_summmary_stats_network_length_steps, index=False)

display(df.style.pipe(format_style_no_index))

# %%

plotly_labels["network_type"] = "Network type"

filepaths = [filepath_summary_network_length, filepath_summary_network_length_steps]

for i, df in enumerate([df_single, df_steps]):

    new_color_dict = {}
    for e, color in enumerate(lts_color_dict.values()):
        k = df.network_type[e]
        new_color_dict[k] = color

    fig = px.bar(
        df,
        x="network_type",
        y="share (%)",
        color="network_type",
        labels=plotly_labels,
        color_discrete_map=new_color_dict,
    )
    fig.update_layout(template="simple_white")
    fig.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
    fig.update_layout(showlegend=False)
    fig.update_yaxes(visible=False)

    config = {
        "toImageButtonOptions": {
            "format": "svg",  # one of png, svg, jpeg, webp
            "filename": "custom_image",
            "height": 500,
            "width": 700,
            "scale": 6,  # Multiply title/legend/axis/canvas sizes by this factor
        }
    }

    fig.show(config=config)
    fig.write_image(filepaths[i], format="jpg", scale=6)
# %%

# fig = px.bar(
#     df,
#     x="network_type",
#     y="share (%)",
#     color="network_type",
#     labels=plotly_labels,
#     color_discrete_map=new_color_dict,
# )
# fig.update_layout(template="simple_white")
# fig.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
# fig.show()
# fig.write_image(filepath_summary_network_length, format="jpg", scale=6)

# %%
### VALUE RANGES FOR EACH LTS LEVEL FOR EACH AGGREGATION LEVEL

network_levels = labels_all

network_levels_steps = labels_step_all

# For each stepwise level
for a, df in zip(aggregation_levels, density_data):

    min_shares = []
    max_shares = []
    mean_shares = []
    median_shares = []
    std_devs = []

    for i, l in enumerate(network_levels_steps[:-1]):

        min_share = df[length_relative_steps_columns[i]].min()
        max_share = df[length_relative_steps_columns[i]].max()
        mean_share = df[length_relative_steps_columns[i]].mean()
        median_share = df[length_relative_steps_columns[i]].median()
        std_dev = df[length_relative_steps_columns[i]].std()

        min_shares.append(min_share)
        max_shares.append(max_share)
        mean_shares.append(mean_share)
        median_shares.append(median_share)
        std_devs.append(std_dev)

    df = pd.DataFrame(
        index=network_levels_steps[:-1],
        data={
            "min_share": min_shares,
            "mean_share": mean_shares,
            "median_share": median_shares,
            "max_share": max_shares,
            "std_dev": std_devs,
        },
    )

    print(f"At the {a} level:")
    # print(df)

    # print("\n")

    df.to_csv(
        filepath_sum_density_relative_steps + a + ".csv",
        index=True,
    )

    display(df.style.pipe(format_style_index))


# %%
# For each level

for a, df in zip(aggregation_levels, density_data):

    min_shares = []
    max_shares = []
    mean_shares = []
    median_shares = []
    std_devs = []

    for i, l in enumerate(network_levels[:-1]):

        min_share = df[length_relative_columns[i]].min()
        max_share = df[length_relative_columns[i]].max()
        mean_share = df[length_relative_columns[i]].mean()
        median_share = df[length_relative_columns[i]].median()
        std_dev = df[length_relative_columns[i]].std()

        min_shares.append(min_share)
        max_shares.append(max_share)
        mean_shares.append(mean_share)
        median_shares.append(median_share)
        std_devs.append(std_dev)

    df = pd.DataFrame(
        index=network_levels[:-1],
        data={
            "min_share": min_shares,
            "mean_share": mean_shares,
            "median_share": median_shares,
            "max_share": max_shares,
            "std_dev (share)": std_devs,
        },
    )

    df.to_csv(
        filepath_sum_density_relative + a + ".csv",
        index=True,
    )

    print(f"At the {a} level:")

    display(df.style.pipe(format_style_index))


# %%
# How many have more bikeable network than car network?

for a, df in zip(aggregation_levels, density_data):

    print(a, ":")
    more_lts_1 = df[df["lts_1_length"] > df["total_car_length"]].shape[0]
    more_lts_1_2 = df[df["lts_1_2_length"] > df["total_car_length"]].shape[0]
    more_lts_1_3 = df[df["lts_1_3_length"] > df["total_car_length"]].shape[0]
    more_lts_1_4 = df[df["lts_1_4_length"] > df["total_car_length"]].shape[0]

    more_lts_1_percent = more_lts_1 / df.shape[0] * 100
    more_lts_1_2_percent = more_lts_1_2 / df.shape[0] * 100
    more_lts_1_3_percent = more_lts_1_3 / df.shape[0] * 100
    more_lts_1_4_percent = more_lts_1_4 / df.shape[0] * 100

    more_bike_count = [more_lts_1, more_lts_1_2, more_lts_1_3, more_lts_1_4]
    more_bike_share = [
        more_lts_1_percent,
        more_lts_1_2_percent,
        more_lts_1_3_percent,
        more_lts_1_4_percent,
    ]

    df = pd.DataFrame(
        index=network_levels_steps[0:-2],
        data={"more_bike_count": more_bike_count, "more_bike_share": more_bike_share},
    )

    df.to_csv(
        filepath_sum_density_more_bike_count + a + ".csv",
        index=True,
    )

    display(df.style.pipe(format_style_index))


# %%
