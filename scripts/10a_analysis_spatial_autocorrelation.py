# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
from src import analysis_functions as analysis_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
from pysal.lib import weights

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)


# %%

### READ DATA ###
density_muni = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM density.density_municipality;",
    engine,
    crs=crs,
    geom_col="geometry",
)

density_muni.replace(np.nan, 0, inplace=True)

density_socio = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM density.density_socio;",
    engine,
    crs=crs,
    geom_col="geometry",
)

density_socio.replace(np.nan, 0, inplace=True)

density_hex = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM density.density_hex;",
    engine,
    crs=crs,
    geom_col="geometry",
)

density_hex.replace(np.nan, 0, inplace=True)

gdfs = [density_muni, density_socio, density_hex]

for gdf in gdfs:

    for p in length_relative_columns:
        gdf[p] = gdf[p] * 100

    for p in length_relative_steps_columns[1:-1]:
        gdf[p] = gdf[p] * 100

# %%

# Define spatial weights
w_muni_queen = analysis_func.compute_spatial_weights(
    density_muni, "municipality", w_type="queen"
)

w_socio_queen = analysis_func.compute_spatial_weights(
    density_socio, "id", w_type="queen"
)

w_grid_queen = analysis_func.compute_spatial_weights(
    density_hex, "hex_id", w_type="queen"
)

w_muni_knn = analysis_func.compute_spatial_weights(
    density_muni, "municipality", w_type="knn", k=k_muni
)

w_socio_knn = analysis_func.compute_spatial_weights(
    density_socio, "id", w_type="knn", k=k_socio
)

w_grid_knn = analysis_func.compute_spatial_weights(
    density_hex, "hex_id", w_type="knn", k=k_hex
)

w_muni = weights.set_operations.w_union(w_muni_queen, w_muni_knn)
w_socio = weights.set_operations.w_union(w_socio_queen, w_socio_knn)
w_grid = weights.set_operations.w_union(w_grid_queen, w_grid_knn)


spatial_weights = [w_muni, w_socio, w_grid]
k_values = [k_muni, k_socio, k_hex]
spatial_weights_values = [f"queen_{k_muni}", f"queen_{k_socio}", f"queen_{k_hex}"]

# %%
all_density_columns = [
    density_columns,
    density_steps_columns[1:-2],
    length_relative_columns,
    length_relative_steps_columns[1:-1],
]

aggregation_level = ["administrative", "socio", "hexgrid"]
id_cols = ["municipality", "id", "hex_id"]

for i, gdf in enumerate(gdfs):

    print(f"At aggregation level: {aggregation_level[i]}:")

    global_morans_results = {}

    for columns in all_density_columns:

        filepaths = [
            f"../results/spatial_autocorrelation/density/{aggregation_level[i]}/{c}.png".replace(
                " ", "_"
            )
            for c in columns
        ]

        morans_results = analysis_func.compute_spatial_autocorrelation(
            columns, columns, gdf, spatial_weights[i], filepaths, show_plot=False
        )

        lisa_results = analysis_func.compute_lisa(
            columns,
            columns,
            gdf,
            spatial_weights[i],
            filepaths,
            show_plot=False,
        )

        for key, value in morans_results.items():
            global_morans_results[key] = value.I

    with open(
        f"../results/spatial_autocorrelation/density/{aggregation_level[i]}/global_moransi_k{spatial_weights_values[i]}.json",
        "w",
    ) as outfile:
        json.dump(global_morans_results, outfile)

    q_columns = [c for c in gdf.columns if c.endswith("_q")]
    q_columns.extend(["geometry", id_cols[i]])

    gdf[q_columns].to_parquet(
        f"../results/spatial_autocorrelation/density/{aggregation_level[i]}/lisas.parquet"
    )

# %%
### FRAGMENTATION ###

# READ DATA

muni_components = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM fragmentation.component_length_muni;",
    engine,
    crs=crs,
    geom_col="geometry",
)

muni_components.replace(np.nan, 0, inplace=True)

socio_components = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM fragmentation.component_length_socio;",
    engine,
    crs=crs,
    geom_col="geometry",
)

socio_components.replace(np.nan, 0, inplace=True)

hex_components = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM fragmentation.component_length_hex;",
    engine,
    crs=crs,
    geom_col="geometry",
)

hex_components.replace(np.nan, 0, inplace=True)

# %%
# Define spatial weights
w_muni_queen = analysis_func.compute_spatial_weights(
    muni_components, "municipality", w_type="queen"
)

w_socio_queen = analysis_func.compute_spatial_weights(
    socio_components, "id", w_type="queen"
)

w_grid_queen = analysis_func.compute_spatial_weights(
    hex_components, "hex_id", w_type="queen"
)

w_muni_knn = analysis_func.compute_spatial_weights(
    muni_components, "municipality", w_type="knn", k=k_muni
)

