# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)


# %%
# Plot total component size distributions
component_size_all = pd.read_sql("SELECT * FROM component_size_all;", engine)
component_size_1 = pd.read_sql("SELECT * FROM component_size_1;", engine)
component_size_2 = pd.read_sql("SELECT * FROM component_size_2;", engine)
component_size_3 = pd.read_sql("SELECT * FROM component_size_3;", engine)
component_size_4 = pd.read_sql("SELECT * FROM component_size_4;", engine)
component_size_car = pd.read_sql("SELECT * FROM component_size_car;", engine)

component_size_dfs = [
    component_size_all,
    component_size_1,
    component_size_2,
    component_size_3,
    component_size_4,
    component_size_car,
]

labels = [
    "total network",
    "LTS 1 network",
    "LTS 2 network",
    "LTS 3 network",
    "LTS 4 network",
    "total car network",
]
columns = ["bike_length"] * 5 + ["geom_length"]

for i, df in enumerate(component_size_dfs):
    plot_func.make_zipf_component_plot(
        df,
        columns[i],
        labels[i],
        f"../results/component_size_distribution/{labels[i]}_zipf.png",
    )

# %%
plot_func.combined_zipf_plot(
    component_size_all=component_size_all,
    component_size_1=component_size_1,
    component_size_2=component_size_2,
    component_size_3=component_size_3,
    component_size_4=component_size_4,
    component_size_car=component_size_car,
    lts_color_dict=lts_color_dict,
    fp="../results/component_size_distribution/combined_zipf.png",
)

# %%
# Plot component size distribution per municipality

munis = dbf.run_query_pg("SELECT DISTINCT municipality from edges;", connection)

municipalities = [m[0] for m in munis]
municipalities.remove(None)

component_columns = [
    "component_all",
    "component_1",
    "component_1_2",
    "component_1_3",
    "component_1_4",
    "component_car",
]

success = []
for muni in municipalities:

    muni_edges = gpd.GeoDataFrame.from_postgis(
        f"SELECT * FROM component_edges WHERE municipality = '{muni}';",
        engine,
        crs=crs,
        geom_col="geometry",
    )

    muni_edges.loc[muni_edges.bike_length.isna(), "bike_length"] = (
        muni_edges.geometry.length
    )
    muni_edges["bike_length"] = muni_edges["bike_length"] / 1000
    muni_edges["geom_length"] = muni_edges.geometry.length / 1000

    if len(muni_edges) > 0:
        component_size_all = (
            muni_edges[muni_edges["component_all"].notna()]
            .groupby("component_all")
            .sum("bike_length")
        )
        component_size_1 = (
            muni_edges[muni_edges["component_1"].notna()]
            .groupby("component_1")
            .sum("bike_length")
        )
        component_size_2 = (
            muni_edges[muni_edges["component_1_2"].notna()]
            .groupby("component_1_2")
            .sum("bike_length")
        )
        component_size_3 = (
            muni_edges[muni_edges["component_1_3"].notna()]
            .groupby("component_1_3")
            .sum("bike_length")
        )
        component_size_4 = (
            muni_edges[muni_edges["component_1_4"].notna()]
            .groupby("component_1_4")
            .sum("bike_length")
        )
        component_size_car = (
            muni_edges[muni_edges["component_car"].notna()]
            .groupby("component_car")
            .sum("geom_length")
        )

        plot_func.combined_zipf_plot(
            component_size_all=component_size_all,
            component_size_1=component_size_1,
            component_size_2=component_size_2,
            component_size_3=component_size_3,
            component_size_4=component_size_4,
            component_size_car=component_size_car,
            lts_color_dict=lts_color_dict,
            fp=f"../results/component_size_distribution/administrative/combined_zipf_{muni}.png",
            title=f"Component size distribution in {muni}",
        )

        success.append(muni)

    elif len(muni_edges) == 0:
        print(f"No edges in {muni}")
        pass

# %%
# Plot local component count

muni_components = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM comp_count_muni;",
    engine,
    crs=crs,
    geom_col="geometry",
)

muni_components.replace(0, np.nan, inplace=True)

# %%
plot_cols = [
    "comp_1_count",
    "comp_2_count",
    "comp_3_count",
    "comp_4_count",
    "comp_car_count",
    "comp_all_count",
]
labels = ["LTS 1", "LTS 1-2", "LTS 1-3", "LTS 1-4", "Total car", "Total network"]
plot_titles = [f"Municipal component count for: {l}" for l in labels]
filepaths = [f"../results/component_count/administrative/{l}" for l in labels]

for i, p in enumerate(plot_cols):

    plot_func.plot_classified_poly(
        gdf=muni_components,
        plot_col=p,
        scheme="quantiles",
        cx_tile=cx_tile_2,
        plot_na=True,
        cmap=pdict["neg"],
        edgecolor="none",
        title=plot_titles[i],
        fp=filepaths[i],
    )


# %%
socio_components = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM comp_count_socio;",
    engine,
    crs=crs,
    geom_col="geometry",
)

socio_components.replace(0, np.nan, inplace=True)

plot_cols = [
    "comp_1_count",
    "comp_2_count",
    "comp_3_count",
    "comp_4_count",
    "comp_car_count",
    "comp_all_count",
]
labels = ["LTS 1", "LTS 1-2", "LTS 1-3", "LTS 1-4", "Total car", "Total network"]
plot_titles = [f"Local component count for: {l}" for l in labels]
filepaths = [f"../results/component_count/socio/{l}" for l in labels]

for i, p in enumerate(plot_cols):

    plot_func.plot_classified_poly(
        gdf=socio_components,
        plot_col=p,
        scheme="quantiles",
        cx_tile=cx_tile_2,
        plot_na=True,
        cmap=pdict["neg"],
        edgecolor="none",
        title=plot_titles[i],
        fp=filepaths[i],
    )


# %%

h3_components = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM comp_count_h3;",
    engine,
    crs=crs,
    geom_col="geometry",
)

h3_components.replace(0, np.nan, inplace=True)
# %%
plot_cols = [
    "comp_1_count",
    "comp_2_count",
    "comp_3_count",
    "comp_4_count",
    "comp_car_count",
    "comp_all_count",
]
labels = ["LTS 1", "LTS 1-2", "LTS 1-3", "LTS 1-4", "Total car", "Total network"]
plot_titles = [f"H3 component count for: {l}" for l in labels]
filepaths = [f"../results/component_count/socio/{l}" for l in labels]

for i, p in enumerate(plot_cols):

    plot_func.plot_classified_poly(
        gdf=h3_components,
        plot_col=p,
        scheme="quantiles",
        cx_tile=cx_tile_2,
        plot_na=True,
        cmap=pdict["neg"],
        edgecolor="none",
        linewidth=0.0,
        title=plot_titles[i],
        fp=filepaths[i],
    )

# %%
# TODO: Plot correlation between local component count and length
