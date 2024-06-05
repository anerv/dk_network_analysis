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
id_columns = ["municipality", "id", "hex_id"]
k_values = [k_muni, k_socio, k_hex]
spatial_weights_values = [f"queen_{k}" for k in k_values]

spatial_weights = []

for i, gdf in enumerate(gdfs):

    w_queen = analysis_func.compute_spatial_weights(gdf, id_columns[i], w_type="queen")

    w_knn = analysis_func.compute_spatial_weights(
        gdf, id_columns[i], w_type="knn", k=k_values[i]
    )
    w = weights.set_operations.w_union(w_queen, w_knn)

    assert len(w.islands) == 0

    spatial_weights.append(w)

# %%
all_density_columns = [
    density_columns,
    density_steps_columns[1:-2],
    length_relative_columns,
    length_relative_steps_columns[1:-1],
]

aggregation_level = ["administrative", "socio", "hexgrid"]
id_columns = ["municipality", "id", "hex_id"]

for i, gdf in enumerate(gdfs):

    print(f"At aggregation level: {aggregation_level[i]}:")

    global_morans_results = {}

    for columns in all_density_columns:

        filepaths_morans = [
            f"../results/spatial_autocorrelation/density/{aggregation_level[i]}/morans_{c}.png".replace(
                " ", "_"
            )
            for c in columns
        ]

        filepaths_lisa = [
            f"../results/spatial_autocorrelation/density/{aggregation_level[i]}/lisa_{c}.png".replace(
                " ", "_"
            )
            for c in columns
        ]

        morans_results = analysis_func.compute_spatial_autocorrelation(
            columns, columns, gdf, spatial_weights[i], filepaths_morans, show_plot=False
        )

        lisa_results = analysis_func.compute_lisa(
            columns,
            columns,
            gdf,
            spatial_weights[i],
            filepaths_lisa,
            show_plot=False,
        )

        for key, value in morans_results.items():
            global_morans_results[key] = value.I

    with open(
        f"../results/spatial_autocorrelation/density/{aggregation_level[i]}/global_moransi_{spatial_weights_values[i]}.json",
        "w",
    ) as outfile:
        json.dump(global_morans_results, outfile)

    q_columns = [c for c in gdf.columns if c.endswith("_q")]
    q_columns.extend(["geometry", id_columns[i]])

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

gdfs = [muni_components, socio_components, hex_components]

# %%
# Define spatial weights

id_columns = ["municipality", "id", "hex_id"]
k_values = [k_muni, k_socio, k_hex]
spatial_weights_values = [f"queen_{k}" for k in k_values]

spatial_weights = []

for i, gdf in enumerate(gdfs):

    w_queen = analysis_func.compute_spatial_weights(gdf, id_columns[i], w_type="queen")

    w_knn = analysis_func.compute_spatial_weights(
        gdf, id_columns[i], w_type="knn", k=k_values[i]
    )
    w = weights.set_operations.w_union(w_queen, w_knn)

    assert len(w.islands) == 0

    spatial_weights.append(w)

# %%

all_fragmentation_columns = [
    component_count_columns,
    component_per_km_columns,
    component_per_km_sqkm_columns,
]

aggregation_level = ["administrative", "socio", "hexgrid"]
id_columns = ["municipality", "id", "hex_id"]

for i, gdf in enumerate(gdfs):

    print(f"At aggregation level: {aggregation_level[i]}:")

    global_morans_results = {}

    for columns in all_fragmentation_columns:

        filepaths_morans = [
            f"../results/spatial_autocorrelation/fragmentation/{aggregation_level[i]}/morans_{c}.png".replace(
                " ", "_"
            )
            for c in columns
        ]

        filepaths_lisa = [
            f"../results/spatial_autocorrelation/fragmentation/{aggregation_level[i]}/lisa_{c}.png".replace(
                " ", "_"
            )
            for c in columns
        ]

        morans_results = analysis_func.compute_spatial_autocorrelation(
            columns, columns, gdf, spatial_weights[i], filepaths_morans, show_plot=False
        )

        lisa_results = analysis_func.compute_lisa(
            columns,
            columns,
            gdf,
            spatial_weights[i],
            filepaths_lisa,
            show_plot=False,
        )

        for key, value in morans_results.items():
            global_morans_results[key] = value.I

    with open(
        f"../results/spatial_autocorrelation/fragmentation/{aggregation_level[i]}/global_moransi_{spatial_weights_values[i]}.json",
        "w",
    ) as outfile:
        json.dump(global_morans_results, outfile)

    q_columns = [c for c in gdf.columns if c.endswith("_q")]
    q_columns.extend(["geometry", id_columns[i]])

    gdf[q_columns].to_parquet(
        f"../results/spatial_autocorrelation/fragmentation/{aggregation_level[i]}/lisas.parquet"
    )

