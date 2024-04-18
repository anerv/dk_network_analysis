# %%
from src import db_functions as dbf
from src import plotting_functions as plot_funcs
import geopandas as gpd
import pandas as pd
import math
import matplotlib.pyplot as plt

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
plot_funcs.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

# %%
queries = [
    "sql/04a_compute_components.sql",
    "sql/04b_compute_component_size.sql",
    "sql/04c_compute_local_component_count.sql",
]

for i, q in enumerate(queries):
    print(f"Running step {i+1}...")
    result = dbf.run_query_pg(q, connection)
    if result == "error":
        print("Please fix error before rerunning and reconnect to the database")
        break

    print(f"Step {i+1} done!")


# %%
def make_zipf_component_plot(df, col, label, fp=None):

    fig = plt.figure(figsize=(10, 6))
    axes = fig.add_axes([0, 0, 1, 1])

    axes.set_axisbelow(True)
    axes.grid(True, which="major", ls="dotted")
    yvals = sorted(list(df[col] / 1000), reverse=True)
    axes.scatter(
        x=[i + 1 for i in range(len(df))],
        y=yvals,
        s=18,
        color="purple",
    )
    axes.set_ylim(
        ymin=10 ** math.floor(math.log10(min(yvals))),
        ymax=10 ** math.ceil(math.log10(max(yvals))),
    )
    axes.set_xscale("log")
    axes.set_yscale("log")

    axes.set_ylabel("Component length [km]")
    axes.set_xlabel("Component rank (largest to smallest)")
    axes.set_title(f"Component length distribution in {label}")

    if fp:
        plt.savefig(fp, bbox_inches="tight")


# %%
# Plot total component size distributions

component_size_all = pd.read_sql("SELECT * FROM component_size_all;", engine)
component_size_1 = pd.read_sql("SELECT * FROM component_size_1;", engine)
component_size_2 = pd.read_sql("SELECT * FROM component_size_2;", engine)
component_size_3 = pd.read_sql("SELECT * FROM component_size_3;", engine)
component_size_4 = pd.read_sql("SELECT * FROM component_size_4;", engine)

component_size_dfs = []

for df in component_size_dfs:
    make_zipf_component_plot(df, "bike_length", "all", f"../results/{df}_zipf.png")

# %%
# Plot component size distribution per municipality

municipalities = dbf.run_query_pg(
    "SELECT DISTINCT municipality from edges;", connection
)

component_columns = [
    "component_all",
    "component_1",
    "component_1_2",
    "component_1_3",
    "component_1_4",
    "component_car",
]

for muni in municipalities:

    muni_edges = gpd.GeoDataFrame.from_postgis(
        f"SELECT * FROM component_edges WHERE municipality = '{muni}';",
        engine,
        crs=crs,
        geom_col="geometry",
    )

    for c in component_columns:
        component_edges = muni_edges[muni_edges[c] == "True"]
        grouped_edges = component_edges.groupby("c").sum("bike_length")

        grouped_edges.to_csv(f"../results/municipalities/{muni}_{c}.csv")

        make_zipf_component_plot(grouped_edges, c)
# %%

# %%
# Compute local component count

queries = [
    "sql/04d_component_length_comparison.sql",
]

for i, q in enumerate(queries):
    print(f"Running step {i+1}...")
    result = dbf.run_query_pg(q, connection)
    if result == "error":
        print("Please fix error before rerunning and reconnect to the database")
        break

    print(f"Step {i+1} done!")

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

# %%

# Plot correlation between local component count and length


# %%

connection.close()
print("Script 04 complete!")
