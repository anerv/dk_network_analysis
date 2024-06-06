# %%
from src import db_functions as dbf
import geopandas as gpd
import numpy as np

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

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
