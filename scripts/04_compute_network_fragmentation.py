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
# Assign component to all edges based on different levels of LTS - including LTS gaps!
