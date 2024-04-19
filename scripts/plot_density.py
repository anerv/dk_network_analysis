# %%
from src import db_functions as dbf
from src import h3_functions as h3f
import geopandas as gpd
import numpy as np

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)
# %%
import matplotlib as mpl
from matplotlib import cm, colors
import matplotlib.pyplot as plt
import matplotlib_inline.backend_inline
from mpl_toolkits.axes_grid1 import make_axes_locatable
import contextily as cx


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


# %%
# PLOT MUNI DENSITY

density_muni = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM density_municipality;",
    engine,
    crs=crs,
    geom_col="geometry",
)
density_muni.replace(0, np.nan, inplace=True)

plot_cols = [
    "lts_1_dens",
    "lts_2_dens",
    "lts_3_dens",
    "lts_4_dens",
    "total_car_dens",
    "total_network_dens",
]
labels = ["LTS 1", "LTS 2", "LTS 3", "LTS 4", "Total car", "Total network"]
plot_titles = [f"Municipal network density for: {l}" for l in labels]
no_data_cols = plot_cols
filepaths = [f"../results/network_density/administrative/{l}" for l in labels]
cmaps = [pdict["pos"]] * len(plot_cols)

plot_polygon_results(
    poly_gdf=density_muni,
    plot_cols=plot_cols,
    plot_titles=plot_titles,
    filepaths=filepaths,
    cmaps=cmaps,
    alpha=pdict["alpha_grid"],
    cx_tile=cx_tile_2,
    no_data_cols=no_data_cols,
)

# Stepwise density
plot_cols = [
    "lts_1_dens",
    "lts_1_2_dens",
    "lts_1_3_dens",
    "lts_1_4_dens",
    "total_car_dens",
    "total_network_dens",
]
labels = ["LTS 1", "LTS 1-2", "LTS 1-3", "LTS 1-4", "Total car", "Total network"]
plot_titles = [f"Municipal network density for: {l}" for l in labels]
no_data_cols = plot_cols
filepaths = [f"../results/network_density/administrative/{l}" for l in labels]
cmaps = [pdict["pos"]] * len(plot_cols)

plot_polygon_results(
    poly_gdf=density_muni,
    plot_cols=plot_cols,
    plot_titles=plot_titles,
    filepaths=filepaths,
    cmaps=cmaps,
    alpha=pdict["alpha_grid"],
    cx_tile=cx_tile_2,
    no_data_cols=no_data_cols,
)

# Relative network length
plot_cols = [
    "lts_1_length_rel",
    "lts_1_2_length_rel",
    "lts_1_3_length_rel",
    "lts_1_4_length_rel",
    "lts_7_length_rel",
    # "total_car_length_rel",
]
for p in plot_cols:
    density_muni[p] = density_muni[p] * 100

labels = [
    "LTS 1 (%)",
    "LTS 1-2 (%)",
    "LTS 1-3 (%)",
    "LTS 1-4 (%)",
    "No biking (%)",
    # "Total car (%)",
]

plot_titles = [f"Municipal network length for: {l}" for l in labels]
no_data_cols = plot_cols
filepaths = [f"../results/network_density/administrative/{l}" for l in labels]
cmaps = [pdict["pos"]] * len(plot_cols)

plot_polygon_results(
    poly_gdf=density_muni,
    plot_cols=plot_cols,
    plot_titles=plot_titles,
    filepaths=filepaths,
    cmaps=cmaps,
    alpha=pdict["alpha_grid"],
    cx_tile=cx_tile_2,
    no_data_cols=no_data_cols,
)
# %%
# SOCIO

density_socio = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM density_socio;",
    engine,
    crs=crs,
    geom_col="geometry",
)

density_socio.replace(0, np.nan, inplace=True)

plot_cols = [
    "lts_1_dens",
    "lts_2_dens",
    "lts_3_dens",
    "lts_4_dens",
    "total_car_dens",
    "total_network_dens",
]
labels = ["LTS 1", "LTS 2", "LTS 3", "LTS 4", "Total car", "Total network"]
plot_titles = [f"Socio network density for: {l}" for l in labels]
no_data_cols = plot_cols
filepaths = [f"../results/network_density/socio/{l}" for l in labels]
cmaps = [pdict["pos"]] * len(plot_cols)

plot_polygon_results(
    poly_gdf=density_socio,
    plot_cols=plot_cols,
    plot_titles=plot_titles,
    filepaths=filepaths,
    cmaps=cmaps,
    alpha=pdict["alpha_grid"],
    cx_tile=cx_tile_2,
    no_data_cols=no_data_cols,
)

