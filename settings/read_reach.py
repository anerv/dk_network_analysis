from src import db_functions as dbf
import geopandas as gpd
import numpy as np

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/filepaths.py").read())

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)


hex_reach = gpd.read_postgis(
    f"SELECT * FROM reach.hex_reach_{reach_dist}", engine, geom_col="geometry"
)
