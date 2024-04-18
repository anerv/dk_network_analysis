# %%

import yaml
import psycopg2
from src import db_functions as dbf

exec(open("settings/yaml_variables.py").read())

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
dbf.run_query_pg(f"CREATE DATABASE {db_name} ENCODING = 'UTF8';", connection)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port, db_host=db_host)

dbf.run_query_pg("sql/00_create_db.sql", connection)

connection.close()

print("Script 00 complete!")

# %%
