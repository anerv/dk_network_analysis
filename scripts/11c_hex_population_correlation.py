# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
import matplotlib.pyplot as plt
import seaborn as sns
import math

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/df_styler.py").read())
exec(open("../settings/filepaths.py").read())
plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)
# %%
exec(open("../helper_scripts/read_hex_results.py").read())


# %%
all_density_columns = [
    density_columns,
    density_steps_columns,
    length_relative_columns,
    length_relative_steps_columns,
]

all_labels = [labels_all, labels_step_all, labels_pct, labels_pct_step]

axis_labels = ["density (km/sqkm)", "density (km/sqkm)", "%", "%"]

subplot_titles = [
    "density",
    "density_steps",
    "length_relative",
    "length_relative_steps",
]

for i, columns in enumerate(all_density_columns[:-2]):

    fig, axes = plt.subplots(
        nrows=math.ceil(len(columns) / 2), ncols=2, figsize=(15, 15)
    )

    axes = axes.flatten()
    if len(columns) % 2 != 0:
        fig.delaxes(axes[-1])

    for e, c in enumerate(columns):

        sub_fig = sns.scatterplot(
            data=hex_gdf,
            x="population_density",
            y=c,
            hue="urban_pct",
            alpha=0.5,
            # palette="pink",
            ax=axes[e],
        )
        sub_fig.get_legend().set_title(
            "Urban area (%)", prop={"size": pdict["legend_fs"]}
        )

        sub_fig.set(
            xscale="log",
            xlabel="People per sqkm",
            ylabel=all_labels[i][e] + " " + axis_labels[i],
        )

    plt.savefig(fp_hex_pop_corr + f"{subplot_titles[i]}.png")
    plt.show()


# %%

all_reach_columns = [reach_columns]

all_labels = [labels_step]

axis_labels = ["reach (km)"]

subplot_titles = ["reach"]

for i, columns in enumerate(all_reach_columns):

    fig, axes = plt.subplots(
        nrows=math.ceil(len(columns) / 2), ncols=2, figsize=(15, 15)
    )

    axes = axes.flatten()
    if len(columns) % 2 != 0:
        fig.delaxes(axes[-1])

    for e, c in enumerate(columns):

        sub_fig = sns.scatterplot(
            data=hex_gdf,
            x="population_density",
            y=c,
            hue="urban_pct",
            alpha=0.5,
            # palette="pink",
            ax=axes[e],
        )
        sub_fig.get_legend().set_title(
            "Urban area (%)", prop={"size": pdict["legend_fs"]}
        )

        sub_fig.set(
            xscale="log",
            xlabel="People per sqkm",
            ylabel=all_labels[i][e] + " " + axis_labels[i],
        )

    plt.savefig(fp_hex_pop_corr + f"{subplot_titles[i]}.png")
    plt.show()

# %%
# exec(open("../helper_scripts/read_reach_comparison.py").read())

# hex_reach_comparison = hex_gdf[["hex_id", "population_density", "urban_pct"]].merge(
#     hex_reach_comparison, on="hex_id", how="inner", suffixes=("", "_y")
# )
# # %%
# comparison_types = ["1_5"]  #  "5_10", "1_15"

# compare_cols = []

# for n in network_levels_step:

#     for c in comparison_types:
#         compare_cols.append(f"{n}_pct_diff_{c}")

# all_reach_columns = [compare_cols]

# all_labels = [labels_step]

# axis_labels = ["difference (%)"]

# subplot_titles = ["reach_pct_diff_1_5"]

# for i, columns in enumerate(all_reach_columns):

#     fig, axes = plt.subplots(
#         nrows=math.ceil(len(columns) / 2), ncols=2, figsize=(15, 15)
#     )

#     axes = axes.flatten()
#     if len(columns) % 2 != 0:
#         fig.delaxes(axes[-1])

#     for e, c in enumerate(columns):

#         sub_fig = sns.scatterplot(
#             data=hex_reach_comparison,
#             x="population_density",
#             y=c,
#             hue="urban_pct",
#             alpha=0.5,
#             # palette="pink",
#             ax=axes[e],
#         )
#         sub_fig.get_legend().set_title(
#             "Urban area (%)", prop={"size": pdict["legend_fs"]}
#         )

#         sub_fig.set(
#             xscale="log",
#             xlabel="People per sqkm",
#             ylabel=all_labels[i][e] + " " + axis_labels[i],
#         )

#     plt.savefig(fp_hex_pop_corr + f"{subplot_titles[i]}.png")
#     plt.show()

# %%