# Stepwise density
plot_cols = [
    "lts_1_dens",
    "lts_1_2_dens",
    "lts_1_3_dens",
    "lts_1_4_dens",
    "total_car_dens",
    "total_network_dens",
]
labels = ["LTS 1", "LTS 1-2", "LTS 1-3", "LTS 1-4", "Total car", "Total network"]
plot_titles = [f"Socio network density for: {l}" for l in labels]
no_data_cols = plot_cols
filepaths = [f"../results/network_density/socio/{l}" for l in labels]
cmaps = [pdict["pos"]] * len(plot_cols)

plot_polygon_results(
    poly_gdf=density_socio,
    plot_cols=plot_cols,
    plot_titles=plot_titles,
    filepaths=filepaths,
    cmaps=cmaps,
    alpha=pdict["alpha_grid"],
    cx_tile=cx_tile_2,
    no_data_cols=no_data_cols,
)

# Relative network length
plot_cols = [
    "lts_1_length_rel",
    "lts_1_2_length_rel",
    "lts_1_3_length_rel",
    "lts_1_4_length_rel",
    "lts_7_length_rel",
    # "total_car_length_rel",
]
for p in plot_cols:
    density_socio[p] = density_socio[p] * 100

labels = [
    "LTS 1 (%)",
    "LTS 1-2 (%)",
    "LTS 1-3 (%)",
    "LTS 1-4 (%)",
    "No biking (%)",
    # "Total car (%)",
]

plot_titles = [f"Socio network length for: {l}" for l in labels]
no_data_cols = plot_cols
filepaths = [f"../results/network_density/socio/{l}" for l in labels]
cmaps = [pdict["pos"]] * len(plot_cols)

plot_polygon_results(
    poly_gdf=density_socio,
    plot_cols=plot_cols,
    plot_titles=plot_titles,
    filepaths=filepaths,
    cmaps=cmaps,
    alpha=pdict["alpha_grid"],
    cx_tile=cx_tile_2,
    no_data_cols=no_data_cols,
)

# %%
# H3

density_h3 = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM density_h3;",
    engine,
    crs=crs,
    geom_col="geometry",
)

density_h3.replace(0, np.nan, inplace=True)

plot_cols = [
    "lts_1_dens",
    "lts_2_dens",
    "lts_3_dens",
    "lts_4_dens",
    "total_car_dens",
    "total_network_dens",
]
labels = ["LTS 1", "LTS 2", "LTS 3", "LTS 4", "Total car", "Total network"]
plot_titles = [f"Local network density for: {l}" for l in labels]
no_data_cols = plot_cols
filepaths = [f"../results/network_density/administrative/{l}.png" for l in labels]
cmaps = [pdict["pos"]] * len(plot_cols)

plot_polygon_results(
    poly_gdf=density_h3,
    plot_cols=plot_cols,
    plot_titles=plot_titles,
    filepaths=filepaths,
    cmaps=cmaps,
    alpha=pdict["alpha_grid"],
    cx_tile=cx_tile_2,
    no_data_cols=no_data_cols,
)

# Stepwise density
plot_cols = [
    "lts_1_dens",
    "lts_1_2_dens",
    "lts_1_3_dens",
    "lts_1_4_dens",
    "total_car_dens",
    "total_network_dens",
]
labels = ["LTS 1", "LTS 1-2", "LTS 1-3", "LTS 1-4", "Total car", "Total network"]
plot_titles = [f"Local network density for: {l}" for l in labels]
no_data_cols = plot_cols
filepaths = [f"../results/network_density/administrative/{l}.png" for l in labels]
cmaps = [pdict["pos"]] * len(plot_cols)

plot_polygon_results(
    poly_gdf=density_h3,
    plot_cols=plot_cols,
    plot_titles=plot_titles,
    filepaths=filepaths,
    cmaps=cmaps,
    alpha=pdict["alpha_grid"],
    cx_tile=cx_tile_2,
    no_data_cols=no_data_cols,
)

# Relative network length
plot_cols = [
    "lts_1_length_rel",
    "lts_1_2_length_rel",
    "lts_1_3_length_rel",
    "lts_1_4_length_rel",
    "lts_7_length_rel",
    # "total_car_length_rel",
]
for p in plot_cols:
    density_h3[p] = density_h3[p] * 100

labels = [
    "LTS 1 (%)",
    "LTS 1-2 (%)",
    "LTS 1-3 (%)",
    "LTS 1-4 (%)",
    "No biking (%)",
    # "Total car (%)",
]

plot_titles = [f"Local network length for: {l}" for l in labels]
no_data_cols = plot_cols
filepaths = [f"../results/network_density/administrative/{l}.png" for l in labels]
cmaps = [pdict["pos"]] * len(plot_cols)

plot_polygon_results(
    poly_gdf=density_h3,
    plot_cols=plot_cols,
    plot_titles=plot_titles,
    filepaths=filepaths,
    cmaps=cmaps,
    alpha=pdict["alpha_grid"],
    cx_tile=cx_tile_2,
    no_data_cols=no_data_cols,
)

# %%
# TODO: Plot distribution of network densities for each lts