w_socio_knn = analysis_func.compute_spatial_weights(
    socio_components, "id", w_type="knn", k=k_socio
)

w_grid_knn = analysis_func.compute_spatial_weights(
    hex_components, "hex_id", w_type="knn", k=k_hex
)

w_muni = weights.set_operations.w_union(w_muni_queen, w_muni_knn)
w_socio = weights.set_operations.w_union(w_socio_queen, w_socio_knn)
w_grid = weights.set_operations.w_union(w_grid_queen, w_grid_knn)

# %%
spatial_weights = [w_muni, w_socio, w_grid]
k_values = [k_muni, k_socio, k_hex]
spatial_weights_values = [f"queen_{k_muni}", f"queen_{k_socio}", f"queen_{k_hex}"]

gdfs = [muni_components, socio_components, hex_components]

all_fragmentation_columns = [
    component_count_columns,
    component_per_km_cols,
    component_per_km_sqkm_cols,
]

aggregation_level = ["administrative", "socio", "hexgrid"]
id_cols = ["municipality", "id", "hex_id"]

for i, gdf in enumerate(gdfs):

    print(f"At aggregation level: {aggregation_level[i]}:")

    global_morans_results = {}

    for columns in all_fragmentation_columns:

        filepaths = [
            f"../results/spatial_autocorrelation/fragmentation/{aggregation_level[i]}/{c}.png".replace(
                " ", "_"
            )
            for c in columns
        ]

        morans_results = analysis_func.compute_spatial_autocorrelation(
            columns, columns, gdf, spatial_weights[i], filepaths, show_plot=False
        )

        lisa_results = analysis_func.compute_lisa(
            columns,
            columns,
            gdf,
            spatial_weights[i],
            filepaths,
            show_plot=False,
        )

        for key, value in morans_results.items():
            global_morans_results[key] = value.I

    with open(
        f"../results/spatial_autocorrelation/fragmentation/{aggregation_level[i]}/global_moransi_k{spatial_weights_values[i]}.json",
        "w",
    ) as outfile:
        json.dump(global_morans_results, outfile)

    q_columns = [c for c in gdf.columns if c.endswith("_q")]
    q_columns.extend(["geometry", id_cols[i]])

    gdf[q_columns].to_parquet(
        f"../results/spatial_autocorrelation/fragmentation/{aggregation_level[i]}/lisas.parquet"
    )


# %%
### REACH #####

hex_reach = gpd.read_postgis(
    "SELECT * FROM reach.hex_reach", engine, geom_col="geometry"
)

for p in reach_columns:
    hex_reach[p] = hex_reach[p] / 1000  # Convert to km

for p in reach_diff_columns:
    hex_reach[p] = hex_reach[p] / 1000  # Convert to km

hex_reach.replace(np.nan, 0, inplace=True)

gdfs = [hex_reach]

w_grid_queen = analysis_func.compute_spatial_weights(
    hex_components, "hex_id", w_type="queen"
)
w_grid_knn = analysis_func.compute_spatial_weights(
    hex_components, "hex_id", w_type="knn", k=k_hex
)
w_grid = weights.set_operations.w_union(w_grid_queen, w_grid_knn)

spatial_weights = [w_grid]
spatial_weights_values = [k_hex]

all_reach_columns = [reach_columns, reach_diff_columns, reach_diff_pct_columns]

aggregation_level = ["hexgrid"]
id_cols = ["hex_id"]

for i, gdf in enumerate(gdfs):

    print(f"At aggregation level: {aggregation_level[i]}:")

    global_morans_results = {}

    for columns in all_reach_columns:

        filepaths = [
            f"../results/spatial_autocorrelation/reach/{aggregation_level[i]}/{c}.png".replace(
                " ", "_"
            )
            for c in columns
        ]

        morans_results = analysis_func.compute_spatial_autocorrelation(
            columns, columns, gdf, spatial_weights[i], filepaths, show_plot=False
        )

        lisa_results = analysis_func.compute_lisa(
            columns,
            columns,
            gdf,
            spatial_weights[i],
            filepaths,
            show_plot=False,
        )

        for key, value in morans_results.items():
            global_morans_results[key] = value.I

    with open(
        f"../results/spatial_autocorrelation/reach/{aggregation_level[i]}/global_moransi_k{spatial_weights_values[i]}.json",
        "w",
    ) as outfile:
        json.dump(global_morans_results, outfile)

    q_columns = [c for c in gdf.columns if c.endswith("_q")]
    q_columns.extend(["geometry", id_cols[i]])

    gdf[q_columns].to_parquet(
        f"../results/spatial_autocorrelation/reach/{aggregation_level[i]}/lisas.parquet"
    )
# %%
## Confirm spatial clustering of population density and socio-economic variables

# TODO: convert households columns to share


socio_gdf = gpd.read_postgis("SELECT * FROM socio;", engine, geom_col="geometry")


columns = ["population_density", "car_ownership", "income"]
