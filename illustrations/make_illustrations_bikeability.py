# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import contextily as cx
from mpl_toolkits.axes_grid1 import make_axes_locatable
import geopandas as gpd
from matplotlib_scalebar.scalebar import ScaleBar
import random
import seaborn as sns
import matplotlib.patches as mpatches
import matplotlib as mpl


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
ax.set_title("total network", fontsize=pdict["map_title_fs"])

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

# %%
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
plot_res = "low"

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

sm = plt.cm.ScalarMappable(
    cmap="PuRd",
    norm=plt.Normalize(
        vmin=population["urban_pct"].min(), vmax=population["urban_pct"].max()
    ),
)
sm._A = []
cbar = fig.colorbar(sm, cax=cax)
cbar.outline.set_visible(False)  # Remove the outline of the colorbar

ax.set_axis_off()
ax.set_title("urban areas (%)", fontsize=pdict["map_title_fs"])

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

cx.add_basemap(
    ax,
    crs=hex_grid.crs,
    source=cx.providers.CartoDB.PositronNoLabels,
    attribution=None,
    attribution_size=0,
)

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
    linewidth=0.5,
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
    "SELECT component_1, component_size_1, geometry FROM fragmentation.component_edges WHERE component_1 IS NOT NULL;",
    engine,
    geom_col="geometry",
)

xmin, ymin = (639464.351371, 6120027.316230)
xmax, ymax = (699033.929025, 6173403.495114)
xmin += 12000
xmax -= 6000
ymin += 12000
ymax -= 6000

lts_subset = component_edges.cx[xmin - 200 : xmax + 200, ymin - 200 : ymax + 200].copy()
del component_edges
# %%
# make unique random colors for each component
# from https://www.delftstack.com/howto/python/generate-random-colors-python/
colors = []
n = len(lts_subset.component_1.unique())
for i in range(n):
    color = "#" + "".join([random.choice("0123456789ABCDEF") for j in range(6)])
    colors.append(color)

lts_subset["color"] = lts_subset.component_1.map(
    dict(zip(lts_subset.component_1.unique(), colors))
)
# %%
fig, ax = plt.subplots(figsize=pdict["fsmap"])

lts_subset.plot(
    # column="component_1",
    categorical=True,
    legend=False,
    ax=ax,
    color=lts_subset.color,
    # cmap=cmap,
    linewidth=1.5,
    alpha=pdict["alpha"],
)

ax.axis([xmin, xmax, ymin, ymax])

ax.set_axis_off()

plt.tight_layout()

fig.savefig("components.png", dpi=pdict["dpi"])

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

# PLOT ALL LEVELS OF LTS NETWORK

# Get full network
total_network = gpd.read_postgis(
    "SELECT id, geometry, car_traffic, lts_access FROM edges WHERE lts_access IN (1,2,3,4,7)",
    engine,
    geom_col="geometry",
)
# %%
# Get subsets

xmin, ymin = (581406, 6134559)
xmax, ymax = (589089, 6140132)

total_network = total_network.cx[xmin - 200 : xmax + 200, ymin - 200 : ymax + 200]

lts1_network = total_network[total_network.lts_access == 1]

lts2_network = total_network[total_network.lts_access == 2]

lts3_network = total_network[total_network.lts_access == 3]

lts4_network = total_network[total_network.lts_access == 4]

car_network = total_network[
    total_network.lts_access.isin([1, 2, 3, 4, 7]) & total_network.car_traffic == True
]

# %%
plot_res = "low"

linewidth = 1.5
# %%
## LTS 1
filepath = f"../illustrations/lts_network_1"

fig, ax = plt.subplots(figsize=pdict["fsmap"])

lts1_network.plot(color=lts_color_dict["1"], linewidth=linewidth, ax=ax)

ax.axis([xmin, xmax, ymin, ymax])

ax.set_axis_off()

if plot_res == "high":
    fig.savefig(filepath + ".svg", dpi=pdict["dpi"])
else:
    fig.savefig(filepath + ".png", dpi=pdict["dpi"])

