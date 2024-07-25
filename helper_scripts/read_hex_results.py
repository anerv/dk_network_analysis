# %%
from src import db_functions as dbf
import geopandas as gpd
import pandas as pd
import numpy as np
import pandas as pd

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

#### HEX #####
hex_geoms = gpd.read_postgis(
    "SELECT hex_id, urban_pct, population_density, geometry FROM hex_grid;",
    engine,
    geom_col="geometry",
)

hex_density = gpd.read_postgis(
    "SELECT * FROM density.density_hex;", engine, geom_col="geometry"
)

hex_components = gpd.read_postgis(
    "SELECT * FROM fragmentation.component_length_hex;", engine, geom_col="geometry"
)

hex_components.drop(
    columns=[
        "lts_1_length",
        "lts_2_length",
        "lts_3_length",
        "lts_4_length",
        "lts_1_2_length",
        "lts_1_3_length",
        "lts_1_4_length",
        "total_car_length",
        "total_network_length",
        "lts_1_dens",
        "lts_1_2_dens",
        "lts_1_3_dens",
        "lts_1_4_dens",
        "total_car_dens",
        "total_network_dens",
    ],
    inplace=True,
)

hex_largest_components = gpd.read_postgis(
    "SELECT * FROM fragmentation.hex_largest_components;", engine, geom_col="geometry"
)

hex_reach = gpd.read_postgis(
    f"SELECT * FROM reach.hex_reach_{reach_dist};", engine, geom_col="geometry"
)

exec(open("../helper_scripts/read_reach_comparison.py").read())

gdfs = [
    hex_density,
    hex_components,
    hex_largest_components,
    hex_reach,
    hex_reach_comparison,
]
for gdf in gdfs:
    gdf.drop(columns=["geometry"], inplace=True)

hex_gdf = hex_geoms.merge(hex_density, on="hex_id", how="left")
hex_gdf = hex_gdf.merge(hex_components, on="hex_id", how="left")
hex_gdf = hex_gdf.merge(hex_reach, on="hex_id", how="left")
hex_gdf = hex_gdf.merge(hex_reach_comparison, on="hex_id", how="left")
hex_gdf = hex_gdf.merge(hex_largest_components, on="hex_id", how="left")

assert hex_gdf.shape[0] == hex_density.shape[0]

duplicates = [c for c in hex_gdf.columns if c.endswith("_x") or c.endswith("_y")]
assert len(duplicates) == 0

del (
    hex_geoms,
    hex_density,
    hex_components,
    hex_largest_components,
    hex_reach,
    hex_reach_comparison,
)
# %%
