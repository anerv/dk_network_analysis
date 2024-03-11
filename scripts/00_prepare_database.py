# %%

import yaml
import psycopg2
from src import db_functions as dbf

with open(r"../config.yml") as file:
    parsed_yaml_file = yaml.load(file, Loader=yaml.FullLoader)

    db_name = parsed_yaml_file["db_name"]
    db_user = parsed_yaml_file["db_user"]
    db_password = parsed_yaml_file["db_password"]
    db_host = parsed_yaml_file["db_host"]
    db_port = parsed_yaml_file["db_port"]


print("Settings loaded!")

connection = dbf.connect_pg("postgres", db_user, db_password, db_port, db_host=db_host)

connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
dbf.run_query_pg(f"CREATE DATABASE {db_name} ENCODING = 'UTF8';", connection)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port, db_host=db_host)

dbf.run_query_pg("sql/00_create_db.sql", connection)

connection.close()

print("Script 00 complete!")

# %%
