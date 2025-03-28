import matplotlib as mpl
from matplotlib import cm, colors
import matplotlib.pyplot as plt
import matplotlib_inline.backend_inline
import contextily as cx
from mpl_toolkits.axes_grid1 import make_axes_locatable
import math
import mapclassify
import seaborn as sns
import numpy as np
import pandas as pd
import geopandas as gpd
from collections import Counter
from IPython.display import display
import plotly.express as px
from matplotlib.colors import to_hex
from matplotlib.colors import ListedColormap
from matplotlib_scalebar.scalebar import ScaleBar
import matplotlib.patches as patches
from matplotlib.ticker import FormatStrFormatter
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
from generativepy.color import Color
from PIL import ImageColor
from src import analysis_functions as analysis_func

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())

# Clustering functions based on https://geographicdata.science/book/notebooks/10_clustering_and_regionalization.html#

# Gini functions based on https://geographicdata.science/book/notebooks/09_spatial_inequality.html


def plot_outliers_zoom(
    gdf_outliers,
    gdf_background,
    cmap,
    xmin,
    xmax,
    ymin,
    ymax,
    cluster_label="socio_label",
    background_color="lightgrey",
    attr=None,
    plot_title=None,
    filepath=None,
    bbox_to_anchor=(0.99, 1),
    fontsize=12,
):

    fig, ax = plt.subplots(figsize=pdict["fsmap"])

    gdf_background.plot(ax=ax, color=background_color, alpha=0.5, linewidth=0.0)

    gdf_outliers.plot(
        ax=ax,
        column=cluster_label,
        cmap=cmap,
        legend=True,
        legend_kwds={
            "frameon": False,
            "bbox_to_anchor": bbox_to_anchor,
            "loc": "upper left",
            "fontsize": fontsize,
        },
        linewidth=0.3,
    )

    ax.set_axis_off()

    if attr is not None:
        cx.add_attribution(ax=ax, text="(C) " + attr, font_size=fontsize)
        txt = ax.texts[-1]
        txt.set_position([0.99, 0.012])
        txt.set_ha("right")
        txt.set_va("bottom")

    ax.add_artist(
        ScaleBar(
            dx=1,
            units="m",
            dimension="si-length",
            length_fraction=0.15,
            width_fraction=0.002,
            location="lower left",
            box_alpha=0.5,
            font_properties={"size": fontsize},
        )
    )

    ax.axis([xmin, xmax, ymin, ymax])

    if plot_title is not None:
        ax.set_title(plot_title, fontsize=pdict["map_title_fs"])

    if filepath is not None:
        fig.savefig(filepath, dpi=pdict["dpi"])

    plt.show()
    plt.close()


def plot_above_below_mean(
    gdf,
    socio_label,
    socio_column="socio_label",
    outlier_above_column="outlier_above",
    outlier_below_column="outlier_below",
    fp=None,
):

    below_mean = gdf[
        (gdf[socio_column] == socio_label) & (gdf[outlier_below_column] == True)
    ]
    above_mean = gdf[
        (gdf[socio_column] == socio_label) & (gdf[outlier_above_column] == True)
    ]

    _, axes = plt.subplots(1, 2, figsize=(10, 5))

    axes = axes.flatten()

    if len(below_mean) > 0:

        gdf.plot(ax=axes[0], color="lightgrey", alpha=0.5, linewidth=0.1)

        below_mean.plot(ax=axes[0], color="blue", linewidth=0.1)

        axes[0].axis("off")

        axes[0].title.set_text(f"Outliers below mean")

    elif len(below_mean) == 0:
        axes[0].axis("off")

    if len(above_mean) > 0:

        gdf.plot(ax=axes[1], color="lightgrey", alpha=0.5, linewidth=0.1)

        above_mean.plot(ax=axes[1], color="red", linewidth=0.1)

        axes[1].title.set_text(f"Outliers above mean")

        axes[1].axis("off")

    elif len(above_mean) == 0:
        axes[1].axis("off")

    plt.tight_layout()

    plt.suptitle(f"{socio_label}")

    if fp:
        plt.savefig(fp, dpi=pdict["dpi"])

    plt.show()


def make_combined_outlier_plot(
    gdf,
    socio_column,
    color_dict,
    outlier_above_column="outlier_above",
    outlier_below_column="outlier_below",
    fp=None,
    fontsize=12,
):

    active_labels = list(
        gdf.loc[gdf[outlier_above_column] == True][socio_column].unique()
    )
    active_labels.sort()
    colors = [color_dict[l] for l in active_labels]
    cmap = color_list_to_cmap(colors)

    _, axes = plt.subplots(1, 2, figsize=pdict["fsmap"])

    axes = axes.flatten()
    ax_above = axes[0]
    ax_below = axes[1]

    gdf.plot(ax=ax_above, color="lightgrey", alpha=0.5, linewidth=0.0)

    gdf[gdf[outlier_above_column] == True].plot(
        categorical=True,
        ax=ax_above,
        column=socio_column,
        linewidth=0.0,
        legend=True,
        legend_kwds={"frameon": False, "fontsize": fontsize},
        cmap=cmap,
    )

    ax_above.set_axis_off()

    active_labels = list(
        gdf.loc[gdf[outlier_below_column] == True][socio_column].unique()
    )
    active_labels.sort()
    colors = [color_dict[l] for l in active_labels]
    cmap = color_list_to_cmap(colors)

    gdf.plot(ax=ax_below, color="lightgrey", alpha=0.5, linewidth=0.0)

    gdf[gdf[outlier_below_column] == True].plot(
        categorical=True,
        ax=ax_below,
        column=socio_column,
        linewidth=0.0,
        legend=True,
        legend_kwds={"frameon": False, "fontsize": fontsize},
        cmap=cmap,
    )
    ax_below.set_axis_off()

    ax_above.add_artist(
        ScaleBar(
            dx=1,
            units="m",
            dimension="si-length",
            length_fraction=0.15,
            width_fraction=0.002,
            location="lower left",
            box_alpha=0.5,
            font_properties={"size": fontsize},
        )
    )

    plt.tight_layout()

    if fp:
        plt.savefig(fp, dpi=pdict["dpi"])

    plt.show()


def plot_concentration_curves_combined(
    ax,
    data,
    opportunities,
    population,
    income,
    oppportunity_labels,
    general_opportunity_label,
    opportunity_colors,
    fontsize=12,
):
    """
    Plot cumulative share of infrastructure vs. cumulative share of population ordered by income.

    Parameters:
    - data (pd.DataFrame): The dataset.
    - opportunity (str): Column name representing the opportunity measure (e.g. access to low stress infrastructure).
    - population (str): Column name representing the population.
    - income (str): Column name representing socioeconic variable (e.g. income).
    - title (str): Title for the plot.
    """
    # Sort data by income
    data = data.sort_values(by=income)

    # Calculate cumulative shares
    data["pop_share"] = data[population] / data[population].sum()
    data["cum_pop_share"] = data["pop_share"].cumsum()

    for i, opportunity in enumerate(opportunities):

        data[f"opp_share_{i}"] = data[opportunity] / data[opportunity].sum()
        data[f"cum_opp_share_{i}"] = data[f"opp_share_{i}"].cumsum()

        # Plot
        ax.plot(
            data["cum_pop_share"],
            data[f"cum_opp_share_{i}"],
            label=oppportunity_labels[i],
            color=opportunity_colors[i],
            linewidth=2,
        )

    ax.plot(
        [0, 1],
        [0, 1],
        linestyle="--",
        color="black",
        label="Perfect equality",
    )

    ax.tick_params(axis="both", which="major", labelsize=fontsize)
    ax.set_xlabel(f"Cumulative share of population", fontsize=fontsize)
    ax.set_ylabel(f"Cumulative share of {general_opportunity_label}", fontsize=fontsize)

    # UPDATE legend label for opportunity:
    handles, labels = ax.get_legend_handles_labels()

    for i, oppportunity_label in enumerate(oppportunity_labels):

        labels[i] = (
            oppportunity_label[0].capitalize() + oppportunity_label[1:]
        )  # oppportunity_label.capitalize()
        ax.legend(handles, labels, frameon=False, fontsize=fontsize)


