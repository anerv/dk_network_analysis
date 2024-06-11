from src import db_functions as dbf
import geopandas as gpd

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/filepaths.py").read())

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)


hex_reach_comparison = gpd.read_postgis(
    "SELECT * FROM reach.compare_reach;", engine, geom_col="geometry"
)
hex_reach_comparison.round(2, inplace=True)
hex_reach_comparison.replace(-0, 0, inplace=True)
hex_reach_comparison.replace(-0.00, 0, inplace=True)
