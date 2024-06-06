from src import db_functions as dbf
import pandas as pd
import numpy as np

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/filepaths.py").read())

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)


hex_largest_components = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM fragmentation.hex_largest_components;",
    engine,
    crs=crs,
    geom_col="geometry",
)

hex_largest_components[largest_local_component_len_columns] = hex_largest_components[
    largest_local_component_len_columns
].replace(np.nan, 0)

hex_largest_components[largest_local_component_area_columns] = hex_largest_components[
    largest_local_component_area_columns
].replace(np.nan, 0)


print("Loaded largest components per hexagon!")
