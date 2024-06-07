# %%
from src import db_functions as dbf

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

queries = [
    "sql/04a_compute_components.sql",
    "sql/04b_compute_component_size.sql",
    "sql/04c_compute_local_component_count.sql",
    "sql/04d_component_length_comparison.sql",
    "sql/04e_compute_socio_largest_component.sql",
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

print("Script 04 complete!")

# %%