def plot_concentration_curves_subplots(
    ax,
    data,
    opportunity,
    population,
    income,
    oppportunity_label,
    opportunity_color="#882255",
    fontsize=12,
):
    """
    Plot cumulative share of infrastructure vs. cumulative share of population ordered by income.

    Parameters:
    - data (pd.DataFrame): The dataset.
    - opportunity (str): Column name representing the opportunity measure (e.g. access to low stress infrastructure).
    - population (str): Column name representing the population.
    - income (str): Column name representing socioeconic variable (e.g. income).
    - title (str): Title for the plot.
    """
    # Sort data by income
    data = data.sort_values(by=income)

    # Calculate cumulative shares
    data["pop_share"] = data[population] / data[population].sum()
    data["cum_pop_share"] = data["pop_share"].cumsum()

    data["opp_share"] = data[opportunity] / data[opportunity].sum()
    data["cum_opp_share"] = data["opp_share"].cumsum()

    # Plot
    ax.plot(
        data["cum_pop_share"],
        data["cum_opp_share"],
        label=opportunity,
        color=opportunity_color,
        linewidth=2,
    )
    ax.plot(
        [0, 1],
        [0, 1],
        linestyle="--",
        color="black",
        label="Perfect equality",
    )
    ax.set_xlabel(f"Cumulative share of population", fontsize=fontsize)
    ax.set_ylabel(f"Cumulative share of {oppportunity_label}", fontsize=fontsize)

    # UPDATE legend label for opportunity:
    handles, labels = ax.get_legend_handles_labels()
    labels[0] = (
        oppportunity_label[0].capitalize() + oppportunity_label[1:]
    )  # oppportunity_label.capitalize()
    ax.legend(handles, labels, frameon=False, fontsize=fontsize)


def plot_concentration_curves(
    data,
    opportunity,
    population,
    income,
    income_label,
    oppportunity_label,
    opportunity_color="#882255",
    fp=None,
):
    """
    Plot cumulative share of infrastructure vs. cumulative share of population ordered by income.

    Parameters:
    - data (pd.DataFrame): The dataset.
    - opportunity (str): Column name representing the opportunity measure (e.g. access to low stress infrastructure).
    - population (str): Column name representing the population.
    - income (str): Column name representing socioeconic variable (e.g. income).
    - title (str): Title for the plot.
    """
    # Sort data by income
    data = data.sort_values(by=income)

    # Calculate cumulative shares
    data["pop_share"] = data[population] / data[population].sum()
    data["cum_pop_share"] = data["pop_share"].cumsum()

    data["opp_share"] = data[opportunity] / data[opportunity].sum()
    data["cum_opp_share"] = data["opp_share"].cumsum()

    # Plot
    plt.figure(figsize=pdict["fsbar"])
    plt.plot(
        data["cum_pop_share"],
        data["cum_opp_share"],
        label=opportunity,
        color=opportunity_color,
        linewidth=2,
    )
    plt.plot([0, 1], [0, 1], linestyle="--", color="black", label="Perfect equality")
    plt.xlabel(f"Cumulative share of population - ordered by {income_label}")
    plt.ylabel(f"Cumulative share of {oppportunity_label}")

    # UPDATE legend label for opportunity:
    handles, labels = plt.gca().get_legend_handles_labels()
    labels[0] = (
        oppportunity_label[0].capitalize() + oppportunity_label[1:]
    )  # oppportunity_label.capitalize()
    plt.legend(handles, labels, frameon=False)
    plt.grid()
    sns.despine()
    plt.tight_layout()

    if fp:
        plt.savefig(fp, dpi=pdict["dpi"])

    plt.show()

    plt.close()


def plot_lorenz(
    cumulative_share,
    share_of_population,
    x_label,
    y_label,
    figsize=(6, 6),
    fp=None,
    fontsize=12,
):

    _, ax = plt.subplots(figsize=figsize)

    ax.plot(
        share_of_population, cumulative_share, color="#882255", label="Lorenz Curve"
    )

    ax.plot((0, 1), (0, 1), color="black", linestyle="--", label="Perfect Equality")

    ax.set_xlabel(f"Cumulative share of {x_label}", fontsize=fontsize)

    ax.set_ylabel(f"Cumulative share of {y_label}", fontsize=fontsize)

    ax.legend(frameon=False, fontsize=fontsize)

    sns.despine()

    plt.tight_layout()

    if fp:

        plt.savefig(fp, dpi=pdict["dpi"])

    plt.show()
    plt.close()


def plot_lorenz_combined(
    ax,
    cumulative_share,
    share_of_population,
    x_label,
    y_label,
    color="#882255",
    fontsize=12,
):
    y_label_elements = y_label.split()

    y_label_part_1 = y_label_elements[0] + " " + y_label_elements[1]
    y_label_part_2 = " ".join(y_label_elements[2:])

    ax.plot(share_of_population, cumulative_share, color=color, label="Lorenz Curve")

    ax.plot((0, 1), (0, 1), color="black", linestyle="--", label="Perfect Equality")

    ax.set_xlabel(f"Cumulative share of {x_label}", fontsize=fontsize)

    # ax.set_ylabel(
    #     f"Cumulative share of {y_label_part_1} " + r"$\bf{" + y_label_part_2 + "}$",
    #     fontsize=fontsize,
    # )
    ax.set_ylabel(
        f"Cumulative share of {y_label_part_1} " + r"\textbf{" + y_label_part_2 + "}",
        fontsize=fontsize,
    )

    ax.tick_params(axis="both", which="major", labelsize=fontsize - 2)

    sns.despine(bottom=True, left=True)

    ax.legend(frameon=False, fontsize=fontsize)


# def plot_lorenz_combined(
#     ax,
#     cumulative_share,
#     share_of_population,
#     x_label,
#     y_label,
#     color="#882255",
#     fontsize=12,
# ):
#     ax.plot(share_of_population, cumulative_share, color=color, label="Lorenz Curve")

#     ax.plot((0, 1), (0, 1), color="black", linestyle="--", label="Perfect Equality")

#     ax.set_xlabel(f"Cumulative share of {x_label}", fontsize=fontsize)

#     ax.set_ylabel(f"Cumulative share of {y_label}", fontsize=fontsize)

#     ax.tick_params(axis="both", which="major", labelsize=fontsize - 2)

#     sns.despine(bottom=True, left=True)

#     ax.legend(frameon=False, fontsize=fontsize)


def plot_components_zoom(
    gdf,
    component_col,
    cmap,
    fp,
    xmin,
    ymin,
    xmax,
    ymax,
    linewidht=1.5,
    alpha=pdict["alpha"],
):

    gdf_subset = gdf.cx[xmin:xmax, ymin:ymax]

    fig, ax = plt.subplots(figsize=pdict["fsmap"])

    ax.set_axis_off()

    gdf_subset.plot(
        column=component_col,
        categorical=True,
        legend=False,
        ax=ax,
        cmap=cmap,
        linewidth=linewidht,
        alpha=alpha,
    )

    cx.add_attribution(
        ax=ax, text="(C) " + pdict["map_attr"], font_size=pdict["map_legend_fs"]
    )
    txt = ax.texts[-1]
    txt.set_position([0.99, 0.01])
    txt.set_ha("right")
    txt.set_va("bottom")

    ax.add_artist(
        ScaleBar(
            dx=1,
            units="m",
            dimension="si-length",
            length_fraction=0.15,
            width_fraction=0.002,
            location="lower left",
            box_alpha=0.5,
            font_properties={"size": pdict["map_legend_fs"]},
        )
    )

    ax.set_title("Disconnected components", fontsize=pdict["map_title_fs"])

    fig.savefig(fp, dpi=pdict["dpi"])

    plt.tight_layout()


