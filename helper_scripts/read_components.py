from src import db_functions as dbf
import geopandas as gpd
import numpy as np

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/filepaths.py").read())

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

muni_components = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM fragmentation.component_count_muni;",
    engine,
    crs=crs,
    geom_col="geometry",
)

muni_components.replace(0, np.nan, inplace=True)

socio_components = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM fragmentation.component_count_socio;",
    engine,
    crs=crs,
    geom_col="geometry",
)

socio_components.replace(0, np.nan, inplace=True)

hex_components = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM fragmentation.component_count_hex;",
    engine,
    crs=crs,
    geom_col="geometry",
)

hex_components.replace(0, np.nan, inplace=True)


print("Component data loaded!")