# %%
# *** Largest component size ****

hex_comp_size = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM fragmentation.hex_largest_components;",
    engine,
    crs=crs,
    geom_col="geometry",
)

hex_comp_size[largest_local_component_len_columns] = hex_comp_size[
    largest_local_component_len_columns
].replace(np.nan, 0)


gdfs = [hex_comp_size]

# Define spatial weights
id_columns = ["hex_id"]
k_values = [k_hex]
spatial_weights_values = [f"queen_{k}" for k in k_values]

spatial_weights = []

for i, gdf in enumerate(gdfs):

    w_queen = analysis_func.compute_spatial_weights(gdf, id_columns[i], w_type="queen")

    w_knn = analysis_func.compute_spatial_weights(
        gdf, id_columns[i], w_type="knn", k=k_values[i]
    )
    w = weights.set_operations.w_union(w_queen, w_knn)

    assert len(w.islands) == 0

    spatial_weights.append(w)

aggregation_level = ["hexgrid"]

all_comp_size_columns = [largest_local_component_len_columns]

for i, gdf in enumerate(gdfs):

    print(f"At aggregation level: {aggregation_level[i]}:")

    global_morans_results = {}

    for columns in all_comp_size_columns:

        filepaths_morans = [
            f"../results/spatial_autocorrelation/fragmentation/{aggregation_level[i]}/morans_{c}.png".replace(
                " ", "_"
            )
            for c in columns
        ]

        filepaths_lisa = [
            f"../results/spatial_autocorrelation/fragmentation/{aggregation_level[i]}/lisa_{c}.png".replace(
                " ", "_"
            )
            for c in columns
        ]

        morans_results = analysis_func.compute_spatial_autocorrelation(
            columns, columns, gdf, spatial_weights[i], filepaths_morans, show_plot=False
        )

        lisa_results = analysis_func.compute_lisa(
            columns,
            columns,
            gdf,
            spatial_weights[i],
            filepaths_lisa,
            show_plot=False,
        )

        for key, value in morans_results.items():
            global_morans_results[key] = value.I

    with open(
        f"../results/spatial_autocorrelation/fragmentation/{aggregation_level[i]}/global_moransi_largest_comp_size_{spatial_weights_values[i]}.json",
        "w",
    ) as outfile:
        json.dump(global_morans_results, outfile)

    q_columns = [c for c in gdf.columns if c.endswith("_q")]
    q_columns.extend(["geometry", id_columns[i]])

    gdf[q_columns].to_parquet(
        f"../results/spatial_autocorrelation/fragmentation/{aggregation_level[i]}/lisas_largest_comp_size_.parquet"
    )

# %%
### REACH #####

hex_reach = gpd.read_postgis(
    "SELECT * FROM reach.hex_reach", engine, geom_col="geometry"
)

hex_reach.replace(np.nan, 0, inplace=True)

gdfs = [hex_reach]

# Define spatial weights
id_columns = ["hex_id"]
k_values = [k_hex]
spatial_weights_values = [f"queen_{k}" for k in k_values]

spatial_weights = []

for i, gdf in enumerate(gdfs):

    w_queen = analysis_func.compute_spatial_weights(gdf, id_columns[i], w_type="queen")

    w_knn = analysis_func.compute_spatial_weights(
        gdf, id_columns[i], w_type="knn", k=k_values[i]
    )
    w = weights.set_operations.w_union(w_queen, w_knn)

    assert len(w.islands) == 0

    spatial_weights.append(w)

