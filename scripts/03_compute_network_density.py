# %%
from src import db_functions as dbf
from src import h3_functions as h3f
import geopandas as gpd
import numpy as np

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)


# %%
q = f"SELECT ST_Union(geometry) as geometry FROM adm_boundaries;"

study_area_poly = gpd.GeoDataFrame.from_postgis(
    q, engine, crs="EPSG:25832", geom_col="geometry"
)

hex_grid = h3f.create_hex_grid(study_area_poly, h3_resolution, crs, 500)

assert hex_grid.crs == crs

hex_grid.columns = hex_grid.columns.str.lower()

dbf.to_postgis(geodataframe=hex_grid, table_name="hex_grid", engine=engine)

print("H3 grid created and saved to database!")

q = "SELECT hex_id FROM hex_grid LIMIT 10;"

test = dbf.run_query_pg(q, connection)

print(test)

# %%
queries = [
    "sql/03a_compute_density_municipality.sql",
    "sql/03b_compute_density_socio.sql",
    "sql/03c_compute_density_hex.sql",
]

for i, q in enumerate(queries):
    print(f"Running step {i+1}...")
    result = dbf.run_query_pg(q, connection)
    if result == "error":
        print("Please fix error before rerunning and reconnect to the database")
        break

    print(f"Step {i+1} done!")

connection.close()

with open("vacuum_analyze.py") as f:
    exec(f.read())

print("Script 03 complete!")


# %%