def plot_poly_zoom(
    poly_gdf,
    plot_col,
    plot_title,
    filepath,
    cmap,
    xmin,
    xmax,
    ymin,
    ymax,
    alpha=pdict["alpha"],
    edgecolor="white",
    linewidth=0.1,
    figsize=pdict["fsmap"],
    dpi=pdict["dpi"],
    legend=True,
    use_norm=False,
    norm_min=None,
    norm_max=None,
    attr=pdict["map_attr"],
    plot_na=True,
    legend_kwds={"fmt": "{:.0f}"},
):

    fig, ax = plt.subplots(1, figsize=figsize)

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="3.5%", pad="1%")

    if use_norm is True:

        cbnorm = colors.Normalize(vmin=norm_min, vmax=norm_max)

        poly_gdf.plot(
            cax=cax,
            ax=ax,
            column=plot_col,
            legend=legend,
            legend_kwds=legend_kwds,
            edgecolor=edgecolor,
            linewidth=linewidth,
            alpha=alpha,
            norm=cbnorm,
            cmap=cmap,
            missing_kwds={
                "color": pdict["nodata"],
                "label": "No data",
                "alpha": pdict["alpha_nodata"],
            },
        )

    else:

        poly_gdf.plot(
            cax=cax,
            ax=ax,
            column=plot_col,
            edgecolor=edgecolor,
            linewidth=linewidth,
            legend=legend,
            legend_kwds=legend_kwds,
            alpha=alpha,
            cmap=cmap,
            missing_kwds={
                "color": pdict["nodata"],
                "label": "No data",
                "alpha": pdict["alpha_nodata"],
            },
        )

    if legend and use_norm is False:
        remove_colorbar_outline(
            cmap, fig, cax, poly_gdf[plot_col].min(), poly_gdf[plot_col].max()
        )

    if legend and use_norm is True:
        remove_colorbar_outline(cmap, fig, cax, norm_min, norm_max)

    if plot_na and len(poly_gdf.loc[poly_gdf[plot_col].isna()]) > 0:
        # Creates a rectangular patch for each contaminant, using the colors above
        patch_list = []
        label = "No data"
        color = pdict["nodata"]
        patch_list.append(
            patches.Patch(
                facecolor=color,
                label=label,
                alpha=pdict["alpha_nodata"],
                linewidth=0,
                edgecolor="none",
            )
        )

        # Creates a legend with the list of patches above.
        ax.legend(
            handles=patch_list,
            fontsize=pdict["map_legend_fs"],
            loc="lower left",
            bbox_to_anchor=(0.3, -0.01),
            # title="Litologia",
            title_fontsize=pdict["legend_title_fs"],
            frameon=True,
        )

    ax.set_axis_off()

    if attr is not None:
        cx.add_attribution(ax=ax, text="(C) " + attr, font_size=pdict["map_legend_fs"])
        txt = ax.texts[-1]
        txt.set_position([0.99, 0.012])
        txt.set_ha("right")
        txt.set_va("bottom")

    ax.add_artist(
        ScaleBar(
            dx=1,
            units="m",
            dimension="si-length",
            length_fraction=0.15,
            width_fraction=0.002,
            location="lower left",
            box_alpha=0.5,
            font_properties={"size": pdict["map_legend_fs"]},
        )
    )

    ax.axis([xmin, xmax, ymin, ymax])
    ax.set_title(plot_title, fontsize=pdict["map_title_fs"])

    fig.savefig(filepath + ".png", dpi=dpi)

    plt.show()
    plt.close()


def plot_zoom_categorical(
    gdf,
    plot_col,
    cmap,
    fp,
    xmin,
    xmax,
    ymin,
    ymax,
    alpha=pdict["alpha"],
    fontsize=10,
    add_attribution=True,
    attr_position=(0.99, 0.01),
):

    fig, ax = plt.subplots(1, 1, figsize=pdict["fsmap"])
    ax.set_axis_off()
    gdf.plot(
        column=plot_col,
        categorical=True,
        legend=True,
        legend_kwds={
            "frameon": False,
            "bbox_to_anchor": (0.99, 1),
            "loc": "upper left",
            "fontsize": fontsize,
        },
        ax=ax,
        cmap=cmap,
        linewidth=0.1,
        alpha=alpha,
    )

    if add_attribution:
        cx.add_attribution(ax=ax, text="(C) " + pdict["map_attr"], font_size=fontsize)
        txt = ax.texts[-1]
        txt.set_position([attr_position[0], attr_position[1]])
        txt.set_ha("right")
        txt.set_va("bottom")

    ax.add_artist(
        ScaleBar(
            dx=1,
            units="m",
            dimension="si-length",
            length_fraction=0.15,
            width_fraction=0.002,
            location="lower left",
            box_alpha=0.5,
            font_properties={"size": fontsize},
        )
    )

    ax.axis([xmin, xmax, ymin, ymax])

    plt.tight_layout()

    fig.savefig(fp, dpi=pdict["dpi"])


def make_cluster_map(
    gdf, plot_col, cmap, fp, add_attribution=True, attr=pdict["map_attr"], fontsize=10
):

    fig, ax = plt.subplots(1, 1, figsize=pdict["fsmap"])
    ax.set_axis_off()
    gdf.plot(
        column=plot_col,
        categorical=True,
        legend=True,
        legend_kwds={
            "frameon": False,
            "bbox_to_anchor": (0.99, 1),
            "fontsize": fontsize,
        },
        ax=ax,
        cmap=cmap,
        linewidth=0.1,
    )

    if add_attribution:
        cx.add_attribution(ax=ax, text="(C) " + attr)
        txt = ax.texts[-1]
        txt.set_position([0.99, 0.01])
        txt.set_ha("right")
        txt.set_va("bottom")
        txt.set_fontsize(fontsize)

    ax.add_artist(
        ScaleBar(
            dx=1,
            units="m",
            dimension="si-length",
            length_fraction=0.15,
            width_fraction=0.002,
            location="lower left",
            box_alpha=0,
            font_properties={"size": fontsize},
        )
    )

    plt.tight_layout()

    fig.savefig(fp, dpi=pdict["dpi"])


def plot_significant_lisa_clusters_all(
    gdf,
    plot_columns,
    titles,
    figsize=pdict["fsmap_subs"],
    colors=["#d7191c", "#fdae61", "#abd9e9", "#2c7bb6", "lightgrey"],
    fp=None,
    dpi=pdict["dpi"],
    legend_pos=(0.95, 0.95),
):
    custom_cmap = color_list_to_cmap(colors)

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
                "bbox_to_anchor": legend_pos,
                "fontsize": pdict["legend_fs"],
            },
            cmap=custom_cmap,
        )

        ax.set_axis_off()
        ax.set_title(titles[i], fontsize=pdict["title_fs"])

    fig.tight_layout()

    if fp:
        fig.savefig(fp, bbox_inches="tight", dpi=dpi)


def color_list_to_cmap(color_list):
    colors = {i: color_list[i] for i in range(len(color_list))}
    return ListedColormap([t[1] for t in sorted(colors.items())])


def style_cluster_means(cluster_means, cmap="coolwarm"):
    """
    Apply background gradient styling to a DataFrame representing cluster means.

    Parameters:
    - cluster_means (pd.DataFrame): The DataFrame containing the cluster means.
    - cmap (str, optional): The colormap to use for the background gradient. Default is "coolwarm".

    Returns:
    - None

    Example:
    >>> style_cluster_means(cluster_means, cmap="viridis")
    """

    styler = cluster_means.style
    styler_dict = {}
    for i in cluster_means.index:
        styler_dict[i] = "coolwarm"

    for idx, cmap in styler_dict.items():
        styler = styler.background_gradient(
            cmap=cmap, subset=pd.IndexSlice[idx, :], axis=1
        )

        cluster_means_styled = cluster_means.style.background_gradient(
            cmap=cmap, subset=pd.IndexSlice[:, :], axis=1
        )

    display(cluster_means_styled)


