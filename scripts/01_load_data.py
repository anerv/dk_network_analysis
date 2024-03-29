# %%

import yaml
import subprocess
import geopandas as gpd
from src import db_functions as dbf

with open(r"../config.yml") as file:
    parsed_yaml_file = yaml.load(file, Loader=yaml.FullLoader)

    db_name = parsed_yaml_file["db_name"]
    input_db_name = parsed_yaml_file["input_db_name"]
    db_user = parsed_yaml_file["db_user"]
    db_password = parsed_yaml_file["db_password"]
    db_host = parsed_yaml_file["db_host"]
    db_port = parsed_yaml_file["db_port"]
    network_edges = parsed_yaml_file["network_edges"]
    network_nodes = parsed_yaml_file["network_nodes"]

    adm_fp = parsed_yaml_file["adm_boundaries_fp"]
    socio_fp = parsed_yaml_file["socio_fp"]

    crs = parsed_yaml_file["CRS"]

print("Settings loaded!")

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)


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


# LOAD ADM DATA
adm = gpd.read_file(adm_fp)

assert adm.crs == crs

adm.columns = adm.columns.str.lower()

useful_cols = [
    "id.lokalid",
    # "dagiid",
    "navn",
    "kommunekode",
    "udenforkommuneinddeling",
    "geometry",
]

adm = adm[useful_cols]

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

# # CREATE INDICES
# dbf.run_query_pg("sql/create_indices.sql", connection)

connection.close()

print("Script 01 complete!")

# %%
