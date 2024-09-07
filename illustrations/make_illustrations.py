# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import contextily as cx
from mpl_toolkits.axes_grid1 import make_axes_locatable
import geopandas as gpd
from matplotlib_scalebar.scalebar import ScaleBar
from shapely.geometry import Point
import numpy as np

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/filepaths.py").read())
plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

# %%
# Get full network
network = gpd.read_postgis(
    "SELECT id, geometry FROM edges WHERE lts_access IN (1,2,3,4,7)",
    engine,
    geom_col="geometry",
)

plot_res = "low"

filepath = "../illustrations/overview_map"

fig, ax = plt.subplots(figsize=pdict["fsmap"])

network.plot(ax=ax, color="black", linewidth=0.2)

ax.set_axis_off()
ax.set_title("Road and path network", fontsize=pdict["map_title_fs"])

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
    ax=ax, text="(C) " + pdict["map_attr"], font_size=pdict["map_legend_fs"]
)
txt = ax.texts[-1]
txt.set_position([0.99, 0.01])
txt.set_ha("right")
txt.set_va("bottom")

if plot_res == "high":
    fig.savefig(filepath + ".svg", dpi=pdict["dpi"])
else:
    fig.savefig(filepath + ".png", dpi=pdict["dpi"])


del network
# %%
population = gpd.read_postgis(
    "SELECT population, population_density, urban_pct, geometry FROM hex_grid",
    engine,
    geom_col="geometry",
)

plot_res = "low"

filepath = "../illustrations/population_map"

fig, ax = plt.subplots(figsize=pdict["fsmap"])

population.plot(
    ax=ax,
    scheme="natural_breaks",
    k=8,
    column="population_density",
    cmap="viridis_r",
    linewidth=0.0,
    edgecolor="none",
    legend=True,
    legend_kwds={
        # "fmt": "{:.0f}",
        "frameon": False,
        "fontsize": pdict["map_legend_fs"],
    },
)

# # Access the legend
legend = ax.get_legend()

new_labels = []
for text in legend.get_texts():
    label = text.get_text()  # Extract the label text

    label_split = label.split(",")

    first_val = label_split[0]
    second_val = label_split[1].strip(" ")

    new_labels.append(
        f"{int(round(float(first_val), -2))}"
        + ", "
        + f"{int(round(float(second_val), -2))}"
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
cx.add_attribution(ax=ax, text="(C) " + "GHSL", font_size=pdict["map_legend_fs"])
txt = ax.texts[-1]
txt.set_position([0.99, 0.01])
txt.set_ha("right")
txt.set_va("bottom")

if plot_res == "high":
    fig.savefig(filepath + ".svg", dpi=pdict["dpi"])
else:
    fig.savefig(filepath + ".png", dpi=pdict["dpi"])


# %%
filepath = "../illustrations/urban_areas"

fig, ax = plt.subplots(figsize=pdict["fsmap"])
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="3.5%", pad="1%")
cax.tick_params(labelsize=pdict["map_legend_fs"])

population.plot(
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
cx.add_attribution(ax=ax, text="(C) " + "SDFI", font_size=pdict["map_legend_fs"])
txt = ax.texts[-1]
txt.set_position([0.99, 0.01])
txt.set_ha("right")
txt.set_va("bottom")

if plot_res == "high":
    fig.savefig(filepath + ".svg", dpi=pdict["dpi"])
else:
    fig.savefig(filepath + ".png", dpi=pdict["dpi"])

del population
# %%
# Plot hex grid

hex_grid = gpd.read_postgis(
    "SELECT hex_id, geometry FROM hex_grid", engine, geom_col="geometry"
)

xmin, ymin = (689922, 6161099 - 200)
xmax = xmin + 3000
ymax = ymin + 3000

plot_res = "low"

filepath = "../illustrations/hex_grid"

fig, ax = plt.subplots(figsize=pdict["fsmap"])

hex_grid.plot(
    ax=ax,
    color="none",
    edgecolor="black",
    linewidth=1,
    legend=False,
)

ax.axis([xmin, xmax, ymin, ymax])

ax.set_axis_off()
ax.set_title("Hex grid")

ax.add_artist(
    ScaleBar(
        dx=1,
        units="m",
        dimension="si-length",
        length_fraction=0.15,
        width_fraction=0.002,
        location="lower right",
        box_alpha=0,
    )
)

cx.add_basemap(ax, crs=hex_grid.crs, source=cx.providers.CartoDB.PositronNoLabels)

if plot_res == "high":
    fig.savefig(filepath + ".svg", dpi=pdict["dpi"])
else:
    fig.savefig(filepath + ".png", dpi=pdict["dpi"])

del hex_grid
# %%
# Density illustration

exec(open("../helper_scripts/read_density.py").read())

del density_muni
del density_socio

edges = gpd.read_postgis(
    "SELECT id, geometry, lts_access FROM edges WHERE lts_access IN (1,2,3,4)",
    engine,
    geom_col="geometry",
)

lts1_edges = edges[edges.lts_access == 1]
# %%
# xmin, ymin = (689922 - 1000, 6161099 - 2000)
# xmax = xmin + 3000
# ymax = ymin + 3000

xmin, ymin = (639464.351371, 6120027.316230)
xmax, ymax = (699033.929025, 6173403.495114)
xmin += 12000
xmax -= 6000
ymin += 12000
ymax -= 6000

plot_res = "low"

filepath = "../illustrations/density"

fig, ax = plt.subplots(figsize=pdict["fsmap"])

density_hex.plot(
    ax=ax,
    column="lts_1_dens",  # "lts_1_4_dens",
    cmap="PuRd",
    edgecolor="none",
    linewidth=0,
    legend=False,
)

lts1_edges.plot(
    ax=ax,
    color="black",
    linewidth=1,
    legend=False,
)

ax.axis([xmin, xmax, ymin, ymax])

ax.set_axis_off()
ax.set_title("Density")

ax.add_artist(
    ScaleBar(
        dx=1,
        units="m",
        dimension="si-length",
        length_fraction=0.15,
        width_fraction=0.002,
        location="lower right",
        box_alpha=0,
    )
)

if plot_res == "high":
    fig.savefig(filepath + ".svg", dpi=pdict["dpi"])
else:
    fig.savefig(filepath + ".png", dpi=pdict["dpi"])

# %%
# Make zoomed component plot

component_edges = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM fragmentation.component_edges;", engine, geom_col="geometry"
)

