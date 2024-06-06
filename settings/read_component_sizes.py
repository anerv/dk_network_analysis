from src import db_functions as dbf
import pandas as pd

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/filepaths.py").read())

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)


component_size_all = pd.read_sql(
    "SELECT * FROM fragmentation.component_size_all;", engine
)
component_size_1 = pd.read_sql("SELECT * FROM fragmentation.component_size_1;", engine)
component_size_2 = pd.read_sql("SELECT * FROM fragmentation.component_size_2;", engine)
component_size_3 = pd.read_sql("SELECT * FROM fragmentation.component_size_3;", engine)
component_size_4 = pd.read_sql("SELECT * FROM fragmentation.component_size_4;", engine)
component_size_car = pd.read_sql(
    "SELECT * FROM fragmentation.component_size_car;", engine
)
