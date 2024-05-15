# %%
import yaml
from src import db_functions as dbf

with open(r"../config.yml") as file:
    parsed_yaml_file = yaml.load(file, Loader=yaml.FullLoader)

    db_name = parsed_yaml_file["db_name"]
    db_user = parsed_yaml_file["db_user"]
    db_password = parsed_yaml_file["db_password"]
    db_host = parsed_yaml_file["db_host"]
    db_port = parsed_yaml_file["db_port"]

connection = dbf.connect_pg(db_name, db_user, db_password, db_port, db_host=db_host)

connection.set_isolation_level(0)

dbf.run_query_pg("VACUUM ANALYZE", connection)

connection.close()

# %%
