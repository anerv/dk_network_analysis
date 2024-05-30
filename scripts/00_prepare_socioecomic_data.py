# %%
import geopandas as gpd
import pandas as pd
import numpy as np

exec(open("../settings/yaml_variables.py").read())

# %%
pop = pd.read_csv(
    "../data/input/socioeconomic/Befolkning.csv", sep=";", encoding="utf-8"
)

keep_cols = [
    "ValgstedId",
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
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_50%-percentil for husstandsindkomst",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_80%-percentil for husstandsindkomst",
]

pop = pop[keep_cols]

rename_dict = {
    "FV2022 - Antal personer opgjort efter forsørgelsestype og afstemningsområde_Antal personer i alt": "population",
    "FV2022 - Personer efter forsørgelsestype_12. Antal personer i alt": "population",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_Antal husstande i alt": "households",
    "FV2022 - Husstandes bilrådighed fordelt på afstemningsområder_Husstande med 1 bil": "households_with_1_car",
    "FV2022 - Husstandes bilrådighed fordelt på afstemningsområder_Husstande med 2 eller flere biler": "households_with_2_cars",
    "FV2022 - Husstandes bilrådighed fordelt på afstemningsområder_Husstande uden bil": "households_without_car",
    "FV2022 - Husstande efter bilrådighed_2. Husstande med 1 bil": "households_with_1_car",
    "FV2022 - Husstande efter bilrådighed_3. Husstande med 2 eller flere biler": "households_with_2_cars",
    "FV2022 - Husstande efter bilrådighed_1. Husstande uden bil": "households_without_car",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_Under 100.000 kr.": "households_income_under_100k",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_100.000 - 149.999 kr": "households_income_100k_150k",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_150.000 - 199.999 kr.": "households_income_150k_200k",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_200.000 - 299.999 kr.": "households_income_200k_300k",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_300.000 - 399.999 kr.": "households_income_300k_400k",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_400.000 - 499.999 kr.": "households_income_400k_500k",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_500.000 - 749.999 kr.": "households_income_500k_750k",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_750.000 kr.-": "households_income_750k_",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_50%-percentil for husstandsindkomst": "households_income_50_percentile",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_80%-percentil for husstandsindkomst": "households_income_80_percentile",
}

pop.rename(columns=rename_dict, inplace=True)

# replace - for no value with 0
pop.replace("-", np.nan, inplace=True)

# replace , with .
for col in pop.columns[1:]:
    pop[col] = pop[col].str.replace(",", ".").astype(float)

# %%
# Fill missing value
pop_2024 = pd.read_csv(
    "../data/input/socioeconomic/Befolkning_2024.csv", sep=";", encoding="utf-8"
)
pop_2024.ValgstedId = pop_2024.Gruppe.astype(int)

keep_cols24 = [
    "ValgstedId",
    "FV2022 - Personer efter forsørgelsestype_12. Antal personer i alt",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_Antal husstande i alt",
    "FV2022 - Husstande efter bilrådighed_2. Husstande med 1 bil",
    "FV2022 - Husstande efter bilrådighed_3. Husstande med 2 eller flere biler",
    "FV2022 - Husstande efter bilrådighed_1. Husstande uden bil",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_Under 100.000 kr.",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_100.000 - 149.999 kr",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_150.000 - 199.999 kr.",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_200.000 - 299.999 kr.",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_300.000 - 399.999 kr.",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_400.000 - 499.999 kr.",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_500.000 - 749.999 kr.",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_750.000 kr.-",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_50%-percentil for husstandsindkomst",
    "FV2022 - Husstandsindkomster fordelt på afstemningsområder_80%-percentil for husstandsindkomst",
]

pop_2024 = pop_2024[keep_cols24]

pop_2024.rename(columns=rename_dict, inplace=True)

# replace - for no value with 0
pop_2024.replace("-", np.nan, inplace=True)

# replace , with .
for col in pop_2024.columns[1:]:
    pop_2024[col] = pop_2024[col].str.replace(",", ".").astype(float)

missing_id = 813002

org_shape = pop.shape

pop.drop(pop[pop.ValgstedId == missing_id].index, inplace=True)

pop = pd.concat([pop, pop_2024[pop_2024.ValgstedId == missing_id]])

assert org_shape == pop.shape

# %%

geoms = gpd.read_file("../data/input/socioeconomic/voting_areas.gpkg")
geoms = geoms[["ValgstedId", "area_name", "municipal_id", "geometry"]]

areas = geoms.merge(pop, on="ValgstedId")

# compute population density
areas["population_density"] = areas.fillna(0).population.astype(int) / (
    areas.geometry.area / 10**6
)

areas["id"] = areas.ValgstedId
assert len(areas.ValgstedId.unique()) == len(areas)

# Export
areas.to_file("../data/processed/voting_areas.gpkg", driver="GPKG")
# %%
