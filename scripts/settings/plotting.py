import matplotlib as mpl
from matplotlib import cm, colors

import matplotlib_inline.backend_inline


# Plot parameters
mpl.rcParams["savefig.bbox"] = "tight"
mpl.rcParams["xtick.minor.visible"] = False
mpl.rcParams["xtick.major.size"] = 0
mpl.rcParams["xtick.labelbottom"] = True
mpl.rcParams["ytick.major.size"] = 3
mpl.rcParams["font.size"] = 10
mpl.rcParams["figure.titlesize"] = 10
mpl.rcParams["legend.title_fontsize"] = 10
mpl.rcParams["legend.fontsize"] = 9
# mpl.rcParams["figure.labelsize"] = 10 # use if figure.titlesize does not work?
mpl.rcParams["axes.labelsize"] = 10
mpl.rcParams["xtick.labelsize"] = 9
mpl.rcParams["ytick.labelsize"] = 9
mpl.rcParams["hatch.linewidth"] = 0.5


pdict = {
    # grid; polygon; base barplots
    "base": "black",
    "base2": "grey",
    "compare_base": "black",  # "dimgray",
    # colormaps for grid cell plots
    "pos": "Blues",  # Positive values (but not percentages)
    "neg": "Reds",  # Negative/Missing/Unmatched values
    "diff": "RdBu",  # for osm-ref difference plots (alternatives: "PiYG", "PRGn", "PuOr")
    "seq": "YlGnBu",  # for sequential plots where low should not be white (usually percentages)
    # alpha (transparency) values (alternatives: PuRd, RdPu, PbBuGn)
    "alpha_back": 0.5,  # for unicolor plots with relevant background
    "alpha_bar": 0.7,  # for partially overlapping stats barplots
    "alpha_grid": 0.9,  # for multicolor/divcolor gridplots
    "alpha_nodata": 0.3,  # for no data patches
    # linewidths (base, emphasis, emphasis2)
    # "line_base": 1,
    # "line_emp": 3,
    # "line_emp2": 5,
    "line_nodata": 0.3,
    # widths for bar plots; single: for 1 value, double: for 2 values comparison
    "bar_single": 0.4,
    "bar_double": 0.75,
    # marker sizes (base, emphasis)
    # "mark_base": 2,
    # "mark_emp": 6,
    # Colors of no-data grid cell patches
    "nodata": "grey",
    "nodata_face": "none",
    "nodata_edge": "grey",
    "nodata_hatch": "//",
    # GLOBAL SETTINGS FOR PLOTS
    "dpi": 300,  # resolution
    # matplotlib figure size for map plots of study area
    "fsmap": (13, 7.3125),
    # size for bar plots
    "fsbar": (8, 8),
    "fsbar_small": (4, 3.5),
    "fsbar_short": (6, 3),
    "fsbar_sub": (4, 3),  # size per subplot
}

# patches for geopandas plots legend of "no data"
import matplotlib.patches as mpatches

nodata_patch = mpatches.Patch(
    facecolor=pdict["nodata_face"],
    edgecolor=pdict["nodata_edge"],
    linewidth=0.3,
    label="No data",
    hatch=pdict["nodata_hatch"],
    alpha=pdict["alpha_nodata"],
)

import contextily as cx

cx_tile_1 = cx.providers.CartoDB.Voyager
cx_tile_2 = cx.providers.CartoDB.Positron
