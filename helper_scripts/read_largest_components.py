from src import db_functions as dbf
import geopandas as gpd

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/filepaths.py").read())

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

hex_largest_components = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM fragmentation.hex_largest_components;",
    engine,
    crs=crs,
    geom_col="geometry",
)

print("Loaded largest components per hexagon!")
