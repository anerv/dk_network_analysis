from src import db_functions as dbf


exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/filepaths.py").read())

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

# generate socio reach comparison columns
exec(open("../helper_scripts/read_reach_comparison.py").read())
hex_reach_cols = [c for c in hex_reach_comparison.columns if "pct_diff" in c]
hex_reach_cols = [c for c in hex_reach_cols if any(r in c for r in reach_comparisons)]

socio_reach_compare_columns = [c + "_median" for c in hex_reach_cols]
del hex_reach_comparison
