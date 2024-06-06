from src import db_functions as dbf
import pandas as pd

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/filepaths.py").read())

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)


component_length_muni = pd.read_sql(
    "SELECT * FROM fragmentation.component_length_muni;", engine
)
component_length_socio = pd.read_sql(
    "SELECT * FROM fragmentation.component_length_socio;", engine
)
component_length_hex = pd.read_sql(
    "SELECT * FROM fragmentation.component_length_hex;", engine
)

print("Component length per aggregation level loaded!")