# %%
## LTS 1-2
filepath = f"../illustrations/lts_network_1_2"

fig, ax = plt.subplots(figsize=pdict["fsmap"])

lts1_network.plot(color=lts_color_dict["1"], linewidth=linewidth, ax=ax)
lts2_network.plot(color=lts_color_dict["2"], linewidth=linewidth, ax=ax)

ax.axis([xmin, xmax, ymin, ymax])

ax.set_axis_off()

if plot_res == "high":
    fig.savefig(filepath + ".svg", dpi=pdict["dpi"])
else:
    fig.savefig(filepath + ".png", dpi=pdict["dpi"])

# %%
# LTS 1-3
filepath = f"../illustrations/lts_network_1_3"

fig, ax = plt.subplots(figsize=pdict["fsmap"])

lts1_network.plot(color=lts_color_dict["1"], linewidth=linewidth, ax=ax)
lts2_network.plot(color=lts_color_dict["2"], linewidth=linewidth, ax=ax)
lts3_network.plot(color=lts_color_dict["3"], linewidth=linewidth + 0.2, ax=ax)

ax.axis([xmin, xmax, ymin, ymax])

ax.set_axis_off()

if plot_res == "high":
    fig.savefig(filepath + ".svg", dpi=pdict["dpi"])
else:
    fig.savefig(filepath + ".png", dpi=pdict["dpi"])

# %%
# LTS 1-4
filepath = f"../illustrations/lts_network_1_4"

fig, ax = plt.subplots(figsize=pdict["fsmap"])

lts1_network.plot(color=lts_color_dict["1"], linewidth=linewidth, ax=ax)
lts2_network.plot(color=lts_color_dict["2"], linewidth=linewidth, ax=ax)
lts3_network.plot(color=lts_color_dict["3"], linewidth=linewidth + 0.2, ax=ax)
lts4_network.plot(color=lts_color_dict["4"], linewidth=linewidth, ax=ax)

ax.axis([xmin, xmax, ymin, ymax])

ax.set_axis_off()

if plot_res == "high":
    fig.savefig(filepath + ".svg", dpi=pdict["dpi"])
else:
    fig.savefig(filepath + ".png", dpi=pdict["dpi"])

# %%
# Car

filepath = f"../illustrations/lts_network_car"

fig, ax = plt.subplots(figsize=pdict["fsmap"])

car_network.plot(color=lts_color_dict["car"], linewidth=linewidth, ax=ax)

ax.axis([xmin, xmax, ymin, ymax])

ax.set_axis_off()

if plot_res == "high":
    fig.savefig(filepath + ".svg", dpi=pdict["dpi"])
else:
    fig.savefig(filepath + ".png", dpi=pdict["dpi"])

# %%

# FULL NETWORK

filepath = f"../illustrations/lts_network_total"

fig, ax = plt.subplots(figsize=pdict["fsmap"])

total_network.plot(color=lts_color_dict["total"], linewidth=linewidth, ax=ax)

ax.axis([xmin, xmax, ymin, ymax])

ax.set_axis_off()

if plot_res == "high":
    fig.savefig(filepath + ".svg", dpi=pdict["dpi"])
else:
    fig.savefig(filepath + ".png", dpi=pdict["dpi"])

# %%

node_id = 686608

startnode = gpd.GeoDataFrame.from_postgis(
    f"SELECT * FROM reach.hex_lts_1 WHERE node_id = {node_id};",
    engine,
    geom_col="node_geom",
)

centroid = gpd.GeoDataFrame.from_postgis(
    f"SELECT * FROM reach.hex_lts_1 WHERE node_id = {node_id};",
    engine,
    geom_col="hex_centroid",
)

# %%
xmin = startnode.bounds.minx.values[0] - 800
xmax = startnode.bounds.maxx.values[0] + 800
ymin = startnode.bounds.miny.values[0] - 800
ymax = startnode.bounds.maxy.values[0] + 800

# %%

hex_grid = gpd.read_postgis(
    "SELECT hex_id, geometry FROM hex_grid", engine, geom_col="geometry"
)

