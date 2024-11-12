# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
from src import analysis_functions as analysis_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import contextily as cx
from mpl_toolkits.axes_grid1 import make_axes_locatable
import geopandas as gpd
from matplotlib_scalebar.scalebar import ScaleBar
import math
import itertools

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/filepaths.py").read())
plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

# %%
# Get socio data

socio_gdf = gpd.read_postgis(
    "SELECT population_density, urban_pct, geometry FROM socio",
    engine,
    geom_col="geometry",
)
# %%
# Population
plot_res = "low"

filepath = "../illustrations/socio_population_density"

fig, ax = plt.subplots(figsize=pdict["fsmap"])

socio_gdf.plot(
    ax=ax,
    scheme="quantiles",  # "natural_breaks",
    k=4,
    column="population_density",
    cmap="cividis",
    linewidth=0.0,
    edgecolor="none",
    legend=True,
    legend_kwds={
        # "fmt": "{:.0f}",
        "frameon": False,
        "fontsize": pdict["map_legend_fs"],
    },
)

# Access the legend
legend = ax.get_legend()

new_labels = []
for text in legend.get_texts():
    label = text.get_text()  # Extract the label text

    label_split = label.split(",")

    first_val = label_split[0]
    second_val = label_split[1].strip(" ")

    new_labels.append(
        f"{int(round(float(first_val), -1))}"
        + ", "
        + f"{int(round(float(second_val), -1))}"
    )

# Update the legend text
for text, new_label in zip(legend.get_texts(), new_labels):
    text.set_text(new_label)

ax.set_axis_off()
ax.set_title("Population density (people/km²)", fontsize=pdict["map_title_fs"])

ax.add_artist(
    ScaleBar(
        dx=1,
        units="m",
        dimension="si-length",
        length_fraction=0.15,
        width_fraction=0.002,
        location="lower left",
        box_alpha=0,
        font_properties={"size": pdict["map_legend_fs"]},
    )
)
cx.add_attribution(
    ax=ax,
    text="(C) " + "Statistics Denmark",
    font_size=pdict["map_legend_fs"],
)
txt = ax.texts[-1]
txt.set_position([0.99, 0.01])
txt.set_ha("right")
txt.set_va("bottom")

if plot_res == "high":
    fig.savefig(filepath + ".svg", dpi=pdict["dpi"])
else:
    fig.savefig(filepath + ".png", dpi=pdict["dpi"])

# %%
# Urban pct

plot_res = "low"

filepath = "../illustrations/socio_urban_pct"

fig, ax = plt.subplots(figsize=pdict["fsmap"])
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="3.5%", pad="1%")
cax.tick_params(labelsize=pdict["map_legend_fs"])

socio_gdf.plot(
    cax=cax,
    ax=ax,
    # scheme="fisher_jenks",
    # k=5,
    column="urban_pct",
    cmap="PuRd",
    linewidth=0.0,
    edgecolor="none",
    legend=True,
    legend_kwds={"fmt": "{:.0f}"},
)

sm = plt.cm.ScalarMappable(
    cmap="PuRd",
    norm=plt.Normalize(
        vmin=socio_gdf["urban_pct"].min(), vmax=socio_gdf["urban_pct"].max()
    ),
)
sm._A = []
cbar = fig.colorbar(sm, cax=cax)
cbar.outline.set_visible(False)  # Remove the outline of the colorbar

ax.set_axis_off()
ax.set_title("Urban areas (%)", fontsize=pdict["map_title_fs"])

ax.add_artist(
    ScaleBar(
        dx=1,
        units="m",
        dimension="si-length",
        length_fraction=0.15,
        width_fraction=0.002,
        location="lower left",
        box_alpha=0,
        font_properties={"size": pdict["map_legend_fs"]},
    )
)
cx.add_attribution(
    ax=ax,
    text="(C) " + "Statistics Denmark",
    font_size=pdict["map_legend_fs"],
)
txt = ax.texts[-1]
txt.set_position([0.99, 0.01])
txt.set_ha("right")
txt.set_va("bottom")

if plot_res == "high":
    fig.savefig(filepath + ".svg", dpi=pdict["dpi"])
else:
    fig.savefig(filepath + ".png", dpi=pdict["dpi"])

# %%

exec(open("../helper_scripts/read_socio_pop.py").read())

# %%
plot_res = "low"

