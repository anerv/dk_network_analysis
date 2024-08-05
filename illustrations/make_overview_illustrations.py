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
# %%
plot_res = "low"

filepath = "../illustrations/overview_map"

fig, ax = plt.subplots(figsize=pdict["fsmap"])

network.plot(ax=ax, color="black", linewidth=0.2)

ax.set_axis_off()
ax.set_title("Road and path network")

ax.add_artist(
    ScaleBar(
        dx=1,
        units="m",
        dimension="si-length",
        length_fraction=0.15,
        width_fraction=0.002,
        location="lower left",
        box_alpha=0,
    )
)
cx.add_attribution(ax=ax, text="(C) " + pdict["map_attr"])
txt = ax.texts[-1]
txt.set_position([0.99, 0.01])
txt.set_ha("right")
txt.set_va("bottom")

if plot_res == "high":
    fig.savefig(filepath + ".svg", dpi=pdict["dpi"])
else:
    fig.savefig(filepath + ".png", dpi=pdict["dpi"])

# %%
population = gpd.read_postgis(
    "SELECT population, population_density, urban_pct, geometry FROM hex_grid",
    engine,
    geom_col="geometry",
)
# %%
plot_res = "low"

filepath = "../illustrations/population_map"

fig, ax = plt.subplots(figsize=pdict["fsmap"])

population.plot(
    # cax=cax,
    ax=ax,
    scheme="natural_breaks",
    k=5,
    column="population_density",
    cmap="viridis",
    linewidth=0.0,
    edgecolor="none",
    legend=True,
    legend_kwds={"fmt": "{:.0f}", "frameon": False},
)

ax.set_axis_off()
ax.set_title("Population density (people/km²)")

ax.add_artist(
    ScaleBar(
        dx=1,
        units="m",
        dimension="si-length",
        length_fraction=0.15,
        width_fraction=0.002,
        location="lower left",
        box_alpha=0,
    )
)
cx.add_attribution(ax=ax, text="(C) " + "GHSL")
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
ax.set_title("Urban areas (%)")

ax.add_artist(
    ScaleBar(
        dx=1,
        units="m",
        dimension="si-length",
        length_fraction=0.15,
        width_fraction=0.002,
        location="lower left",
        box_alpha=0,
    )
)
cx.add_attribution(ax=ax, text="(C) " + "SDFI")
txt = ax.texts[-1]
txt.set_position([0.99, 0.01])
txt.set_ha("right")
txt.set_va("bottom")

if plot_res == "high":
    fig.savefig(filepath + ".svg", dpi=pdict["dpi"])
else:
    fig.savefig(filepath + ".png", dpi=pdict["dpi"])

# %%
# Plot hex grid

hex_grid = gpd.read_postgis(
    "SELECT hex_id, geometry FROM hex_grid", engine, geom_col="geometry"
)

# %%
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

# %%
# Density illustration

exec(open("../helper_scripts/read_density.py").read())

del density_muni
del density_socio

edges = gpd.read_postgis(
    "SELECT id, geometry FROM edges WHERE lts_access IN (1,2,3,4)",
    engine,
    geom_col="geometry",
)
# %%
xmin, ymin = (689922 - 1000, 6161099 - 2000)
xmax = xmin + 3000
ymax = ymin + 3000

plot_res = "low"

filepath = "../illustrations/density"

fig, ax = plt.subplots(figsize=pdict["fsmap"])

density_hex.plot(
    ax=ax,
    column="lts_1_4_dens",
    cmap="PuRd",
    edgecolor="none",
    linewidth=0,
    legend=False,
)

edges.plot(
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
lts1_edges = gpd.read_postgis(
    "SELECT id, geometry FROM edges WHERE lts_access IN (1)",
    engine,
    geom_col="geometry",
)

# %%
xmin, ymin = (689922 - 1000, 6161099 - 2000)
xmax = xmin + 3000
ymax = ymin + 3000

plot_res = "low"

filepath = "../illustrations/reach"

fig, ax = plt.subplots(figsize=pdict["fsmap"])

lts1_edges.plot(
    ax=ax,
    color="black",
    linewidth=1,
    legend=False,
)

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
