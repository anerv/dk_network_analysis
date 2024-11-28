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
from matplotlib.colors import rgb2hex

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
    k=7,
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

socio_hex_cluster = gpd.read_postgis(
    "SELECT * FROM clustering.socio_socio_clusters", engine, geom_col="geometry"
)
socio_hex_cluster.fillna(0, inplace=True)

exec(open("../helper_scripts/read_socio_pop.py").read())

socio.drop(columns=["geometry"], inplace=True)

socio_socio_bike = socio_hex_cluster.merge(socio, on="id")

# socio_corr_variables.remove("Household income 50th percentile")

# socio_corr_variables.remove("Population density")

# analysis_vars = socio_corr_variables[7:]
# analysis_vars.append("Average bikeability rank")

analysis_vars = [
    "Household income 50th percentile",
    "Household low income (share)",
    "Household medium income (share)",
    "Household high income (share)",
    "Households w car (share)",
    "Households 1 car (share)",
    "Households 2 cars (share)",
    "Households no car (share)",
    "Population density",
    "Urban area (%)",
    "Average bikeability rank",
]

socio_socio_bike.rename(
    columns={"average_bikeability_rank": "Average bikeability rank"}, inplace=True
)

socio_socio_bike["Household low income (share)"] = (
    socio_socio_bike["Income under 150k (share)"]
    + socio_socio_bike["Income 150-200k (share)"]
    + socio_socio_bike["Income 200-300k (share)"]
)
socio_socio_bike["Household medium income (share)"] = (
    socio_socio_bike["Income 300-400k (share)"]
    + socio_socio_bike["Income 400-500k (share)"]
)
socio_socio_bike["Household high income (share)"] = (
    socio_socio_bike["Income 500-750k (share)"]
    + socio_socio_bike["Income 750k+ (share)"]
)

variable_combos = list(itertools.combinations(analysis_vars, 2))

analysis_func.normalize_data(socio_socio_bike, analysis_vars)

### bounds defining upper boundaries of color classes - assumes data normalized to [0,1]
class_bounds = [0.25, 0.50, 0.75, 1]

### get corner colors from https://www.joshuastevens.net/cartography/make-a-bivariate-choropleth-map/
c00 = plot_func.hex_to_Color("#e8e8e8")
c10 = plot_func.hex_to_Color("#be64ac")
c01 = plot_func.hex_to_Color("#5ac8c8")
c11 = plot_func.hex_to_Color("#3b4994")

colorlist = plot_func.create_color_grid(class_bounds, c00, c10, c01, c11)
### convert back to hex color
colorlist = [rgb2hex([c.r, c.g, c.b]) for c in colorlist]

# %%
for v in variable_combos:

    v0 = v[0] + "_norm"
    v1 = v[1] + "_norm"

    plot_func.make_bivariate_choropleth_map(
        socio_socio_bike,
        v0,
        v1,
        v[0],
        v[1],
        class_bounds,
        colorlist,
        fp=f"socio_bivariate_{v[0]}_{v[1]}.png",
    )
# %%