def plot_clustering(gdf, cluster_col, fp, figsize=pdict["fsmap"], cmap=pdict["cat"]):
    """
    Plot clustering results on a GeoDataFrame.

    Parameters:
    gdf (GeoDataFrame): The GeoDataFrame containing the data to be plotted.
    cluster_col (str): The name of the column in the GeoDataFrame that represents the clustering results.
    fp (str): The file path where the plot will be saved.
    figsize (tuple, optional): The size of the figure.
    cmap (str or Colormap, optional): The colormap to be used for the plot. Defaults to pdict["cat"].

    Returns:
    None
    """

    _, ax = plt.subplots(1, figsize=figsize)

    gdf.plot(
        column=cluster_col,
        categorical=True,
        legend=True,
        linewidth=0,
        ax=ax,
        cmap=cmap,
    )

    ax.set_axis_off()

    plt.savefig(fp)

    plt.show()


def plot_cluster_sizes(cluster_sizes, cluster_areas, fp):
    """
    Plots the cluster sizes and areas as a bar chart.

    Args:
        cluster_sizes (list): A list of integers representing the sizes of each cluster.
        cluster_areas (list): A list of floats representing the areas of each cluster.
        fp (str): The file path to save the plot.

    Returns:
        None
    """
    __, ax = plt.subplots(1, figsize=(15, 10))
    area_tracts = pd.DataFrame({"No. Tracts": cluster_sizes, "Area": cluster_areas})
    area_tracts = area_tracts * 100 / area_tracts.sum()
    ax = area_tracts.plot.bar(ax=ax)
    ax.set_xlabel("Cluster labels")
    ax.set_ylabel("Percentage by cluster")

    plt.savefig(fp)

    plt.show()


def plot_cluster_variable_distributions(
    gdf,
    cluster_col,
    cluster_variables,
    fp,
    palette=pdict["cat"],
):
    """
    Plot the distributions of cluster variables using kernel density estimation (KDE).

    Parameters:
    gdf (GeoDataFrame): The GeoDataFrame containing the data.
    cluster_col (str): The name of the column representing the clusters.
    cluster_variables (list): The list of variables to plot.
    fp (str): The file path to save the plot.
    palette (str, optional): The color palette to use for the plot.".

    Returns:
    None
    """
    tidy_df = gdf.set_index(cluster_col)
    tidy_df = tidy_df[cluster_variables]
    tidy_df = tidy_df.stack()
    tidy_df = tidy_df.reset_index()
    tidy_df = tidy_df.rename(columns={"level_1": "Attribute", 0: "Values"})

    sns.set_theme(font_scale=1.5, style="white")

    facets = sns.FacetGrid(
        data=tidy_df,
        col="Attribute",
        hue=cluster_col,
        sharey=False,
        sharex=False,
        aspect=2,
        col_wrap=3,
        palette=palette,
    )
    fig = facets.map(
        sns.kdeplot,
        "Values",
        fill=False,
        warn_singular=False,
        multiple="stack",
    )

    fig.add_legend(title="Cluster")
    fig.savefig(fp)


def map_all_cluster_results(
    gdf, cluster_columns, titles, fp, figsize=(30, 25), cmap=pdict["cat"]
):
    """
    Plot all cluster results on a map.

    Args:
        gdf (GeoDataFrame): The GeoDataFrame containing the spatial data.
        cluster_columns (list): List of column names representing the cluster results.
        titles (list): List of titles for each cluster result plot.
        fp (str): Filepath to save the plot.
        figsize (tuple, optional): Figure size. Defaults to (30, 25).
        cmap (str, optional): Colormap name.
    """

    _, axs = plt.subplots(1, len(cluster_columns), figsize=figsize)

    for i, cluster_col in enumerate(cluster_columns):

        gdf.plot(
            column=cluster_col,
            categorical=True,
            cmap=cmap,
            legend=True,
            linewidth=0,
            ax=axs[i],
        )

        axs[i].set_axis_off()
        axs[i].set_title(titles[i])

    plt.savefig(fp)
    plt.show()


def get_min_max_vals(gdf, columns):
    min_vals = [gdf[p].min() for p in columns]
    max_vals = [gdf[p].max() for p in columns]
    return min(min_vals), max(max_vals)


def compare_lisa_results(fp, metric, aggregation_level, rename_dict, format_style):
    """
    Compare LISA (Local Indicators of Spatial Association) results.

    Parameters:
    - fp (str): Filepath of the data file.
    - metric (str): The metric to compare.
    - aggregation_level (str): The level of aggregation.
    - rename_dict (dict): A dictionary to rename the columns.
    - format_style (function): A function to format the output style.

    Returns:
    None
    """

    summary = {}

    gdf = gpd.read_parquet(fp)

    cols = [
        c for c in gdf.columns if c not in ["geometry", "hex_id", "municipality", "id"]
    ]

    for c in cols:
        summary[c] = gdf[c].value_counts().to_dict()

    dfs = []
    for c in summary.keys():
        df = pd.DataFrame.from_dict(summary[c], orient="index", columns=[c])

        dfs.append(df)

    joined_df = pd.concat(dfs, axis=1)

    new_col_names = [c.strip("_q") for c in joined_df.columns]
    new_columns_dict = {}
    for z, c in enumerate(joined_df.columns):
        new_columns_dict[c] = new_col_names[z]
    joined_df.rename(columns=new_columns_dict, inplace=True)

    joined_df.rename(columns=rename_dict, inplace=True)

    print(f"LISA summary for {metric} at {aggregation_level}")

    display(joined_df.style.pipe(format_style))

    long_df = joined_df.reset_index().melt(
        id_vars="index", var_name="Metric", value_name="Count"
    )

    # Create the stacked bar chart
    fig = px.bar(
        long_df,
        x="Metric",
        y="Count",
        color="index",
        title=f"LISA for {metric} at {aggregation_level}",
        labels={"index": "LISA Type", "Count": "Count", "Metric": "Metric"},
        hover_data=["Metric", "index", "Count"],
        color_discrete_map={
            "Non-Significant": "#d3d3d3",
            "HH": "#d62728",
            "HL": "#e6bbad",
            "LH": "#add8e6",
            "LL": "#1f77b4",
        },
    )

    # Show the figure
    fig.show()


def process_plot_moransi(fp, metric, aggregation_level, rename_dict):
    """
    Process and plot Moran's I for a given metric at a specified aggregation level.

    Args:
        fp (str): The file path of the JSON file containing the data.
        metric (str): The name of the metric.
        aggregation_level (str): The aggregation level.
        rename_dict (dict): A dictionary to rename the index of the DataFrame.

    Returns:
        pandas.DataFrame: The processed DataFrame.

    """
    df = pd.read_json(
        fp,
        orient="index",
    )

    df.rename(columns={0: f"morans I: {aggregation_level}"}, inplace=True)

    df.rename(
        index=rename_dict,
        inplace=True,
    )

    fig = px.bar(
        df.reset_index(),
        x="index",
        y=f"morans I: {aggregation_level}",
        title=f"Moran's I for {metric} at {aggregation_level}",
        labels={
            "index": "Metric type",
        },
    )

    fig.show()

    plt.close()

    return df


