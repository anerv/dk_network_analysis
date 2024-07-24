# %%
from src import plotting_functions as plot_func
import geopandas as gpd
import pandas as pd
from IPython.display import display

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/df_styler.py").read())
exec(open("../settings/filepaths.py").read())
plot_func.set_renderer("png")

# %%
k_values = [k_muni, k_socio, k_hex]
spatial_weights_values = [f"queen_{k}" for k in k_values]
rename_dicts = [
    rename_index_dict_density,
    rename_index_dict_fragmentation,
    rename_index_dict_reach,
]

metrics = ["density", "fragmentation", "reach"]
# %%

# DENSITY AND FRAGMENTATION

for i, metric in enumerate(metrics[:-1]):

    dfs = []

    for e, a in enumerate(aggregation_levels):

        fp = (
            fp_spatial_auto_base
            + f"{metric}/{a}/global_moransi_{spatial_weights_values[e]}.json"
        )

        df = plot_func.process_plot_moransi(fp, metric, a, rename_dicts[i])

        dfs.append(df)

    joined_df = pd.concat(dfs, axis=1)

    display(joined_df.style.pipe(format_style_index))


# %%
# FRAGMENTATION COMPONENT SIZE

fp = (
    fp_spatial_auto_fragmentation
    + f"hexgrid/global_moransi_largest_component_size_{spatial_weights_values[e]}.json"
)
df = plot_func.process_plot_moransi(
    fp=fp,
    metric="largest component size",
    aggregation_level="hexgrid",
    rename_dict=rename_index_dict_largest_comp,
)

display(df.style.pipe(format_style_index))


# %%
# REACH

fp = fp_spatial_auto_reach + f"hexgrid/global_moransi_{spatial_weights_values[2]}.json"
df = plot_func.process_plot_moransi(
    fp=fp,
    metric="network reach",
    aggregation_level="hexgrid",
    rename_dict=rename_dicts[2],
)

display(df.style.pipe(format_style_index))

# %%

# DENSITY AND FRAGMENTATION
for i, metric in enumerate(metrics[:-1]):

    for e, a in enumerate(aggregation_levels):

        fp = fp_spatial_auto_base + f"{metric}/{a}/lisas.parquet"

        plot_func.compare_lisa_results(
            fp, metric, a, rename_dicts[i], format_style_index
        )


# LARGEST COMPONENT SIZE
fp = fp_spatial_auto_fragmentation + f"hexgrid/lisas_largest_component_size_.parquet"

plot_func.compare_lisa_results(
    fp,
    metric="largest component size",
    aggregation_level=aggregation_levels[-1],
    rename_dict=rename_index_dict_largest_comp,
    format_style=format_style_index,
)


# REACH
fp = fp_spatial_auto_reach + f"hexgrid/lisas.parquet"

plot_func.compare_lisa_results(
    fp,
    metric="network reach",
    aggregation_level=aggregation_levels[-1],
    rename_dict=rename_dicts[2],
    format_style=format_style_index,
)

# %%
# Make maps of significant LISA clusters

import math


def plot_significant_lisa_clusters_all(
    gdf,
    plot_columns,
    titles,
    figsize=pdict["fsmap_subs"],
    colors=["#d7191c", "#fdae61", "#abd9e9", "#2c7bb6", "lightgrey"],
    fp=None,
    dpi=pdict["dpi"],
):
    custom_cmap = plot_func.color_list_to_cmap(colors)

    row_num = math.ceil(len(plot_columns) / 2)

    fig, axes = plt.subplots(nrows=row_num, ncols=2, figsize=figsize)

    axes = axes.flatten()

    if len(plot_columns) % 2 != 0:
        fig.delaxes(axes[-1])

    for i, p in enumerate(plot_columns):

        ax = axes[i]

        gdf.plot(
            column=p,
            categorical=True,
            legend=True,
            linewidth=0.0,
            ax=ax,
            edgecolor="none",
            legend_kwds={
                "frameon": False,
                "loc": "upper right",
                "bbox_to_anchor": (0.95, 0.95),
                # "fontsize": pdict["legend_fs"],
            },
            cmap=custom_cmap,
        )

        ax.set_axis_off()
        ax.set_title(titles[i], fontsize=pdict["title_fs"])

    fig.tight_layout()

    if fp:
        fig.savefig(fp, bbox_inches="tight", dpi=dpi)


# %%
# Density
gdf_density = gpd.read_parquet(fp_spatial_auto_density + "hexgrid/lisas.parquet")

titles = [
    "LTS 1 density",
    "LTS 2 density",
    "LTS 3 density",
    "LTS 4 density",
    "Car density",
    "Total network density",
]

plot_columns = [d + "_q" for d in density_columns]

fp = fp_spatial_auto_density + "hexgrid/lisas_significant_clusters_density.png"

plot_significant_lisa_clusters_all(
    gdf_density, plot_columns=plot_columns, titles=titles, fp=fp
)
#
# length relative

titles = [
    "LTS 1 %",
    "LTS 2 %",
    "LTS 3 %",
    "LTS 4 %",
    "Car %",
]

plot_columns = [d + "_q" for d in length_relative_columns]

fp = fp_spatial_auto_density + "hexgrid/lisas_significant_clusters_length_relative.png"

plot_significant_lisa_clusters_all(
    gdf_density,
    plot_columns=plot_columns,
    titles=titles,
    fp=fp,
)

del gdf_density
# %%
# Largest component length
gdf_fragmentation = gpd.read_parquet(
    fp_spatial_auto_fragmentation + "hexgrid/lisas_largest_component_size_.parquet"
)
plot_columns = [d + "_q" for d in largest_local_component_len_columns]

fp = (
    fp_spatial_auto_fragmentation
    + "hexgrid/lisas_significant_clusters_largest_component_len.png"
)

titles = [
    "Max component length - LTS 1",
    "Max component length - LTS 1-2",
    "Max component length - LTS 1-3",
    "Max component length - LTS 1-4",
    "Max component length - car",
]

plot_significant_lisa_clusters_all(
    gdf_fragmentation,
    plot_columns=plot_columns,
    titles=titles,
    fp=fp,
)

del gdf_fragmentation

# %%
# Reach
gdf_reach = gpd.read_parquet(fp_spatial_auto_reach + "hexgrid/lisas.parquet")

plot_columns = [d + "_q" for d in reach_columns]

titles = ["LTS 1 reach", "LTS 1-2 reach", "LTS 1-3 reach", "LTS 1-4 reach", "Car reach"]

fp = fp_spatial_auto_reach + "hexgrid/lisas_significant_clusters_reach.png"

plot_significant_lisa_clusters_all(
    gdf_reach,
    plot_columns=plot_columns,
    titles=titles,
    fp=fp,
)

del gdf_reach
# %%