hex_subset = hex_grid.cx[xmin - 200 : xmax + 200, ymin - 200 : ymax + 200].copy()
del hex_grid

component_edges = gpd.GeoDataFrame.from_postgis(
    "SELECT component_1, component_size_1, geometry FROM fragmentation.component_edges WHERE component_1 IS NOT NULL;",
    engine,
    geom_col="geometry",
)

comp_subset = component_edges.cx[
    xmin - 200 : xmax + 200, ymin - 200 : ymax + 200
].copy()
del component_edges

largest_comp = comp_subset[
    comp_subset.component_size_1 == comp_subset.component_size_1.max()
]
other_comps = comp_subset[
    comp_subset.component_size_1 != comp_subset.component_size_1.max()
]

plot_res = "low"

filepath = "../illustrations/reach_computation"

fig, ax = plt.subplots(figsize=pdict["fsmap"])

hex_subset.plot(
    ax=ax, color="none", edgecolor="black", linewidth=0.5, legend=False, alpha=0.8
)

largest_comp.plot(
    ax=ax,
    color="#994455",  # "indigo",
    linewidth=2,
    legend=False,
)
other_comps.plot(
    ax=ax,
    color="grey",
    linewidth=2,
    legend=False,
    linestyle="--",
)

startnode.plot(ax=ax, color="firebrick", markersize=40)

# centroid.plot(ax=ax, color="black", markersize=40)

ax.axis([xmin, xmax, ymin, ymax])

ax.set_axis_off()


if plot_res == "high":
    fig.savefig(filepath + ".svg", dpi=pdict["dpi"])
else:
    fig.savefig(filepath + ".png", dpi=pdict["dpi"])

# %%

total_area = "SELECT SUM(ST_Area(geometry)) / 1000000 FROM municipalities;"
urban_area = "SELECT SUM(ST_Area(geometry)) / 1000000 FROM urban_areas;"

total_area = dbf.run_query_pg(total_area, connection)[0][0]

urban_area = dbf.run_query_pg(urban_area, connection)[0][0]

rural_area = total_area - urban_area

area_df = pd.DataFrame(
    {"area": [urban_area, rural_area, total_area]},
    index=[
        "urban",
        "rural",
        "total",
    ],
)
area_df["share"] = area_df["area"] / area_df.loc["total", "area"] * 100

hex_grid = gpd.read_postgis("SELECT * FROM hex_grid", engine, geom_col="geometry")

urban_pop = hex_grid[hex_grid.urban_pct > 0].population.sum()
rural_pop = hex_grid[hex_grid.urban_pct == 0].population.sum()
total_pop = urban_pop + rural_pop

pop_df = pd.DataFrame(
    {"population": [urban_pop, rural_pop, total_pop]}, index=["urban", "rural", "total"]
)
pop_df["share"] = pop_df["population"] / pop_df.loc["total", "population"] * 100

# %%

data = {
    "category": ["population", "population", "area", "area"],
    "area": ["urban", "rural", "urban", "rural"],
    "share": [
        pop_df.loc["urban", "share"],
        pop_df.loc["rural", "share"],
        area_df.loc["urban", "share"],
        area_df.loc["rural", "share"],
    ],
}

df = pd.DataFrame(data)

df.set_index(["category", "area"], inplace=True)

df = df.sort_index(level=["category", "area"], ascending=[True, True])

df_unstacked = df.unstack()

# Reorder columns to ensure 'rural' comes last (farthest from the y-axis)
df_unstacked = df_unstacked.reorder_levels([1, 0], axis=1)
df_unstacked = df_unstacked[["urban", "rural"]]  # Reorder columns manually

colors = ["#332288"] * 4

filepath = "../illustrations/area_population_urban_rural"

fig, ax = plt.subplots(figsize=pdict["fsbar"])

df_unstacked.plot(
    kind="barh", stacked=True, ax=ax, legend=False, color=colors, width=0.15
)

sns.despine(top=True, right=True, left=True, bottom=True)

bars = [
    thing for thing in ax.containers if isinstance(thing, mpl.container.BarContainer)
]