def plot_correlation(
    df,
    corr_columns,
    method="spearman",
    pair_plot_type="reg",
    diag_kind="kde",
    corner=True,
    pairplot=True,
    mask=True,
    pair_plot_x_log=False,
    pair_plot_y_log=False,
    heatmap_fp=None,
    pairplot_fp=None,
):
    """
    Plots the correlation between columns in a DataFrame and generates a heatmap and pairplot.

    Parameters:
        df (pandas.DataFrame): The DataFrame containing the data.
        corr_columns (list): The list of column names to calculate correlation and plot.
        pair_plot_type (str, optional): The type of plot for the pairplot. Defaults to "reg".
        diag_kind (str, optional): The type of plot for the diagonal subplots in the pairplot. Defaults to "kde".
        corner (bool, optional): Whether to plot only the lower triangle of the heatmap and pairplot. Defaults to True.
        pair_plot_x_log (bool, optional): Whether to set the x-axis of the pairplot to a logarithmic scale. Defaults to False.
        pair_plot_y_log (bool, optional): Whether to set the y-axis of the pairplot to a logarithmic scale. Defaults to False.
        heatmap_fp (str, optional): The file path to save the heatmap plot. Defaults to None.
        pairplot_fp (str, optional): The file path to save the pairplot. Defaults to None.

    Returns:
        None
    """

    df_corr = df[corr_columns].corr(method=method)

    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(11, 9))

    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(230, 20, as_cmap=True)

    if mask:
        # Generate a mask for the upper triangle
        mask = np.triu(np.ones_like(df_corr, dtype=bool))
        hm = sns.heatmap(
            df_corr,
            mask=mask,
            cmap=cmap,
            center=0,
            square=True,
            linewidths=0.5,
            cbar_kws={"shrink": 0.5},
        )

    else:
        hm = sns.heatmap(
            df_corr,
            cmap=cmap,
            center=0,
            square=True,
            linewidths=0.5,
            cbar_kws={"shrink": 0.5},
        )

    if heatmap_fp is not None:
        # Save heatmap
        hm.get_figure().savefig(heatmap_fp)

    if pairplot is True:
        if pair_plot_x_log is False and pair_plot_y_log is False:

            pp = sns.pairplot(
                df[corr_columns],
                kind=pair_plot_type,
                diag_kind=diag_kind,
                corner=corner,
            )
        else:
            pp = sns.pairplot(
                df[corr_columns], kind=pair_plot_type, diag_kind=diag_kind, corner=False
            )

        if pair_plot_x_log is True:
            for ax in pp.axes.flat:
                ax.set(xscale="log")

        if pair_plot_y_log is True:
            for ax in pp.axes.flat:
                ax.set(yscale="log")

        if pairplot_fp is not None:
            # Save pairplot
            pp.savefig(pairplot_fp)


# def plot_classified_poly(
#     gdf,
#     plot_col,
#     scheme,
#     k,
#     plot_na,
#     cmap,
#     title,
#     cx_tile=None,
#     edgecolor="black",
#     linewidth=0.5,
#     fp=None,
#     legend=True,
#     alpha=1,
#     figsize=pdict["fsmap"],
#     attr=pdict["map_attr"],
#     set_axis_off=True,
#     dpi=pdict["dpi"],
#     classification_kwds=None,
#     background_color=None,
#     legend_kwds={"fmt": "{:.0f}"},
# ):
#     """
#     Plots a classified polygon based on the given parameters.

#     Parameters:
#     gdf (GeoDataFrame): The GeoDataFrame containing the polygon data to be plotted.
#     plot_col (str): The column in the GeoDataFrame to be used for coloring the polygons.
#     scheme (str): The classification scheme to be used for coloring the polygons.
#     k (int): The number of classes to be used for the classification.
#     cx_tile (str): The contextily tile to be used for the basemap.
#     plot_na (bool): If True, polygons with no data are plotted in light grey.
#     cmap (str): The colormap to be used for coloring the polygons.
#     title (str): The title of the plot.
#     edgecolor (str, optional): The color of the polygon edges. Defaults to "black".
#     fp (str, optional): The file path where the plot should be saved. If None, the plot is not saved. Defaults to None.
#     legend (bool, optional): If True, a legend is added to the plot. Defaults to True.
#     alpha (float, optional): The alpha level of the polygons. Defaults to 0.8.
#     figsize (tuple, optional): The size of the figure. Defaults to (10, 10).
#     attr (str, optional): The attribute to be used for the plot. Defaults to None.
#     set_axis_off (bool, optional): If True, the axis is set off. Defaults to True.
#     plot_res (str, optional): The resolution of the plot. Defaults to "low".
#     dpi (int, optional): The resolution in dots per inch. Defaults to 300.
#     classification_kwds (dict, optional): Additional keyword arguments for the 'user_defined' classification scheme. Defaults to None.

#     Returns:
#     None
#     """

#     fig, ax = plt.subplots(1, figsize=figsize)

#     # divider = make_axes_locatable(ax)
#     # cax = divider.append_axes("right", size="3.5%", pad="1%")
#     if scheme == "user_defined" and classification_kwds is not None:
#         if plot_na:
#             gdf.plot(
#                 # cax=cax,
#                 ax=ax,
#                 column=plot_col,
#                 scheme=scheme,
#                 k=k,
#                 cmap=cmap,
#                 alpha=alpha,
#                 edgecolor=edgecolor,
#                 linewidth=linewidth,
#                 legend=legend,
#                 legend_kwds=legend_kwds,
#                 missing_kwds={
#                     "color": pdict["nodata"],
#                     "label": "No data",
#                     "alpha": pdict["alpha_nodata"],
#                 },
#                 classification_kwds=classification_kwds,
#             )
#     else:
#         if plot_na:
#             gdf.plot(
#                 # cax=cax,
#                 ax=ax,
#                 column=plot_col,
#                 scheme=scheme,
#                 k=k,
#                 cmap=cmap,
#                 alpha=alpha,
#                 edgecolor=edgecolor,
#                 linewidth=linewidth,
#                 legend=legend,
#                 legend_kwds=legend_kwds,
#                 missing_kwds={
#                     "color": pdict["nodata"],
#                     "label": "No data",
#                     "alpha": pdict["alpha_nodata"],
#                 },
#             )
#         else:
#             gdf.plot(
#                 # cax=cax,
#                 ax=ax,
#                 column=plot_col,
#                 scheme=scheme,
#                 k=k,
#                 cmap=cmap,
#                 alpha=alpha,
#                 edgecolor=edgecolor,
#                 linewidth=linewidth,
#                 legend=legend,
#                 legend_kwds=legend_kwds,
#             )

#     if cx_tile is not None:
#         cx.add_basemap(ax=ax, crs=gdf.crs, source=cx_tile)

#     if cx_tile is None and background_color is not None:
#         ax.set_facecolor(background_color)

#     if set_axis_off:
#         ax.set_axis_off()

#     if cx_tile is None and background_color is not None:
#         ax.add_artist(ax.patch)
#         ax.patch.set_zorder(-1)

#     if attr is not None:
#         cx.add_attribution(ax=ax, text="(C) " + attr)
#         txt = ax.texts[-1]
#         txt.set_position([0.99, 0.01])
#         txt.set_ha("right")
#         txt.set_va("bottom")

#     ax.add_artist(
#         ScaleBar(
#             dx=1,
#             units="m",
#             dimension="si-length",
#             length_fraction=0.15,
#             width_fraction=0.002,
#             location="lower left",
#             box_alpha=0,
#         )
#     )
#     ax.set_title(title)

#     if fp:
#
#       fig.savefig(fp + ".png", dpi=dpi)

#     plt.show()
#     plt.close()


def remove_colorbar_outline(cmap, fig, cax, norm_min, norm_max):
    sm = plt.cm.ScalarMappable(
        cmap=cmap, norm=plt.Normalize(vmin=norm_min, vmax=norm_max)
    )
    sm._A = []
    cbar = fig.colorbar(sm, cax=cax)
    cbar.outline.set_visible(False)  # Remove the outline of the colorbar


