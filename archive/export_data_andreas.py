# %%
import geopandas as gpd
import yaml
from src import db_functions as dbf

with open(r"../config.yml") as file:
    parsed_yaml_file = yaml.load(file, Loader=yaml.FullLoader)

    db_name = parsed_yaml_file["db_name"]
    input_db_name = parsed_yaml_file["input_db_name"]
    db_user = parsed_yaml_file["db_user"]
    db_password = parsed_yaml_file["db_password"]
    db_host = parsed_yaml_file["db_host"]
    db_port = parsed_yaml_file["db_port"]
    network_edges = parsed_yaml_file["network_edges"]
    network_nodes = parsed_yaml_file["network_nodes"]

print("Settings loaded!")

# %%
engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)


municipalities = [
    # "Albertslund",
    # "Allerød",
    # "Ballerup",
    # "Brøndby",
    # "Dragør",
    # "Egedal",
    # "Fredensborg",
    "Frederiksberg",
    # "Frederikssund",
    # "Furesø",
    # "Gentofte",
    # "Gladsaxe",
    # "Glostrup",
    # "Greve",
    # "Gribskov",
    # "Halsnæs",
    # "Helsingør",
    # "Herlev",
    # "Hillerød",
    # "Hvidovre",
    # "Høje-Taastrup",
    # "Hørsholm",
    # "Ishøj",
    "København",
    # "Køge",
    # "Lyngby-Taarbæk",
    # "Roskilde",
    # "Rudersdal",
    # "Rødovre",
    # "Solrød",
    # "Tårnby",
    # "Vallensbæk",
]

queries = [
    "export_andreas.sql",
]

for i, q in enumerate(queries):
    print(f"Running step {i+1}...")
    result = dbf.run_query_pg(q, connection)
    if result == "error":
        print("Please fix error before rerunning and reconnect to the database")
        break

    print(f"Step {i+1} done!")


edges = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM andreas_export;", engine, geom_col="geometry"
)
nodes = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM andreas_export_nodes;", engine, geom_col="geometry"
)

print("Data retrieved!")

# %%
assert len(edges.municipality.unique()) == len(municipalities)

# %%
edges.to_file("../data/edges_udtraek.gpkg")

# %%
nodes.to_file("../data/nodes_udtraek.gpkg")

print("Data saved!")

connection.close()

# %%


def plot_grid_results(
    grid,
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
    crs=study_crs,
    legend=True,
    set_axis_off=True,
    legend_loc="upper left",
    use_norm=False,
    norm_min=None,
    norm_max=None,
    plot_res=plot_res,
    attr=None,
):
    """
    Make multiple choropleth maps of e.g. grid with analysis results based on a list of geodataframe columns to be plotted
    and save them in separate files
    Arguments:
        grid (gdf): geodataframe with polygons to be plotted
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
        na_linewidth (numeric): width of edge lines of no data grid cells
        na_legend(matplotlib Patch): patch to be used for the no data layer in the legend
        figsize(tuple): size of each plot
        dpi(numeric): resolution of saved plots
        crs (string): name of crs used for the grid (to set correct crs of basemap)
        legend (bool): True if a legend/colorbar should be plotted
        set_axis_off (bool): True if axis ticks and values should be omitted
        legend_loc (string): Position of map legend (see matplotlib doc for valid entries)
        use_norm (bool): True if colormap should be defined based on provided min and max values
        norm_min(numeric): min value to use for norming color map
        norm_max(numeric): max value to use for norming color map
        #formats (list): list of file formats
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

            grid.plot(
                cax=cax,
                ax=ax,
                column=c,
                legend=legend,
                alpha=alpha,
                norm=cbnorm,
                cmap=cmaps[i],
            )

        else:
            grid.plot(
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

        # add patches in grid cells with no data on edges
        if type(no_data_cols[i]) == tuple:

            grid[
                (grid[no_data_cols[i][0]].isnull())
                & (grid[no_data_cols[i][1]].isnull())
            ].plot(
                ax=ax,
                facecolor=na_facecolor,
                edgecolor=na_edgecolor,
                linewidth=na_linewidth,
                hatch=na_hatch,
                alpha=na_alpha,
            )

        else:
            grid[grid[no_data_cols[i]].isnull()].plot(
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

        # for f in formats:
        #     fig.savefig(filepaths[i] + "." + f, dpi=dpi)
