# %%

import yaml
import psycopg2
import subprocess
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

print("Settings loaded!")

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


connection = dbf.connect_pg("postgres", db_user, db_password, db_port, db_host=db_host)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port, db_host=db_host)

dbf.run_query_pg("sql/00_create_db.sql", connection)

# pg_dump -t table_to_copy source_db | psql target_db


# %%
connection.close()

print("Script 01 complete!")

# %%


connection = dbf.connect_pg("postgres", db_user, db_password, db_port, db_host=db_host)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port, db_host=db_host)

dbf.run_query_pg("sql/00_create_db.sql", connection)

# pg_dump -t table_to_copy source_db | psql target_db


# %%
connection.close()

print("Script 01 complete!")

# %%
subprocess.run(
    f"pg_dump -t {network_edges} {input_db_name} | psql {db_name}",
    shell=True,
    check=True,
)


connection = dbf.connect_pg("postgres", db_user, db_password, db_port, db_host=db_host)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port, db_host=db_host)

dbf.run_query_pg("sql/00_create_db.sql", connection)

# pg_dump -t table_to_copy source_db | psql target_db


# %%
connection.close()

print("Script 01 complete!")

# %%
subprocess.run(
    f"pg_dump -t {network_edges} {input_db_name} | psql {db_name}",
    shell=True,
    check=True,
)


connection = dbf.connect_pg("postgres", db_user, db_password, db_port, db_host=db_host)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port, db_host=db_host)

dbf.run_query_pg("sql/00_create_db.sql", connection)

# pg_dump -t table_to_copy source_db | psql target_db


# %%
connection.close()

print("Script 01 complete!")

# %%
subprocess.run(
    f"pg_dump -t {network_edges} {input_db_name} | psql {db_name}",
    shell=True,
    check=True,
)


connection = dbf.connect_pg("postgres", db_user, db_password, db_port, db_host=db_host)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port, db_host=db_host)

dbf.run_query_pg("sql/00_create_db.sql", connection)

# pg_dump -t table_to_copy source_db | psql target_db


# %%
connection.close()

print("Script 01 complete!")

# %%
