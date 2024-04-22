import matplotlib as mpl
from matplotlib import cm, colors
import matplotlib.pyplot as plt
import matplotlib_inline.backend_inline
import contextily as cx
from mpl_toolkits.axes_grid1 import make_axes_locatable
import math

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())


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
    axes.set_title(f"Component length distribution in {label}")

    if fp:
        plt.savefig(fp, bbox_inches="tight")

    if show:
        plt.show()
    else:
        plt.close()


def plot_classified_poly(
    gdf,
    plot_col,
    scheme,
    cx_tile,
    plot_na,
    cmap,
    title,
    edgecolor="black",
    fp=None,
    legend=True,
    alpha=0.8,
    figsize=(10, 10),
    attr=None,
    set_axis_off=True,
    plot_res="low",
    dpi=300,
    classification_kwds=None,
):
    """
    Plots a classified polygon based on the given parameters.

    Parameters:
    gdf (GeoDataFrame): The GeoDataFrame containing the polygon data to be plotted.
    plot_col (str): The column in the GeoDataFrame to be used for coloring the polygons.
    scheme (str): The classification scheme to be used for coloring the polygons.
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
                cmap=cmap,
                alpha=alpha,
                edgecolor=edgecolor,
                legend=legend,
                missing_kwds={"color": "lightgrey", "label": "No data"},
                classification_kwds=classification_kwds,
            )
    else:
        if plot_na:
            gdf.plot(
                # cax=cax,
                ax=ax,
                column=plot_col,
                scheme=scheme,
                cmap=cmap,
                alpha=alpha,
                edgecolor=edgecolor,
                legend=legend,
                missing_kwds={"color": "lightgrey", "label": "No data"},
            )
        else:
            gdf.plot(
                # cax=cax,
                ax=ax,
                column=plot_col,
                scheme=scheme,
                cmap=cmap,
                alpha=alpha,
                edgecolor=edgecolor,
                legend=legend,
            )

    cx.add_basemap(ax=ax, crs=gdf.crs, source=cx_tile)

    if attr is not None:
        cx.add_attribution(ax=ax, text="(C) " + attr)
        txt = ax.texts[-1]
        txt.set_position([1, 0.00])
        txt.set_ha("right")
        txt.set_va("bottom")

    ax.set_title(title)

    if set_axis_off:
        ax.set_axis_off()

    if fp:
        if plot_res == "high":
            fig.savefig(fp + ".svg", dpi=dpi)
        else:
            fig.savefig(fp + ".png", dpi=dpi)


def plot_polygon_results(
    poly_gdf,
    plot_cols,
    plot_titles,
    filepaths,
    cmaps,
    alpha,
    cx_tile,
    no_data_cols,
    na_facecolor=pdict["nodata_face"],
    na_edgecolor=pdict["nodata_edge"],
    na_linewidth=pdict["line_nodata"],
    na_hatch=pdict["nodata_hatch"],
    na_alpha=pdict["alpha_nodata"],
    na_legend=nodata_patch,
    figsize=pdict["fsmap"],
    dpi=pdict["dpi"],
    crs=crs,
    legend=True,
    set_axis_off=True,
    legend_loc="upper left",
    use_norm=False,
    norm_min=None,
    norm_max=None,
    plot_res=pdict["plot_res"],
    attr=None,
    plot_na=True,
):
    """
    Make multiple choropleth maps of e.g. poly_gdf with analysis results based on a list of geodataframe columns to be plotted
    and save them in separate files
    Arguments:
        poly_gdf (gdf): geodataframe with polygons to be plotted
        plot_cols (list): list of column names (strings) to be plotted
        plot_titles (list): list of strings to be used as plot titles
        cmaps (list): list of color maps
        alpha(numeric): value between 0-1 for setting the transparency of the plots
        cx_tile(cx tileprovider): name of contextily tile to be used for base map
        no_data_cols(list): list of column names used for generating no data layer in each plot
        na_facecolor(string): name of color used for the no data layer fill
        na_edegcolor(string): name of color used for the no data layer outline
        na_hatch: hatch pattern used for no data layer
        na_alpha (numeric): value between 0-1 for setting the transparency of the plots
        na_linewidth (numeric): width of edge lines of no data poly_gdf cells
        na_legend(matplotlib Patch): patch to be used for the no data layer in the legend
        figsize(tuple): size of each plot
        dpi(numeric): resolution of saved plots
        crs (string): name of crs used for the poly_gdf (to set correct crs of basemap)
        legend (bool): True if a legend/colorbar should be plotted
        set_axis_off (bool): True if axis ticks and values should be omitted
        legend_loc (string): Position of map legend (see matplotlib doc for valid entries)
        use_norm (bool): True if colormap should be defined based on provided min and max values
        norm_min(numeric): min value to use for norming color map
        norm_max(numeric): max value to use for norming color map
        attr (string): optional attribution
        plot_na (bool): True if no data layer should be plotted

    Returns:
        None
    """

    if use_norm is True:
        assert norm_min is not None, print("Please provide a value for norm_min")
        assert norm_max is not None, print("Please provide a value for norm_max")

    for i, c in enumerate(plot_cols):

        fig, ax = plt.subplots(1, figsize=figsize)

        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="3.5%", pad="1%")

        if use_norm is True:

            cbnorm = colors.Normalize(vmin=norm_min[i], vmax=norm_max[i])

            poly_gdf.plot(
                cax=cax,
                ax=ax,
                column=c,
                legend=legend,
                alpha=alpha,
                norm=cbnorm,
                cmap=cmaps[i],
            )

        else:
            poly_gdf.plot(
                cax=cax,
                ax=ax,
                column=c,
                legend=legend,
                alpha=alpha,
                cmap=cmaps[i],
            )
        cx.add_basemap(ax=ax, crs=crs, source=cx_tile)

        if attr is not None:
            cx.add_attribution(ax=ax, text="(C) " + attr)
            txt = ax.texts[-1]
            txt.set_position([1, 0.00])
            txt.set_ha("right")
            txt.set_va("bottom")

        ax.set_title(plot_titles[i])

        if set_axis_off:
            ax.set_axis_off()

        if plot_na:
            # add patches in poly_gdf cells with no data on edges
            if type(no_data_cols[i]) == tuple and len(
                poly_gdf[
                    (poly_gdf[no_data_cols[i][0]].isnull())
                    & (poly_gdf[no_data_cols[i][1]].isnull())
                ]
                > 0
            ):

                poly_gdf[
                    (poly_gdf[no_data_cols[i][0]].isnull())
                    & (poly_gdf[no_data_cols[i][1]].isnull())
                ].plot(
                    ax=ax,
                    facecolor=na_facecolor,
                    edgecolor=na_edgecolor,
                    linewidth=na_linewidth,
                    hatch=na_hatch,
                    alpha=na_alpha,
                )

                ax.legend(handles=[na_legend], loc=legend_loc)

            elif (
                type(no_data_cols[i]) == str
                and len(poly_gdf[poly_gdf[no_data_cols[i]].isnull()]) > 0
            ):
                poly_gdf[poly_gdf[no_data_cols[i]].isnull()].plot(
                    ax=ax,
                    facecolor=na_facecolor,
                    edgecolor=na_edgecolor,
                    linewidth=na_linewidth,
                    hatch=na_hatch,
                    alpha=na_alpha,
                )

                ax.legend(handles=[na_legend], loc=legend_loc)

        if plot_res == "high":
            fig.savefig(filepaths[i] + ".svg", dpi=dpi)
        else:
            fig.savefig(filepaths[i] + ".png", dpi=dpi)
