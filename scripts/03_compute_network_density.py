# %%
import yaml
from src import db_functions as dbf
from src import h3_functions as h3f
import geopandas as gpd

exec(open("settings/yaml_variables.py").read())

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)


# %%
q = f"SELECT ST_Union(geometry) as geometry FROM adm_boundaries;"

study_area_poly = gpd.GeoDataFrame.from_postgis(
    q, engine, crs="EPSG:25832", geom_col="geometry"
)

h3_grid = h3f.create_h3_grid(study_area_poly, h3_resolution, crs, 500)

assert h3_grid.crs == crs

h3_grid.columns = h3_grid.columns.str.lower()

dbf.to_postgis(geodataframe=h3_grid, table_name="h3_grid", engine=engine)

print("H3 grid created and saved to database!")

q = "SELECT hex_id FROM h3_grid LIMIT 10;"

test = dbf.run_query_pg(q, connection)

print(test)

# %%
queries = [
    "sql/03a_compute_density_municipality.sql",
    "sql/03b_compute_density_socio.sql",
    "sql/03c_compute_density_h3.sql",
]

for i, q in enumerate(queries):
    print(f"Running step {i+1}...")
    result = dbf.run_query_pg(q, connection)
    if result == "error":
        print("Please fix error before rerunning and reconnect to the database")
        break

    print(f"Step {i+1} done!")

connection.close()

print("Script 03 complete!")

# %%

# TODO: Plot network density for muni, socio, h3 for each lts

# TODO: Plot distribution of network densities for each lts
