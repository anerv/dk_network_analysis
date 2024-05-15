# %%

from src import db_functions as dbf

exec(open("../settings/yaml_variables.py").read())

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

queries = [
    "sql/02a_lts_cleanup.sql",
    "sql/02b_compute_initial_components.sql",
    "sql/02c_close_lts_gaps.sql",
    "sql/02d_compute_infrastructure_length.sql",
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

print("Script 02 complete!")
# %%