def plot_unclassified_poly(
    poly_gdf,
    plot_col,
    plot_title,
    filepath,
    cmap,
    cx_tile=None,
    alpha=1,
    edgecolor="white",
    linewidth=0.1,
    figsize=pdict["fsmap"],
    dpi=pdict["dpi"],
    legend=True,
    set_axis_off=True,
    use_norm=False,
    norm_min=None,
    norm_max=None,
    attr=pdict["map_attr"],
    plot_na=True,
    background_color=None,
    legend_kwds={"fmt": "{:.0f}"},
    legend_fs=pdict["map_legend_fs"],
):
    """
    Plots an unclassified polygon based on the given parameters.
    poly_gdf (GeoDataFrame): The GeoDataFrame containing the polygon data to be plotted.
    plot_col (str): The column in the GeoDataFrame to be used for coloring the polygons.
    plot_title (str): The title of the plot.
    filepath (str): The file path where the plot should be saved.
    cmap (str): The colormap to be used for coloring the polygons.
    alpha (float): The alpha level of the polygons.
    cx_tile (str): The contextily tile to be used for the basemap.
    figsize (tuple, optional): The size of the figure. Defaults to (10, 10).
    dpi (int, optional): The resolution in dots per inch. Defaults to 300.
    legend (bool, optional): If True, a legend is added to the plot. Defaults to True.
    set_axis_off (bool, optional): If True, the axis is set off. Defaults to True.
    use_norm (bool, optional): If True, the colormap is normalized. Defaults to False.
    norm_min (float, optional): The minimum value for the colormap normalization. Defaults to None.
    norm_max (float, optional): The maximum value for the colormap normalization. Defaults to None.
    attr (str, optional): The attribute to be used for the plot. Defaults to None.
    plot_na (bool, optional): If True, polygons with no data are plotted in light grey. Defaults to True.
    """

    if use_norm is True:
        assert norm_min is not None, print("Please provide a value for norm_min")
        assert norm_max is not None, print("Please provide a value for norm_max")

    fig, ax = plt.subplots(1, figsize=figsize)

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="3.5%", pad="1%")
    cax.tick_params(labelsize=legend_fs)

    if use_norm is True:

        cbnorm = colors.Normalize(vmin=norm_min, vmax=norm_max)

        if plot_na:

            poly_gdf.plot(
                cax=cax,
                ax=ax,
                column=plot_col,
                legend=legend,
                legend_kwds=legend_kwds,
                edgecolor=edgecolor,
                linewidth=linewidth,
                alpha=alpha,
                norm=cbnorm,
                cmap=cmap,
                missing_kwds={
                    "color": pdict["nodata"],
                    "label": "No data",
                    "alpha": pdict["alpha_nodata"],
                },
            )

        else:

            poly_gdf.plot(
                cax=cax,
                ax=ax,
                column=plot_col,
                edgecolor=edgecolor,
                linewidth=linewidth,
                legend=legend,
                legend_kwds=legend_kwds,
                alpha=alpha,
                norm=cbnorm,
                cmap=cmap,
            )

    else:
        if plot_na:

            poly_gdf.plot(
                cax=cax,
                ax=ax,
                column=plot_col,
                edgecolor=edgecolor,
                linewidth=linewidth,
                legend=legend,
                legend_kwds=legend_kwds,
                alpha=alpha,
                cmap=cmap,
                missing_kwds={
                    "color": pdict["nodata"],
                    "label": "No data",
                    "alpha": pdict["alpha_nodata"],
                },
            )

        else:
            poly_gdf.plot(
                cax=cax,
                ax=ax,
                column=plot_col,
                edgecolor=edgecolor,
                linewidth=linewidth,
                legend=legend,
                legend_kwds=legend_kwds,
                alpha=alpha,
                cmap=cmap,
            )

    if legend and use_norm is False:
        remove_colorbar_outline(
            cmap, fig, cax, poly_gdf[plot_col].min(), poly_gdf[plot_col].max()
        )

    if legend and use_norm is True:
        remove_colorbar_outline(cmap, fig, cax, norm_min, norm_max)

    if plot_na and len(poly_gdf.loc[poly_gdf[plot_col].isna()]) > 0:
        # Creates a rectangular patch for each contaminant, using the colors above
        patch_list = []
        label = "No data"
        color = pdict["nodata"]
        patch_list.append(
            patches.Patch(
                facecolor=color,
                label=label,
                alpha=pdict["alpha_nodata"],
                linewidth=0,
                edgecolor="none",
            )
        )

        # Creates a legend with the list of patches above.
        ax.legend(
            handles=patch_list,
            fontsize=legend_fs,
            loc="lower left",
            bbox_to_anchor=(0.1, -0.015),
            # title="Litologia",
            title_fontsize=legend_fs,
            frameon=False,
        )

    if cx_tile is not None:
        cx.add_basemap(ax=ax, crs=poly_gdf.crs, source=cx_tile)

    if cx_tile is None and background_color is not None:
        ax.set_facecolor(background_color)

    if set_axis_off:
        ax.set_axis_off()

    if cx_tile is None and background_color is not None:
        ax.add_artist(ax.patch)
        ax.patch.set_zorder(-1)

    if attr is not None:
        cx.add_attribution(ax=ax, text="(C) " + attr, font_size=pdict["map_legend_fs"])
        txt = ax.texts[-1]
        txt.set_position([0.99, 0.01])
        txt.set_ha("right")
        txt.set_va("bottom")

    ax.add_artist(
        ScaleBar(
            dx=1,
            units="m",
            dimension="si-length",
            length_fraction=0.15,  # modify the length of the scale bar
            width_fraction=0.002,
            location="lower left",
            box_alpha=0,
            font_properties={"size": legend_fs},
        )
    )

    ax.set_title(plot_title, fontsize=pdict["map_title_fs"])

    fig.savefig(filepath + ".png", dpi=dpi)

    plt.show()
    plt.close()


def set_renderer(f="svg"):
    matplotlib_inline.backend_inline.set_matplotlib_formats(f)


