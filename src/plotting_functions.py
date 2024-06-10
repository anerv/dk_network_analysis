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
from IPython.display import Image, HTML, display
import plotly.express as px


exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())


def get_min_max_vals(gdf, columns):
    min_vals = [gdf[p].min() for p in columns]
    max_vals = [gdf[p].max() for p in columns]
    return min(min_vals), max(max_vals)


def compare_lisa_results(fp, metric, aggregation_level, rename_dict, format_style):

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
    pair_plot_type="reg",
    diag_kind="kde",
    corner=True,
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

    df_corr = df[corr_columns].corr()

    # Generate a mask for the upper triangle
    mask = np.triu(np.ones_like(df_corr, dtype=bool))

    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(11, 9))

    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(230, 20, as_cmap=True)

    hm = sns.heatmap(
        df_corr,
        mask=mask,
        cmap=cmap,
        vmax=0.3,
        center=0,
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.5},
    )

    if heatmap_fp is not None:
        # Save heatmap
        hm.get_figure().savefig(heatmap_fp)

    if pair_plot_x_log is False and pair_plot_y_log is False:

        pp = sns.pairplot(
            df[corr_columns], kind=pair_plot_type, diag_kind=diag_kind, corner=corner
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


def get_unique_bins(
    gdf,
    p,
    scheme,
    k,
):
    if scheme == "fisherjenks":

        test = mapclassify.FisherJenks(gdf[p], k=k)

        if len(set(test.bins)) == k:
            return k
        else:
            return len(set(test.bins))

    else:
        print("Only Fisher Jenks is supported")

        return None


def plot_classified_poly(
    gdf,
    plot_col,
    scheme,
    k,
    plot_na,
    cmap,
    title,
    cx_tile=None,
    edgecolor="black",
    linewidth=0.5,
    fp=None,
    legend=True,
    alpha=1,
    figsize=(10, 10),
    attr=pdict["map_attr"],
    set_axis_off=True,
    plot_res=pdict["plot_res"],
    dpi=pdict["dpi"],
    classification_kwds=None,
    background_color=None,
):
    """
    Plots a classified polygon based on the given parameters.

    Parameters:
    gdf (GeoDataFrame): The GeoDataFrame containing the polygon data to be plotted.
    plot_col (str): The column in the GeoDataFrame to be used for coloring the polygons.
    scheme (str): The classification scheme to be used for coloring the polygons.
    k (int): The number of classes to be used for the classification.
    cx_tile (str): The contextily tile to be used for the basemap.
    plot_na (bool): If True, polygons with no data are plotted in light grey.
    cmap (str): The colormap to be used for coloring the polygons.
    title (str): The title of the plot.
    edgecolor (str, optional): The color of the polygon edges. Defaults to "black".
    fp (str, optional): The file path where the plot should be saved. If None, the plot is not saved. Defaults to None.
    legend (bool, optional): If True, a legend is added to the plot. Defaults to True.
    alpha (float, optional): The alpha level of the polygons. Defaults to 0.8.
    figsize (tuple, optional): The size of the figure. Defaults to (10, 10).
    attr (str, optional): The attribute to be used for the plot. Defaults to None.
    set_axis_off (bool, optional): If True, the axis is set off. Defaults to True.
    plot_res (str, optional): The resolution of the plot. Defaults to "low".
    dpi (int, optional): The resolution in dots per inch. Defaults to 300.
    classification_kwds (dict, optional): Additional keyword arguments for the 'user_defined' classification scheme. Defaults to None.

    Returns:
    None
    """

    fig, ax = plt.subplots(1, figsize=figsize)

    # divider = make_axes_locatable(ax)
    # cax = divider.append_axes("right", size="3.5%", pad="1%")
    if scheme == "user_defined" and classification_kwds is not None:
        if plot_na:
            gdf.plot(
                # cax=cax,
                ax=ax,
                column=plot_col,
                scheme=scheme,
                k=k,
                cmap=cmap,
                alpha=alpha,
                edgecolor=edgecolor,
                linewidth=linewidth,
                legend=legend,
                missing_kwds={"color": pdict["nodata"], "label": "No data"},
                classification_kwds=classification_kwds,
            )
    else:
        if plot_na:
            gdf.plot(
                # cax=cax,
                ax=ax,
                column=plot_col,
                scheme=scheme,
                k=k,
                cmap=cmap,
                alpha=alpha,
                edgecolor=edgecolor,
                linewidth=linewidth,
                legend=legend,
                missing_kwds={"color": pdict["nodata"], "label": "No data"},
            )
        else:
            gdf.plot(
                # cax=cax,
                ax=ax,
                column=plot_col,
                scheme=scheme,
                k=k,
                cmap=cmap,
                alpha=alpha,
                edgecolor=edgecolor,
                linewidth=linewidth,
                legend=legend,
            )

    if cx_tile is not None:
        cx.add_basemap(ax=ax, crs=gdf.crs, source=cx_tile)

    if cx_tile is None and background_color is not None:
        ax.set_facecolor(background_color)

    if set_axis_off:
        ax.set_axis_off()

    if cx_tile is None and background_color is not None:
        ax.add_artist(ax.patch)
        ax.patch.set_zorder(-1)

    if attr is not None:
        cx.add_attribution(ax=ax, text="(C) " + attr)
        txt = ax.texts[-1]
        txt.set_position([0.99, 0.01])
        txt.set_ha("right")
        txt.set_va("bottom")

    ax.set_title(title)

    if fp:
        if plot_res == "high":
            fig.savefig(fp + ".svg", dpi=dpi)
        else:
            fig.savefig(fp + ".png", dpi=dpi)

    plt.show()
    plt.close()


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
    plot_res=pdict["plot_res"],
    attr=pdict["map_attr"],
    plot_na=True,
    background_color=None,
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
    plot_res (str, optional): The resolution of the plot. Defaults to "low".
    attr (str, optional): The attribute to be used for the plot. Defaults to None.
    plot_na (bool, optional): If True, polygons with no data are plotted in light grey. Defaults to True.
    """

    if use_norm is True:
        assert norm_min is not None, print("Please provide a value for norm_min")
        assert norm_max is not None, print("Please provide a value for norm_max")

    fig, ax = plt.subplots(1, figsize=figsize)

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="3.5%", pad="1%")

    if use_norm is True:

        cbnorm = colors.Normalize(vmin=norm_min, vmax=norm_max)

        if plot_na:

            poly_gdf.plot(
                cax=cax,
                ax=ax,
                column=plot_col,
                legend=legend,
                edgecolor=edgecolor,
                linewidth=linewidth,
                alpha=alpha,
                norm=cbnorm,
                cmap=cmap,
                missing_kwds={"color": pdict["nodata"], "label": "No data"},
            )

        else:

            poly_gdf.plot(
                cax=cax,
                ax=ax,
                column=plot_col,
                edgecolor=edgecolor,
                linewidth=linewidth,
                legend=legend,
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
                alpha=alpha,
                cmap=cmap,
                missing_kwds={"color": pdict["nodata"], "label": "No data"},
            )

        else:
            poly_gdf.plot(
                cax=cax,
                ax=ax,
                column=plot_col,
                edgecolor=edgecolor,
                linewidth=linewidth,
                legend=legend,
                alpha=alpha,
                cmap=cmap,
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
        cx.add_attribution(ax=ax, text="(C) " + attr)
        txt = ax.texts[-1]
        txt.set_position([0.99, 0.01])
        txt.set_ha("right")
        txt.set_va("bottom")

    ax.set_title(plot_title)

    if plot_res == "high":
        fig.savefig(filepath + ".svg", dpi=dpi)
    else:
        fig.savefig(filepath + ".png", dpi=dpi)

    # fig.close()


def set_renderer(f="svg"):
    matplotlib_inline.backend_inline.set_matplotlib_formats(f)


def combined_zipf_plot(
    component_size_all,
    component_size_1,
    component_size_2,
    component_size_3,
    component_size_4,
    component_size_car,
    lts_color_dict,
    fp,
    title="Component length distribution",
):
    fig = plt.figure(figsize=pdict["fsbar"])
    axes = fig.add_axes([0, 0, 1, 1])

    from matplotlib.patches import Patch

    axes.set_axisbelow(True)
    axes.grid(True, which="major", ls="dotted")

    all_yvals = sorted(list(component_size_all["bike_length"]), reverse=True)
    lts1_yvals = sorted(list(component_size_1["bike_length"]), reverse=True)
    lts2_yvals = sorted(list(component_size_2["bike_length"]), reverse=True)
    lts3_yvals = sorted(list(component_size_3["bike_length"]), reverse=True)
    lts4_yvals = sorted(list(component_size_4["bike_length"]), reverse=True)
    ltscar_yvals = sorted(list(component_size_car["geom_length"]), reverse=True)

    axes.scatter(
        x=[i + 1 for i in range(len(component_size_all))],
        y=all_yvals,
        s=18,
        color=lts_color_dict["total"],
    )

    axes.scatter(
        x=[i + 1 for i in range(len(component_size_1))],
        y=lts1_yvals,
        s=18,
        color=lts_color_dict["1"],
    )

    axes.scatter(
        x=[i + 1 for i in range(len(component_size_2))],
        y=lts2_yvals,
        s=18,
        color=lts_color_dict["2"],
    )

    axes.scatter(
        x=[i + 1 for i in range(len(component_size_3))],
        y=lts3_yvals,
        s=18,
        color=lts_color_dict["3"],
    )

    axes.scatter(
        x=[i + 1 for i in range(len(component_size_4))],
        y=lts4_yvals,
        s=18,
        color=lts_color_dict["4"],
    )

    axes.scatter(
        x=[i + 1 for i in range(len(component_size_car))],
        y=ltscar_yvals,
        s=18,
        color=lts_color_dict["car"],
    )

    y_min = min(
        min(all_yvals),
        min(lts1_yvals),
        min(lts2_yvals),
        min(lts3_yvals),
        min(lts4_yvals),
        min(ltscar_yvals),
    )
    y_max = max(
        max(all_yvals),
        max(lts1_yvals),
        max(lts2_yvals),
        max(lts3_yvals),
        max(lts4_yvals),
        max(ltscar_yvals),
    )
    axes.set_ylim(
        ymin=10 ** math.floor(math.log10(y_min)),
        ymax=10 ** math.ceil(math.log10(y_max)),
    )
    axes.set_xscale("log")
    axes.set_yscale("log")

    axes.set_ylabel("Component length [km]")
    axes.set_xlabel("Component rank (largest to smallest)")

    legend_patches = [
        Patch(
            facecolor=lts_color_dict["total"],
            edgecolor=lts_color_dict["total"],
            label="Color Patch",
        ),
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
    ]

    axes.legend(legend_patches, ["All", "LTS 1", "LTS 2", "LTS 3", "LTS 4", "Car"])
    axes.set_title(title)

    fig.savefig(fp)
    plt.close()


def make_zipf_component_plot(df, col, label, fp=None, show=True):

    fig = plt.figure(figsize=pdict["fsbar"])
    axes = fig.add_axes([0, 0, 1, 1])

    axes.set_axisbelow(True)
    axes.grid(True, which="major", ls="dotted")
    yvals = sorted(list(df[col]), reverse=True)
    # yvals = sorted(list(df[col] / 1000), reverse=True)
    axes.scatter(
        x=[i + 1 for i in range(len(df))],
        y=yvals,
        s=18,
        color="purple",
    )
    axes.set_ylim(
        ymin=10 ** math.floor(math.log10(min(yvals))),
        ymax=10 ** math.ceil(math.log10(max(yvals))),
    )
    axes.set_xscale("log")
    axes.set_yscale("log")

    axes.set_ylabel("Component length [km]")
    axes.set_xlabel("Component rank (largest to smallest)")
    axes.set_title(f"Component length distribution in: {label}")

    if fp:
        plt.savefig(fp, bbox_inches="tight")

    if show:
        plt.show()
    else:
        plt.close()
