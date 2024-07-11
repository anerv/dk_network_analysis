# %%
from src import db_functions as dbf
import geopandas as gpd
import pandas as pd
import numpy as np
import pandas as pd

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

# Read socio density
socio_density = gpd.read_postgis(
    "SELECT * FROM density.density_socio", engine, geom_col="geometry"
)

# socio_density = socio_density[socio_density.total_network_length > 0]

# Read socio comp count
socio_components = gpd.read_postgis(
    "SELECT * FROM fragmentation.component_length_socio;", engine, geom_col="geometry"
)

socio_components.drop(
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

# Read socio largest comp size
socio_largest_components = gpd.read_postgis(
    "SELECT * FROM fragmentation.socio_largest_component;", engine, geom_col="geometry"
)

# Read socio reach
socio_reach = gpd.read_postgis(
    f"SELECT * FROM reach.socio_reach_{reach_dist}", engine, geom_col="geometry"
)

socio_reach_comparison = gpd.read_postgis(
    "SELECT * FROM reach.socio_reach_comparison", engine, geom_col="geometry"
)

gdfs = [
    socio_density,
    socio_components,
    socio_largest_components,
    socio_reach,
    socio_reach_comparison,
]
for gdf in gdfs:
    gdf.drop(columns=["geometry"], inplace=True)


# %%