def combined_zipf_plot(
    # component_size_all,
    component_size_1,
    component_size_1_2,
    component_size_1_3,
    component_size_1_4,
    component_size_car,
    lts_color_dict,
    fp,
    title="Component length distribution",
    figsize=pdict["fsbar"],
    scatter_size=15,
    alpha_line=0.7,
    linewidth=0.5,
    fs_increase=3,
):
    """
    Plot a combined Zipf plot for component length distribution.

    Args:
        component_size_all (dict): A dictionary containing component size information for all components.
        component_size_1 (dict): A dictionary containing component size information for LTS 1 components.
        component_size_1_2 (dict): A dictionary containing component size information for LTS 1-2 components.
        component_size_1_3 (dict): A dictionary containing component size information for LTS 1-3 components.
        component_size_1_4 (dict): A dictionary containing component size information for LTS 1-4 components.
        component_size_car (dict): A dictionary containing component size information for car components.
        lts_color_dict (dict): A dictionary mapping LTS numbers to color codes.
        fp (str): The file path to save the plot.
        title (str, optional): The title of the plot. Defaults to "Component length distribution".
        figsize (tuple, optional): The figure size of the plot. Defaults to pdict["fsbar"].

    Returns:
        None
    """

    fig = plt.figure(figsize=figsize)
    axes = fig.add_axes([0, 0, 1, 1])

    from matplotlib.patches import Patch

    axes.set_axisbelow(True)
    axes.grid(True, which="major", ls="dotted")

    # all_yvals = sorted(list(component_size_all["infra_length"]), reverse=True)
    lts1_yvals = sorted(list(component_size_1["infra_length"]), reverse=True)
    lts2_yvals = sorted(list(component_size_1_2["infra_length"]), reverse=True)
    lts3_yvals = sorted(list(component_size_1_3["infra_length"]), reverse=True)
    lts4_yvals = sorted(list(component_size_1_4["infra_length"]), reverse=True)
    car_yvals = sorted(list(component_size_car["infra_length"]), reverse=True)

    lts1_xvals = [i + 1 for i in range(len(component_size_1))]
    lts2_xvals = [i + 1 for i in range(len(component_size_1_2))]
    lts3_xvals = [i + 1 for i in range(len(component_size_1_3))]
    lts4_xvals = [i + 1 for i in range(len(component_size_1_4))]
    car_xvals = [i + 1 for i in range(len(component_size_car))]
    # all_xvals = [i + 1 for i in range(len(component_size_all))]

    axes.scatter(
        x=lts1_xvals,
        y=lts1_yvals,
        s=scatter_size,
        color=lts_color_dict["1"],
    )

    axes.scatter(
        x=lts2_xvals,
        y=lts2_yvals,
        s=scatter_size,
        color=lts_color_dict["2"],
    )

    axes.scatter(
        x=lts3_xvals,
        y=lts3_yvals,
        s=scatter_size,
        color=lts_color_dict["3"],
    )

    axes.scatter(
        x=lts4_xvals,
        y=lts4_yvals,
        s=scatter_size,
        color=lts_color_dict["4"],
    )

    axes.scatter(
        x=car_xvals,
        y=car_yvals,
        s=scatter_size,
        color=lts_color_dict["car"],
    )

    # axes.scatter(
    #     x=all_xvals,
    #     y=all_yvals,
    #     s=scatter_size,
    #     color=lts_color_dict["total"],
    # )

    axes.plot(
        lts1_xvals,
        lts1_yvals,
        color=lts_color_dict["1"],
        linewidth=linewidth,
        alpha=alpha_line,
    )

    axes.plot(
        lts2_xvals,
        lts2_yvals,
        color=lts_color_dict["2"],
        linewidth=linewidth,
        alpha=alpha_line,
    )

    axes.plot(
        lts3_xvals,
        lts3_yvals,
        color=lts_color_dict["3"],
        linewidth=linewidth,
        alpha=alpha_line,
    )

    axes.plot(
        lts4_xvals,
        lts4_yvals,
        color=lts_color_dict["4"],
        linewidth=linewidth,
        alpha=alpha_line,
    )

    axes.plot(
        car_xvals,
        car_yvals,
        color=lts_color_dict["car"],
        linewidth=linewidth,
        alpha=alpha_line,
    )
    # axes.plot(
    #     all_xvals,
    #     all_yvals,
    #     color=lts_color_dict["total"],
    #     linewidth=linewidth,
    #     alpha=alpha_line,
    # )

    y_min = min(
        # min(all_yvals),
        min(lts1_yvals),
        min(lts2_yvals),
        min(lts3_yvals),
        min(lts4_yvals),
        min(car_yvals),
    )
    y_max = max(
        # max(all_yvals),
        max(lts1_yvals),
        max(lts2_yvals),
        max(lts3_yvals),
        max(lts4_yvals),
        max(car_yvals),
    )
    axes.set_ylim(
        ymin=10 ** math.floor(math.log10(y_min)),
        ymax=10 ** math.ceil(math.log10(y_max)),
    )
    axes.set_xscale("log")
    axes.set_yscale("log")

    axes.set_ylabel("Component length [km]", fontsize=pdict["fs_subplot"] + fs_increase)
    axes.set_xlabel(
        "Component rank (largest to smallest)",
        fontsize=pdict["fs_subplot"] + fs_increase,
    )

    legend_patches = [
        Patch(
            facecolor=lts_color_dict["1"],
            edgecolor=lts_color_dict["1"],
            label="Color Patch",
        ),
        Patch(
            facecolor=lts_color_dict["2"],
            edgecolor=lts_color_dict["2"],
            label="Color Patch",
        ),
        Patch(
            facecolor=lts_color_dict["3"],
            edgecolor=lts_color_dict["3"],
            label="Color Patch",
        ),
        Patch(
            facecolor=lts_color_dict["4"],
            edgecolor=lts_color_dict["4"],
            label="Color Patch",
        ),
        Patch(
            facecolor=lts_color_dict["car"],
            edgecolor=lts_color_dict["car"],
            label="Color Patch",
        ),
        # Patch(
        #     facecolor=lts_color_dict["total"],
        #     edgecolor=lts_color_dict["total"],
        #     label="Color Patch",
        # ),
    ]

    axes.legend(
        legend_patches,
        [
            "LTS 1",
            "LTS ≤ 2",
            "LTS ≤ 3",
            "LTS ≤ 4",
            "Total car",
            # "Total network",
        ],
    )
    axes.set_title(title, fontsize=pdict["fs_subplot"] + fs_increase)

    legend = axes.get_legend()
    if legend:
        legend.set_frame_on(False)

        for i in range(len(legend.get_texts())):
            legend.get_texts()[i].set_fontsize(pdict["fs_subplot"] + fs_increase)

    axes.tick_params(axis="both", which="major", labelsize=pdict["fs_subplot"])

    fig.savefig(fp, bbox_inches="tight", dpi=pdict["dpi"])
    plt.show()
    plt.close()


# def make_zipf_component_plot(df, col, label, fp=None, show=True):
#     """
#     Create a Zipf component plot.

#     Parameters:
#     - df (DataFrame): The DataFrame containing the data.
#     - col (str): The column name in the DataFrame to use for the y-values.
#     - label (str): The label to include in the plot title.
#     - fp (str, optional): The file path to save the plot image. Default is None.
#     - show (bool, optional): Whether to display the plot. Default is True.

#     Returns:
#     None
#     """

#     fig = plt.figure(figsize=pdict["fsbar"])
#     axes = fig.add_axes([0, 0, 1, 1])

#     axes.set_axisbelow(True)
#     axes.grid(True, which="major", ls="dotted")
#     yvals = sorted(list(df[col]), reverse=True)

#     axes.scatter(
#         x=[i + 1 for i in range(len(df))],
#         y=yvals,
#         s=18,
#         color="purple",
#     )
#     axes.set_ylim(
#         ymin=10 ** math.floor(math.log10(min(yvals))),
#         ymax=10 ** math.ceil(math.log10(max(yvals))),
#     )
#     axes.set_xscale("log")
#     axes.set_yscale("log")

#     axes.set_ylabel("Component length [km]")
#     axes.set_xlabel("Component rank (largest to smallest)")
#     axes.set_title(f"Component length distribution in: {label}")

#     if fp:
#         plt.savefig(fp, bbox_inches="tight")

#     if show:
#         plt.show()
#     else:
#         plt.close()


def make_barplot(data, x, y, hue_col, palette, xlabel=None, fp=None):

    _, ax = plt.subplots(figsize=pdict["fsbar"])
    sns.barplot(ax=ax, data=data, x=x, y=y, palette=palette, hue=hue_col, errorbar=None)
    plt.xlabel(xlabel)
    ax.yaxis.set_major_formatter(FormatStrFormatter("%.0f"))
    plt.ylabel("Average bikeability rank")
    plt.xticks(rotation=45, ha="right")
    sns.despine(left=True, bottom=True)
    plt.tight_layout()

    if fp:
        plt.savefig(fp, dpi=pdict["dpi"])

    plt.show()


def make_stripplot(
    data,
    x,
    y,
    hue_col,
    palette,
    legend=False,
    xlabel=None,
    xticks=None,
    fp=None,
    fontsize=12,
):

    plt.figure(figsize=pdict["fsbar"])
    sns.stripplot(
        data=data, x=x, y=y, hue=hue_col, palette=palette, legend=legend, jitter=True
    )

    plt.xlabel(xlabel, fontsize=fontsize)
    plt.ylabel("")

    if xticks:
        plt.xticks(xticks, fontsize=fontsize)

    plt.yticks(fontsize=fontsize)

    sns.despine(left=True, bottom=True)
    plt.tight_layout()

    if fp:
        plt.savefig(fp, dpi=pdict["dpi"])

    plt.show()


def sns_scatter(data, x, y, hue, palette, alpha=0.7, yticks=None):

    _, ax = plt.subplots(figsize=pdict["fsbar"])
    sns.scatterplot(
        ax=ax,
        data=data,
        x=x,
        y=y,
        hue=hue,
        palette=palette,
        alpha=alpha,
    )

    ax.yaxis.set_major_formatter(FormatStrFormatter("%.0f"))
    plt.ylabel("Average bikeability rank")

    if yticks:
        plt.yticks(yticks)
    sns.despine(left=True, bottom=True)

    plt.legend(
        loc="upper left",
        bbox_to_anchor=(1, 1),
        frameon=False,
    )

    plt.show()
    plt.close()


