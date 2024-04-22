# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
import geopandas as gpd
import pandas as pd
import math
import matplotlib.pyplot as plt

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

for muni in municipalities:

    print(muni)

    muni_edges = gpd.GeoDataFrame.from_postgis(
        f"SELECT * FROM component_edges WHERE municipality = '{muni}';",
        engine,
        crs=crs,
        geom_col="geometry",
    )

    muni_edges["bike_length"] = muni_edges["bike_length"] / 1000
    muni_edges["geom_length"] = muni_edges.geometry.length / 1000

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
        fp=f"../results/component_size_distribution/combined_zipf_{muni}.png",
        title=f"Component size distribution in {muni}",
    )

    # for c in component_columns:
    #     component_edges = muni_edges[muni_edges[c].notna()]
    #     grouped_edges = component_edges.groupby(c).sum("bike_length")

    #     grouped_edges.reset_index(inplace=True)
    #     # grouped_edges.to_csv(f"../results/component_size_distribution/{muni}_{c}.csv")
    #     if len(grouped_edges) > 0:

    #         make_zipf_component_plot(
    #             grouped_edges,
    #             c,
    #             muni,
    #             f"../results/component_size_distribution/{muni}_{l}_zipf.png",
    #             show=False,
    #         )

# %%
# Plot local component count

muni_components = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM comp_count_muni;",
    engine,
    crs=crs,
    geom_col="geometry",
)


socio_components = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM comp_count_socio;",
    engine,
    crs=crs,
    geom_col="geometry",
)


h3_components = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM comp_count_h3;",
    engine,
    crs=crs,
    geom_col="geometry",
)

# %%
# Plot correlation between local component count and length