for container in ax.containers:

    total_width = 0
    for i, rect in enumerate(container):
        width = rect.get_width()
        this_width = total_width + (width / 3)
        total_width += width
        ax.text(
            this_width,
            rect.get_y() - 0.05,
            f"{width:.0f}%",
            ha="center",
            va="bottom",
            color="black",
            fontsize=pdict["fontsize"],
        )

hatch_bars = bars[1::2]

for bar in hatch_bars:
    for patch in bar:
        patch.set_hatch("//")

ax.set(xticks=[], yticks=[])
ax.set_ylabel("")

plt.tight_layout()
plt.savefig(filepath + ".png", dpi=pdict["dpi"])
plt.show()

# %%
# LTS urban rural PLOT

# Get full network

lts_1_length_urban = dbf.run_query_pg(
    "SELECT SUM(infra_length) / 1000 FROM edges WHERE lts_access = 1 AND urban IS NOT NULL AND municipality IS NOT NULL;",
    connection,
)[0][0]
lts_2_length_urban = dbf.run_query_pg(
    "SELECT SUM(infra_length)  / 1000 FROM edges WHERE lts_access = 2 AND urban IS NOT NULL AND municipality IS NOT NULL;",
    connection,
)[0][0]
lts_3_length_urban = dbf.run_query_pg(
    "SELECT SUM(infra_length)  / 1000 FROM edges WHERE lts_access = 3 AND urban IS NOT NULL AND municipality IS NOT NULL;",
    connection,
)[0][0]
lts_4_length_urban = dbf.run_query_pg(
    "SELECT SUM(infra_length)  / 1000 FROM edges WHERE lts_access = 4 AND urban IS NOT NULL AND municipality IS NOT NULL;",
    connection,
)[0][0]

lts_1_length_rural = dbf.run_query_pg(
    "SELECT SUM(infra_length) / 1000 FROM edges WHERE lts_access = 1 AND urban IS NULL AND municipality IS NOT NULL;",
    connection,
)[0][0]
lts_2_length_rural = dbf.run_query_pg(
    "SELECT SUM(infra_length)  / 1000 FROM edges WHERE lts_access = 2 AND urban IS NULL AND municipality IS NOT NULL;",
    connection,
)[0][0]
lts_3_length_rural = dbf.run_query_pg(
    "SELECT SUM(infra_length)  / 1000 FROM edges WHERE lts_access = 3 AND urban IS NULL AND municipality IS NOT NULL;",
    connection,
)[0][0]
lts_4_length_rural = dbf.run_query_pg(
    "SELECT SUM(infra_length) / 1000 FROM edges WHERE lts_access = 4 AND urban IS NULL AND municipality IS NOT NULL;",
    connection,
)[0][0]

car_length_urban = dbf.run_query_pg(
    "SELECT SUM(infra_length) / 1000 FROM edges WHERE car_traffic = TRUE AND lts_access IN (1,2,3,4,7) AND urban IS NOT NULL AND municipality IS NOT NULL;",
    connection,
)[0][0]

car_length_rural = dbf.run_query_pg(
    "SELECT SUM(infra_length)  / 1000 FROM edges WHERE car_traffic = TRUE AND lts_access IN (1,2,3,4,7) AND urban IS NULL AND municipality IS NOT NULL;",
    connection,
)[0][0]

total_length = dbf.run_query_pg(
    "SELECT SUM(infra_length) / 1000 FROM edges WHERE lts_access IN (1,2,3,4,7) AND municipality IS NOT NULL;",
    connection,
)[0][0]

total_urban_length = dbf.run_query_pg(
    "SELECT SUM(infra_length) / 1000 FROM edges WHERE lts_access IN (1,2,3,4,7) AND urban IS NOT NULL AND municipality IS NOT NULL;",
    connection,
)[0][0]

total_rural_length = dbf.run_query_pg(
    "SELECT SUM(infra_length) / 1000 FROM edges WHERE lts_access IN (1,2,3,4,7) AND urban IS NULL AND municipality IS NOT NULL;",
    connection,
)[0][0]

assert round(total_length, 0) == round(total_urban_length + total_rural_length, 0)

