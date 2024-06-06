# %%
from src import plotting_functions as plot_func
from src import analysis_functions as analysis_func
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from src import db_functions as dbf

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

# %%
# Settings

# K-values to test
hex_ks = [6, 18, 36]  # 60
muni_ks = [3, 5, 7]
socio_ks = [4, 8, 12]

all_ks = [muni_ks, socio_ks, hex_ks]

id_columns = ["municipality", "id", "hex_id"]

aggregation_levels = ["administrative", "socio", "hexgrid"]

fp = "../results/spatial_autocorrelation/sensitivity_test/"
# %%
####### DENSITY ############
############################

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

all_columns = [
    length_columns,
    length_relative_steps_columns,
]

for i, gdf in enumerate(gdfs):

    analysis_func.compare_spatial_weights_sensitivity(
        gdf=gdf,
        id_column=id_columns[i],
        aggregation_level=aggregation_levels[i],
        k_values=all_ks[i],
        all_columns=all_columns,
        fp=fp,
    )

# %%
####### FRAGMENTATION ######
############################

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


all_columns = [
    component_count_columns,
    component_per_km_columns,
]

for i, gdf in enumerate(gdfs):

    compare_spatial_weights_sensitivity(
        gdf=gdf,
        id_column=id_columns[i],
        aggregation_level=aggregation_levels[i],
        k_values=all_ks[i],
        all_columns=all_columns,
        fp=fp,
    )

# %%

####### REACH ##############
############################

hex_reach = gpd.read_postgis(
    f"SELECT * FROM reach.hex_reach_{reach_dist}", engine, geom_col="geometry"
)

hex_reach.replace(np.nan, 0, inplace=True)

# K-values to test
hex_ks = [6, 18, 36]  # 60

aggregation_levels = ["hexgrid"]

all_columns = [reach_columns]

analysis_func.compare_spatial_weights_sensitivity(
    gdf=hex_reach,
    id_column="hex_id",
    aggregation_level="hex_grid",
    k_values=hex_ks,
    all_columns=all_columns,
    fp=fp,
)

# %%