for label, plot_columns in zip(["income", "cars"], [socio_income_vars, socio_car_vars]):

    filepath = f"../illustrations/socio_vars_{label}"

    row_num = math.ceil(len(plot_columns) / 3)

    height = row_num * 3 + 1
    width = 10
    figsize = (width, height)

    fig, axes = plt.subplots(nrows=row_num, ncols=3, figsize=figsize)

    axes = axes.flatten()

    rmv_idx = len(plot_columns) - len(axes)
    for r in range(rmv_idx, 0):
        fig.delaxes(axes[r])

    for i, p in enumerate(plot_columns):

        ax = axes[i]

        socio.plot(
            column=p,
            legend=True,
            linewidth=0.0,
            ax=ax,
            edgecolor="none",
            scheme="natural_breaks",
            k=5,
            legend_kwds={
                "frameon": False,
                "loc": "upper right",
                # "bbox_to_anchor": legend_pos,
                "fontsize": pdict["legend_fs"],
                "fmt": "{:.0f}",
            },
            cmap="cividis",
        )

        # # Update the legend text
        # for text, new_label in zip(legend.get_texts(), new_labels):
        #     text.set_text(new_label)

        ax.set_axis_off()
        ax.set_title(p, fontsize=pdict["title_fs"])

    fig.tight_layout()

    fig.savefig(filepath, bbox_inches="tight", dpi=pdict["dpi"])
# %%

# Make bivariate maps!

# Based on https://waterprogramming.wordpress.com/2022/09/08/bivariate-choropleth-maps/

from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
from matplotlib.colors import rgb2hex
from generativepy.color import Color
from PIL import ImageColor


### function to convert hex color to rgb to Color object (generativepy package)
def hex_to_Color(hexcode):
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
    _ = legend_ax.set_xticks(list(range(len(class_bounds) + 1)), xticks)
    _ = legend_ax.set_yticks(list(range(len(class_bounds) + 1)), yticks)
    _ = legend_ax.set_xlabel(col1_label)
    _ = legend_ax.set_ylabel(col2_label)

    plt.tight_layout()

    if fp:
        plt.savefig(fp, dpi=pdict["dpi"])

    plt.show()
    plt.close()


# %%

### percentile bounds defining upper boundaries of color classes
class_bounds = [0.25, 0.50, 0.75, 1]

### get corner colors from https://www.joshuastevens.net/cartography/make-a-bivariate-choropleth-map/
c00 = hex_to_Color("#e8e8e8")
c10 = hex_to_Color("#be64ac")
c01 = hex_to_Color("#5ac8c8")
c11 = hex_to_Color("#3b4994")

colorlist = create_color_grid(class_bounds, c00, c10, c01, c11)

### convert back to hex color
colorlist = [rgb2hex([c.r, c.g, c.b]) for c in colorlist]

# %%
socio_hex_cluster = gpd.read_postgis(
    "SELECT * FROM clustering.socio_socio_clusters", engine, geom_col="geometry"
)
socio_hex_cluster.fillna(0, inplace=True)

exec(open("../helper_scripts/read_socio_pop.py").read())

socio.drop(columns=["geometry"], inplace=True)

socio_socio_bike = socio_hex_cluster.merge(socio, on="id")

# socio_corr_variables.remove("Household income 50th percentile")

# socio_corr_variables.remove("Population density")

analysis_vars = socio_corr_variables
analysis_vars.append("average_bikeability_rank")

variable_combos = list(itertools.combinations(analysis_vars, 2))
# %%

analysis_func.normalize_data(socio_socio_bike, analysis_vars)

# %%
for v in variable_combos:

    v0 = v[0] + "_norm"
    v1 = v[1] + "_norm"

    make_bivariate_choropleth_map(
        socio_socio_bike,
        v0,
        v1,
        v[0],
        v[1],
        class_bounds,
        colorlist,
    )

# %%

make_bivariate_choropleth_map(
    socio_socio_bike,
    "average_bikeability_rank",
    "Households w car (share)",
    "bike",
    "Cars",
    class_bounds,
    colorlist,
)

# %%

# %%


# def get_bivariate_choropleth_color(p1, p2, class_bounds, colorlist):
#     print(p1, p2)
#     if p1 >= 0 and p2 >= 0:
#         count = 0
#         stop = False
#         for percentile_bound_p1 in class_bounds:
#             for percentile_bound_p2 in class_bounds:
#                 if (not stop) and (p1 <= percentile_bound_p1):
#                     if (not stop) and (p2 <= percentile_bound_p2):
#                         color = colorlist[count]
#                         stop = True
#                 count += 1
#     else:
#         color = [0.8, 0.8, 0.8, 1]
#     return color


# gdf = socio_socio_bike.copy()

# col1, col2 = ("0-17 years (share)", "Household income 50th percentile")
# gdf["color_bivariate"] = [
#     get_bivariate_choropleth_color(p1, p2, class_bounds, colorlist)
#     for p1, p2 in zip(gdf[col1].values, gdf[col2].values)
# ]

# # %%

# for p1, p2 in zip(gdf[col1].values, gdf[col2].values):
#     print(p1, p2)
# %%