total_urban_share = total_urban_length / total_length * 100
total_rural_share = total_rural_length / total_length * 100

lts_1_urban_share = lts_1_length_urban / total_length * 100
lts_2_urban_share = lts_2_length_urban / total_length * 100
lts_3_urban_share = lts_3_length_urban / total_length * 100
lts_4_urban_share = lts_4_length_urban / total_length * 100
lts_1_rural_share = lts_1_length_rural / total_length * 100
lts_2_rural_share = lts_2_length_rural / total_length * 100
lts_3_rural_share = lts_3_length_rural / total_length * 100
lts_4_rural_share = lts_4_length_rural / total_length * 100
car_urban_share = car_length_urban / total_length * 100
car_rural_share = car_length_rural / total_length * 100

# %%
urban_shares = [
    lts_1_urban_share,
    lts_2_urban_share,
    lts_3_urban_share,
    lts_4_urban_share,
    car_urban_share,
    total_urban_share,
]

rural_shares = [
    lts_1_rural_share,
    lts_2_rural_share,
    lts_3_rural_share,
    lts_4_rural_share,
    car_rural_share,
    total_rural_share,
]

bike_values = [
    lts_1_urban_share,
    lts_1_rural_share,
    lts_2_urban_share,
    lts_2_rural_share,
    lts_3_urban_share,
    lts_3_rural_share,
    lts_4_urban_share,
    lts_4_rural_share,
]
car_values = [car_urban_share, car_rural_share]

df_bike = pd.DataFrame(
    {"share": bike_values},
    index=[
        "LTS 1 urban",
        "LTS 1 rural",
        "LTS 2 urban",
        "LTS 2 rural",
        "LTS 3 urban",
        "LTS 3 rural",
        "LTS 4 urban",
        "LTS 4 rural",
    ],
)

df_car = pd.DataFrame({"share": car_values}, index=["Car urban", "Car rural"])

# %%

filepath = "../illustrations/lts_urban_rural"

fig, ax = plt.subplots(figsize=pdict["fsbar"])

colors = list(lts_color_dict.values())[0:4]
bike_colors = [i for i in colors for _ in range(2)]

colors = [lts_color_dict["car"]]
car_colors = [i for i in colors for _ in range(2)]

total_bike = df_bike.sum().values[0]
total_car = df_car.sum().values[0]

# Plot the data
df_bike.T.plot(
    kind="barh",
    stacked=True,
    ax=ax,
    color=bike_colors,
    # position=0,
    width=0.05,
)

df_car.T.plot(
    kind="barh", stacked=True, ax=ax, color=car_colors, position=2, width=0.05
)

bars = [
    thing for thing in ax.containers if isinstance(thing, mpl.container.BarContainer)
]

# Add value labels below each bar
total_width = 0
for container in ax.containers[0:-2]:
    for i, rect in enumerate(container):
        width = rect.get_width()  # Width of the current bar

        this_width = total_width + (width / 2)
        total_width += width
        ax.text(
            this_width,  # Center the text based on bar width
            rect.get_y() - 0.015,  # Place the text below the bar
            f"{width:.0f}%",  # Format the text
            ha="center",  # Horizontal alignment
            va="bottom",  # Vertical alignment to ensure it's below
            color="black",  # Adjust text color if needed
            fontsize=pdict["fontsize"],
        )

ax.text(
    total_width + 2.5,  # Center the text based on bar width
    rect.get_y() + 0.02,  # Place the text below the bar
    f"{total_bike:.0f}%",  # Format the text
    ha="center",  # Horizontal alignment
    va="bottom",  # Vertical alignment to ensure it's below
    color="black",  # Adjust text color if needed
    fontsize=pdict["fontsize"],
)

total_width = 0
for container in ax.containers[-2:]:
    for i, rect in enumerate(container):
        width = rect.get_width()  # Width of the current bar

        this_width = total_width + (width / 2)
        total_width += width

        ax.text(
            this_width,  # Center the text based on bar width
            rect.get_y() - 0.015,  # Place the text below the bar
            f"{width:.0f}%",  # Format the text
            ha="center",  # Horizontal alignment
            va="bottom",  # Vertical alignment to ensure it's below
            color="black",  # Adjust text color if needed
            fontsize=pdict["fontsize"],
        )

