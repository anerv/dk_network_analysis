# %%

import subprocess
import geopandas as gpd
from src import db_functions as dbf
from src import analysis_functions as analysis_func

exec(open("../settings/yaml_variables.py").read())

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

# %%
# LOAD INPUT NETWORK DATA
subprocess.run(
    f"pg_dump -t {network_edges} {input_db_name} | psql {db_name}",
    shell=True,
    check=True,
)

subprocess.run(
    f"pg_dump -t {network_nodes} {input_db_name} | psql {db_name}",
    shell=True,
    check=True,
)

q = f"DROP TABLE IF EXISTS edges CASCADE;"

dbf.run_query_pg(q, connection)

q = f"DROP TABLE IF EXISTS nodes CASCADE;"

dbf.run_query_pg(q, connection)

q = f"ALTER TABLE {network_edges} RENAME TO edges;"

dbf.run_query_pg(q, connection)

q = f"ALTER TABLE {network_nodes} RENAME TO nodes;"

dbf.run_query_pg(q, connection)

q_ix = "CREATE INDEX IF NOT EXISTS nodes_geom_ix ON nodes USING GIST (geometry);"

dbf.run_query_pg(q_ix, connection)

# %%
# LOAD URBAN AREAS DATA
urban = gpd.read_parquet(urban_areas_fp)

assert urban.crs == crs

dbf.to_postgis(geodataframe=urban, table_name="urban_areas", engine=engine)

# Preprocess urban data
q = "sql/01a_preprocess_urban.sql"
result = dbf.run_query_pg(q, connection)
if result == "error":
    print("Please fix error before rerunning and reconnect to the database")

# LOAD ADM DATA
adm = gpd.read_file(adm_fp)

assert adm.crs == crs

adm.columns = adm.columns.str.lower()

useful_columns = [
    "id.lokalid",
    # "dagiid",
    "navn",
    "kommunekode",
    "udenforkommuneinddeling",
    "geometry",
]

adm = adm[useful_columns]

dbf.to_postgis(geodataframe=adm, table_name="adm_boundaries", engine=engine)

q_ix = "CREATE INDEX IF NOT EXISTS adm_geom_ix ON adm_boundaries USING GIST (geometry);"

dbf.run_query_pg(q_ix, connection)

q = "SELECT navn, kommunekode FROM adm_boundaries LIMIT 10;"

test = dbf.run_query_pg(q, connection)

print(test)

# LOAD SOCIOECONOMIC DATA
socio = gpd.read_file(socio_fp)

assert socio.crs == crs

socio.columns = socio.columns.str.lower()

dbf.to_postgis(geodataframe=socio, table_name="socio", engine=engine)

q_ix = "CREATE INDEX IF NOT EXISTS socio_geom_ix ON socio USING GIST (geometry);"

dbf.run_query_pg(q_ix, connection)

q = "SELECT area_name, population FROM socio LIMIT 10;"

test = dbf.run_query_pg(q, connection)

print(test)

# Preprocess socio data
q = "sql/01b_preprocess_socio.sql"
result = dbf.run_query_pg(q, connection)
if result == "error":
    print("Please fix error before rerunning and reconnect to the database")


# CREATE HEX GRID
q = f"SELECT ST_Union(geometry) as geometry FROM adm_boundaries;"

study_area_poly = gpd.GeoDataFrame.from_postgis(
    q, engine, crs="EPSG:25832", geom_col="geometry"
)

hex_grid = analysis_func.create_hex_grid(study_area_poly, h3_resolution, crs, 500)

assert hex_grid.crs == crs

hex_grid.columns = hex_grid.columns.str.lower()

dbf.to_postgis(geodataframe=hex_grid, table_name="hex_grid", engine=engine)

print("H3 grid created and saved to database!")

q = "SELECT hex_id FROM hex_grid LIMIT 10;"

test = dbf.run_query_pg(q, connection)

print(test)

# %%
exec(open("../helper_scripts/vectorize_raster_population_data.py").read())

h3_gdf.rename(columns={f"hex_id_{h3_resolution}": "hex_id"}, inplace=True)

h3_gdf.to_postgis("h3_population", engine, if_exists="replace")

# %%

# Preprocess hex grid data
q = "sql/01c_preprocess_hexgrid.sql"
result = dbf.run_query_pg(q, connection)
if result == "error":
    print("Please fix error before rerunning and reconnect to the database")


connection.close()

print("Script 01b complete!")

# %%
