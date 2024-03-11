# %%
import geopandas as gpd
import pandas as pd
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
pop = pd.read_csv(
    "../data/input/socioeconomic/Befolkning.csv", sep=";", encoding="utf-8"
)

keep_cols = [
    "ValgstedId",
    # "KredsNr",
    # "StorKredsNr",
    # "LandsdelsNr",
    "FV2022 - Antal personer opgjort efter forsørgelsestype og afstemningsområde_Antal personer i alt",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_Antal husstande i alt",
    "FV2022 - Husstandes bilrådighed fordelt på afstemningsområder_Husstande med 1 bil",
    "FV2022 - Husstandes bilrådighed fordelt på afstemningsområder_Husstande med 2 eller flere biler",
    "FV2022 - Husstandes bilrådighed fordelt på afstemningsområder_Husstande uden bil",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_Under 100.000 kr.",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_100.000 - 149.999 kr",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_150.000 - 199.999 kr.",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_200.000 - 299.999 kr.",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_300.000 - 399.999 kr.",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_400.000 - 499.999 kr.",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_500.000 - 749.999 kr.",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_750.000 kr.-",
]

pop = pop[keep_cols]

geoms = gpd.read_file("../data/input/socioeconomic/voting_areas.gpkg")
geoms = geoms[["ValgstedId", "area_name", "municipal_id", "geometry"]]

areas = geoms.merge(pop, on="ValgstedId")

# %%
rename_dict = {
    "FV2022 - Antal personer opgjort efter forsørgelsestype og afstemningsområde_Antal personer i alt": "population",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_Antal husstande i alt": "households",
    "FV2022 - Husstandes bilrådighed fordelt på afstemningsområder_Husstande med 1 bil": "households_with_1_car",
    "FV2022 - Husstandes bilrådighed fordelt på afstemningsområder_Husstande med 2 eller flere biler": "households_with_2_cars",
    "FV2022 - Husstandes bilrådighed fordelt på afstemningsområder_Husstande uden bil": "households_without_car",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_Under 100.000 kr.": "households_income_under_100k",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_100.000 - 149.999 kr": "households_income_100k_150k",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_150.000 - 199.999 kr.": "households_income_150k_200k",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_200.000 - 299.999 kr.": "households_income_200k_300k",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_300.000 - 399.999 kr.": "households_income_300k_400k",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_400.000 - 499.999 kr.": "households_income_400k_500k",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_500.000 - 749.999 kr.": "households_income_500k_750k",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_750.000 kr.-": "households_income_750k_",
}


areas.rename(columns=rename_dict, inplace=True)

# %%
# replace - for no value with 0
areas.replace("-", 0, inplace=True)

# replace , with .
for col in areas.columns[4:]:
    areas[col] = areas[col].str.replace(",", ".").astype(float)

# %%
# compute population density
areas["population_density"] = areas.population / areas.geometry.area

# %%
# Export
areas.to_file("../data/processed/voting_areas.gpkg", driver="GPKG")
# %%

# %%