lts_subset = component_edges[component_edges.component_1.notna()]

xmin, ymin = (639464.351371, 6120027.316230)
xmax, ymax = (699033.929025, 6173403.495114)
xmin += 12000
xmax -= 6000
ymin += 12000
ymax -= 6000

plot_func.plot_components_zoom(
    lts_subset,
    "component_1",
    "Set2",
    "components.png",
    xmin,
    ymin,
    xmax,
    ymax,
)

del component_edges
del lts_subset


# %%

# Read segment data


# %%
xmin, ymin = (639464.351371, 6120027.316230)
xmax, ymax = (699033.929025, 6173403.495114)
xmin += 12000
xmax -= 6000
ymin += 12000
ymax -= 6000

exec(open("reach_segment_ids.py").read())

startnode = gpd.GeoDataFrame.from_postgis(
    f"SELECT * FROM reach.hex_lts_1 WHERE node_id = {node_id};",
    engine,
    geom_col="node_geom",
)

all_reach_edges = gpd.GeoDataFrame.from_postgis(
    f"SELECT * FROM reach.lts_1_segments;",
    engine,
    geom_col="geometry",
)

reach_edges_15 = gpd.GeoDataFrame.from_postgis(
    f"SELECT * FROM reach.lts_1_segments WHERE id IN {segment_ids_15};",
    engine,
    geom_col="geometry",
)

reach_edges_10 = gpd.GeoDataFrame.from_postgis(
    f"SELECT * FROM reach.lts_1_segments WHERE id IN {segment_ids_10};",
    engine,
    geom_col="geometry",
)

reach_edges_5 = gpd.GeoDataFrame.from_postgis(
    f"SELECT * FROM reach.lts_1_segments WHERE id IN {segment_ids_5};",
    engine,
    geom_col="geometry",
)
# %%
plot_res = "low"

filepath = "../illustrations/reach"

fig, ax = plt.subplots(figsize=pdict["fsmap"])

all_reach_edges.plot(
    ax=ax,
    color="lightgrey",
    linewidth=1,
    legend=False,
)

reach_edges_15.plot(
    ax=ax,
    color="#6699cc",
    linewidth=1.5,
    legend=False,
)
reach_edges_10.plot(
    ax=ax,
    color="#994455",
    linewidth=1.7,
    legend=False,
)

startnode.plot(ax=ax, color="black", markersize=40, alpha=1)

ax.axis([xmin, xmax, ymin, ymax])

ax.set_axis_off()
ax.set_title("Reach")

ax.add_artist(
    ScaleBar(
        dx=1,
        units="m",
        dimension="si-length",
        length_fraction=0.15,
        width_fraction=0.002,
        location="lower right",
        box_alpha=0,
    )
)

if plot_res == "high":
    fig.savefig(filepath + ".svg", dpi=pdict["dpi"])
else:
    fig.savefig(filepath + ".png", dpi=pdict["dpi"])

# %%

xmin, ymin = (639464.351371, 6120027.316230)
xmax, ymax = (699033.929025, 6173403.495114)

density_hex = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM density.density_hex;",
    engine,
    crs=crs,
    geom_col="geometry",
)

density_hex.replace(0, np.nan, inplace=True)

edges = gpd.read_postgis(
    "SELECT id, geometry FROM edges WHERE lts_access IN (1,2,3,4)",
    engine,
    geom_col="geometry",
)
# %%

# PLOT LTS NETWORK