all_reach_columns = [reach_columns, reach_diff_columns, reach_diff_pct_columns]

aggregation_level = ["hexgrid"]

for i, gdf in enumerate(gdfs):

    print(f"At aggregation level: {aggregation_level[i]}:")

    global_morans_results = {}

    for columns in all_reach_columns:

        filepaths_morans = [
            f"../results/spatial_autocorrelation/reach/{aggregation_level[i]}/morans_{c}.png".replace(
                " ", "_"
            )
            for c in columns
        ]

        filepaths_lisa = [
            f"../results/spatial_autocorrelation/reach/{aggregation_level[i]}/lisa_{c}.png".replace(
                " ", "_"
            )
            for c in columns
        ]

        morans_results = analysis_func.compute_spatial_autocorrelation(
            columns, columns, gdf, spatial_weights[i], filepaths_morans, show_plot=False
        )

        lisa_results = analysis_func.compute_lisa(
            columns,
            columns,
            gdf,
            spatial_weights[i],
            filepaths_lisa,
            show_plot=False,
        )

        for key, value in morans_results.items():
            global_morans_results[key] = value.I

    with open(
        f"../results/spatial_autocorrelation/reach/{aggregation_level[i]}/global_moransi_{spatial_weights_values[i]}.json",
        "w",
    ) as outfile:
        json.dump(global_morans_results, outfile)

    q_columns = [c for c in gdf.columns if c.endswith("_q")]
    q_columns.extend(["geometry", id_columns[i]])

    gdf[q_columns].to_parquet(
        f"../results/spatial_autocorrelation/reach/{aggregation_level[i]}/lisas.parquet"
    )
# %%
## Confirm spatial clustering of population density and socio-economic variables

socio_gdf = gpd.read_postgis("SELECT * FROM socio;", engine, geom_col="geometry")

org_len = len(socio_gdf)

socio_gdf.dropna(subset=["population_density"], inplace=True)

print("Dropped rows with missing population density:", org_len - len(socio_gdf))

socio_gdf.replace(np.nan, 0, inplace=True)

w_queen = analysis_func.compute_spatial_weights(socio_gdf, "id", w_type="queen")

w_knn = analysis_func.compute_spatial_weights(socio_gdf, "id", w_type="knn", k=k_socio)
w = weights.set_operations.w_union(w_queen, w_knn)

assert len(w.islands) == 0


columns = [
    "population_density",
    "households_1car_share",
    "households_2cars_share",
    "households_nocar_share",
    "households_with_car_share",
    "households_income_under_100k_share",
    "households_income_100_150k_share",
    "households_income_150_200k_share",
    "households_income_200_300k_share",
    "households_income_200_300k_share",
    "households_income_300_400k_share",
    "households_income_400_500k_share",
    "households_income_500_750k_share",
]

global_morans_results = {}


filepaths_morans = [
    f"../results/spatial_autocorrelation/socio_pop/morans_{c}.png".replace(" ", "_")
    for c in columns
]

filepaths_lisa = [
    f"../results/spatial_autocorrelation/socio_pop/lisa_{c}.png".replace(" ", "_")
    for c in columns
]

morans_results = analysis_func.compute_spatial_autocorrelation(
    columns, columns, socio_gdf, w, filepaths_morans, show_plot=False
)

lisa_results = analysis_func.compute_lisa(
    columns,
    columns,
    socio_gdf,
    w,
    filepaths_lisa,
    show_plot=False,
)

for key, value in morans_results.items():
    global_morans_results[key] = value.I

with open(
    f"../results/spatial_autocorrelation/socio_pop/global_moransi_queens_{k_socio}.json",
    "w",
) as outfile:
    json.dump(global_morans_results, outfile)

q_columns = [c for c in socio_gdf.columns if c.endswith("_q")]
q_columns.extend(["geometry", "id"])

socio_gdf[q_columns].to_parquet(
    f"../results/spatial_autocorrelation/socio_pop/lisas.parquet"
)

# %%
