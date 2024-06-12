from src import db_functions as dbf
import pandas as pd
import geopandas as gpd

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/filepaths.py").read())

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

component_length_muni = gpd.read_postgis(
    "SELECT * FROM fragmentation.component_length_muni;", engine, geom_col="geometry"
)
component_length_socio = gpd.read_postgis(
    "SELECT * FROM fragmentation.component_length_socio;", engine, geom_col="geometry"
)
component_length_hex = gpd.read_postgis(
    "SELECT * FROM fragmentation.component_length_hex;", engine, geom_col="geometry"
)

print("Component length per aggregation level loaded!")