# Bivariate map functions from on https://waterprogramming.wordpress.com/2022/09/08/bivariate-choropleth-maps/


### function to convert hex color to rgb to Color object (generativepy package)
def hex_to_color(hexcode):
    rgb = ImageColor.getcolor(hexcode, "RGB")
    rgb = [v / 256 for v in rgb]
    rgb = Color(*rgb)
    return rgb


def create_color_grid(class_bounds, c00, c10, c01, c11):
    group_count = len(class_bounds)
    c00_to_c10 = []
    c01_to_c11 = []
    colorlist = []
    for i in range(group_count):
        c00_to_c10.append(c00.lerp(c10, 1 / (group_count - 1) * i))
        c01_to_c11.append(c01.lerp(c11, 1 / (group_count - 1) * i))
    for i in range(group_count):
        for j in range(group_count):
            colorlist.append(
                c00_to_c10[i].lerp(c01_to_c11[i], 1 / (group_count - 1) * j)
            )
    return colorlist


### function to get bivariate color given two percentiles
def get_bivariate_choropleth_color(p1, p2, class_bounds, colorlist):
    if p1 >= 0 and p2 >= 0:
        count = 0
        stop = False
        for percentile_bound_p1 in class_bounds:
            for percentile_bound_p2 in class_bounds:
                if (not stop) and (p1 <= percentile_bound_p1):
                    if (not stop) and (p2 <= percentile_bound_p2):
                        color = colorlist[count]
                        stop = True
                count += 1
    else:
        color = [0.8, 0.8, 0.8, 1]
    return color


def make_bivariate_choropleth_map(
    gdf,
    col1,
    col2,
    # attr,
    col1_label,
    col2_label,
    class_bounds,
    colorlist,
    figsize=pdict["fsmap"],
    alpha=0.8,
    fp=None,
    fs_labels=12,
    fs_tick=10,
):

    ### plot map based on bivariate choropleth
    _, ax = plt.subplots(1, 1, figsize=figsize)

    gdf["color_bivariate"] = [
        get_bivariate_choropleth_color(p1, p2, class_bounds, colorlist)
        for p1, p2 in zip(gdf[col1].values, gdf[col2].values)
    ]

    gdf.plot(
        ax=ax, color=gdf["color_bivariate"], alpha=alpha, legend=False, linewidth=0.0
    )

    ax.set_axis_off()

    ax.add_artist(
        ScaleBar(
            dx=1,
            units="m",
            dimension="si-length",
            length_fraction=0.15,
            width_fraction=0.002,
            location="lower left",
            box_alpha=0.5,
            font_properties={"size": fs_labels},
        )
    )

    ### now create inset legend
    legend_ax = ax.inset_axes([0.6, 0.6, 0.35, 0.35])
    legend_ax.set_aspect("equal", adjustable="box")
    count = 0
    xticks = [0]
    yticks = [0]
    for i, percentile_bound_p1 in enumerate(class_bounds):
        for j, percentile_bound_p2 in enumerate(class_bounds):
            percentileboxes = [Rectangle((i, j), 1, 1)]
            pc = PatchCollection(
                percentileboxes, facecolor=colorlist[count], alpha=alpha
            )
            count += 1
            legend_ax.add_collection(pc)
            if i == 0:
                yticks.append(percentile_bound_p2)
        xticks.append(percentile_bound_p1)

    _ = legend_ax.set_xlim([0, len(class_bounds)])
    _ = legend_ax.set_ylim([0, len(class_bounds)])
    _ = legend_ax.set_xticks(
        list(range(len(class_bounds) + 1)), xticks, fontsize=fs_tick
    )
    _ = legend_ax.set_yticks(
        list(range(len(class_bounds) + 1)), yticks, fontsize=fs_tick
    )
    _ = legend_ax.set_xlabel(col1_label, fontsize=fs_labels)
    _ = legend_ax.set_ylabel(col2_label, fontsize=fs_labels)

    plt.tight_layout()

    if fp:
        plt.savefig(fp, dpi=pdict["dpi"])

    plt.show()
    plt.close()


def make_stripplot_w_outliers(
    data,
    x,
    y,
    hue_col,
    palette,
    outlier_above_col="outlier_above",
    outlier_below_col="outlier_below",
    legend=False,
    xlabel=None,
    xticks=None,
    fp=None,
    fontsize=12,
):
    plt.figure(figsize=pdict["fsbar"])
    sns.stripplot(
        data=data,
        x=x,
        y=y,
        hue=hue_col,
        palette=palette,
        size=8,
        legend=legend,
        jitter=False,
        alpha=0.5,
    )

    # Overlay outliers in black
    outliers = data[
        (data[outlier_above_col] == True) | (data[outlier_below_col] == True)
    ]
    plt.scatter(
        outliers[x],
        outliers[y],
        edgecolor="black",
        facecolor="none",
        linewidth=1,
        # color="#4A4A4A",
        s=50,
        label="Outliers",
        zorder=10,  # Ensure outliers are plotted on top
        alpha=0.6,
    )

    plt.xlabel(xlabel, fontsize=fontsize)
    plt.ylabel("")

    if xticks:
        plt.xticks(xticks, fontsize=fontsize)

    plt.yticks(fontsize=fontsize)

    sns.despine(left=True, bottom=True)
    plt.tight_layout()

    if fp:
        plt.savefig(fp, dpi=pdict["dpi"])

    plt.show()


def make_bivariate_choropleth_map_zoom(
    gdf,
    col1,
    col2,
    # attr,
    col1_label,
    col2_label,
    class_bounds,
    colorlist,
    xmin,
    xmax,
    ymin,
    ymax,
    figsize=pdict["fsmap"],
    alpha=0.8,
    fp=None,
    fs_labels=12,
    fs_tick=10,
    legend=True,
):

    ### plot map based on bivariate choropleth
    _, ax = plt.subplots(1, 1, figsize=figsize)

    gdf["color_bivariate"] = [
        get_bivariate_choropleth_color(p1, p2, class_bounds, colorlist)
        for p1, p2 in zip(gdf[col1].values, gdf[col2].values)
    ]

    gdf.plot(
        ax=ax, color=gdf["color_bivariate"], alpha=alpha, legend=False, linewidth=0.0
    )

    ax.axis([xmin, xmax, ymin, ymax])

    ax.add_artist(
        ScaleBar(
            dx=1,
            units="m",
            dimension="si-length",
            length_fraction=0.15,
            width_fraction=0.002,
            location="lower left",
            box_alpha=0.5,
            font_properties={"size": fs_labels},
        )
    )

    ax.set_axis_off()

    if legend:
        ### now create inset legend
        legend_ax = ax.inset_axes([0.6, 0.6, 0.35, 0.35])
        legend_ax.set_aspect("equal", adjustable="box")
        count = 0
        xticks = [0]
        yticks = [0]
        for i, percentile_bound_p1 in enumerate(class_bounds):
            for j, percentile_bound_p2 in enumerate(class_bounds):
                percentileboxes = [Rectangle((i, j), 1, 1)]
                pc = PatchCollection(
                    percentileboxes, facecolor=colorlist[count], alpha=alpha
                )
                count += 1
                legend_ax.add_collection(pc)
                if i == 0:
                    yticks.append(percentile_bound_p2)
            xticks.append(percentile_bound_p1)

        _ = legend_ax.set_xlim([0, len(class_bounds)])
        _ = legend_ax.set_ylim([0, len(class_bounds)])
        _ = legend_ax.set_xticks(
            list(range(len(class_bounds) + 1)), xticks, fontsize=fs_tick
        )
        _ = legend_ax.set_yticks(
            list(range(len(class_bounds) + 1)), yticks, fontsize=fs_tick
        )
        _ = legend_ax.set_xlabel(col1_label, fontsize=fs_labels)
        _ = legend_ax.set_ylabel(col2_label, fontsize=fs_labels)

    plt.tight_layout()

    if fp:
        plt.savefig(fp, dpi=pdict["dpi"])

    plt.show()
    plt.close()
