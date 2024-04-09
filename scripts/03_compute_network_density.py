# %%
import yaml
from src import db_functions as dbf
from src import h3_functions as h3f
import geopandas as gpd


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

    adm_fp = parsed_yaml_file["adm_boundaries_fp"]
    socio_fp = parsed_yaml_file["socio_fp"]

    crs = parsed_yaml_file["CRS"]

    h3_resolution = parsed_yaml_file["h3_resolution"]

print("Settings loaded!")


engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)


# %%
q = f"SELECT ST_Union(geometry) as geometry FROM adm_boundaries;"

study_area_poly = gpd.GeoDataFrame.from_postgis(
    q, engine, crs="EPSG:25832", geom_col="geometry"
)

h3_grid = h3f.create_h3_grid(study_area_poly, h3_resolution, crs, 500)

assert h3_grid.crs == crs

h3_grid.columns = h3_grid.columns.str.lower()

dbf.to_postgis(geodataframe=h3_grid, table_name="h3_grid", engine=engine)

print("H3 grid created and saved to database!")

q = "SELECT hex_id FROM h3_grid LIMIT 10;"

test = dbf.run_query_pg(q, connection)

print(test)

# %%
queries = [
    "sql/03a_compute_density_municipality.sql",
    "sql/03b_compute_density_socio.sql",
    "sql/03c_compute_density_h3.sql",
]

for i, q in enumerate(queries):
    print(f"Running step {i+1}...")
    result = dbf.run_query_pg(q, connection)
    if result == "error":
        print("Please fix error before rerunning and reconnect to the database")
        break

    print(f"Step {i+1} done!")

connection.close()

print("Script 03 complete!")

# %%