ax.text(
    total_width + 2.5,  # Center the text based on bar width
    rect.get_y() + 0.02,  # Place the text below the bar
    f"{total_car:.0f}%",  # Format the text
    ha="center",  # Horizontal alignment
    va="bottom",  # Vertical alignment to ensure it's below
    color="black",  # Adjust text color if needed
    fontsize=pdict["fontsize"],
)

hatch_bars = bars[1::2]

for bar in hatch_bars:
    for patch in bar:
        patch.set_hatch("//")

# Add legend
no_urban_patch = mpatches.Patch(
    facecolor="none",
    edgecolor="grey",
    linewidth=0.3,
    label="Non-urban",
    hatch="///",
)
lts1_patch = mpatches.Patch(
    facecolor=lts_color_dict["1"],
    edgecolor=lts_color_dict["1"],
    linewidth=0.3,
    label="LTS 1",
)
lts2_patch = mpatches.Patch(
    facecolor=lts_color_dict["2"],
    edgecolor=lts_color_dict["2"],
    linewidth=0.3,
    label="LTS 2",
)
lts3_patch = mpatches.Patch(
    facecolor=lts_color_dict["3"],
    edgecolor=lts_color_dict["3"],
    linewidth=0.3,
    label="LTS 3",
)
lts4_patch = mpatches.Patch(
    facecolor=lts_color_dict["4"],
    edgecolor=lts_color_dict["4"],
    linewidth=0.3,
    label="LTS 4",
)
car_patch = mpatches.Patch(
    facecolor=lts_color_dict["car"],
    edgecolor=lts_color_dict["car"],
    linewidth=0.3,
    label="Car",
)
ax.legend(
    handles=[lts1_patch, lts2_patch, lts3_patch, lts4_patch, car_patch, no_urban_patch],
    loc="upper right",
    frameon=False,
    fontsize=pdict["legend_fs"],
    ncol=6,
)

sns.despine(top=True, right=True, left=True, bottom=True)

ax.set(xticks=[], yticks=[])

plt.tight_layout()

plt.savefig(filepath + ".png", dpi=pdict["dpi"])

plt.show()

# %%
# MAKE SCS illustration

xmin, ymin, xmax, ymax = 680737 + 1500, 6176481, 729782 - 1000, 6220763 - 500

# TODO: Get background
background = gpd.read_postgis(
    "SELECT * FROM municipalities;", engine, geom_col="geometry"
)

bg_dis = background.dissolve()

scs = gpd.read_file("scs.gpkg")

scs.to_crs(crs="EPSG:25832", inplace=True)
scs_planned = scs.loc[scs["status"].isin(["Planlagt", "Projekteret"])]
scs_existing = scs.loc[scs["status"].isin(["Eksisterende"])]

# %%
# Get full network
low_stress_network = gpd.read_postgis(
    "SELECT id, geometry FROM edges WHERE lts_access IN (1,2)",
    engine,
    geom_col="geometry",
)

low_stress_subset = low_stress_network.cx[
    xmin - 100 : xmax + 100, ymin - 100 : ymax + 100
].copy()
# %%
plot_res = "low"

filepath = "../illustrations/scs_map"

fig, ax = plt.subplots(figsize=pdict["fsmap"])

bg_dis.plot(ax=ax, color="white", edgecolor="black", linewidth=0.2, legend=False)

low_stress_subset.plot(ax=ax, color="#117733", linewidth=0.2)
scs_existing.plot(ax=ax, color="#EE7733", linewidth=2, alpha=0.8)
scs_planned.plot(ax=ax, color="#6699CC", linewidth=2, alpha=0.8)

ax.axis([xmin, xmax, ymin, ymax])
ax.set_axis_off()
# ax.set_title("total network", fontsize=pdict["map_title_fs"])

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
    text="(C) " + pdict["map_attr"] + ", Supercykelstier",
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
