# %%
import geopandas as gpd
import yaml
from src import db_functions as dbf

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

print("Settings loaded!")

# %%
engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)


municipalities = [
    # "Albertslund",
    # "Allerød",
    # "Ballerup",
    # "Brøndby",
    # "Dragør",
    # "Egedal",
    # "Fredensborg",
    "Frederiksberg",
    # "Frederikssund",
    # "Furesø",
    # "Gentofte",
    # "Gladsaxe",
    # "Glostrup",
    # "Greve",
    # "Gribskov",
    # "Halsnæs",
    # "Helsingør",
    # "Herlev",
    # "Hillerød",
    # "Hvidovre",
    # "Høje-Taastrup",
    # "Hørsholm",
    # "Ishøj",
    "København",
    # "Køge",
    # "Lyngby-Taarbæk",
    # "Roskilde",
    # "Rudersdal",
    # "Rødovre",
    # "Solrød",
    # "Tårnby",
    # "Vallensbæk",
]

queries = [
    "export_andreas.sql",
]

for i, q in enumerate(queries):
    print(f"Running step {i+1}...")
    result = dbf.run_query_pg(q, connection)
    if result == "error":
        print("Please fix error before rerunning and reconnect to the database")
        break

    print(f"Step {i+1} done!")


edges = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM andreas_export;", engine, geom_col="geometry"
)
nodes = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM andreas_export_nodes;", engine, geom_col="geometry"
)

print("Data retrieved!")

# %%
assert len(edges.municipality.unique()) == len(municipalities)

# %%
edges.to_file("../data/edges_udtraek.gpkg")

# %%
nodes.to_file("../data/nodes_udtraek.gpkg")

print("Data saved!")

connection.close()

# %%
