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

    adm_fp = parsed_yaml_file["adm_boundaries_fp"]
    socio_fp = parsed_yaml_file["socio_fp"]
    urban_areas_fp = parsed_yaml_file["urban_areas_fp"]

    pop_fp_1 = parsed_yaml_file["pop_fp_1"]
    pop_fp_2 = parsed_yaml_file["pop_fp_2"]

    crs = parsed_yaml_file["CRS"]

    h3_resolution = parsed_yaml_file["h3_resolution"]

    k_muni = parsed_yaml_file["k_muni"]
    k_socio = parsed_yaml_file["k_socio"]
    k_hex = parsed_yaml_file["k_hex"]
    p_lisa = parsed_yaml_file["p_lisa"]

    reach_dist = parsed_yaml_file["reach_dist"]
