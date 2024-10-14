# %%
import geopandas as gpd
import pandas as pd
import numpy as np

exec(open("../settings/yaml_variables.py").read())

pop = pd.read_csv(
    "../data/input/socioeconomic/Befolkning.csv", sep=";", encoding="utf-8"
)
# replace - for no value with 0
pop.replace("-", np.nan, inplace=True)

# replace , with .
for col in pop.columns[5:]:
    pop[col] = pop[col].str.replace(",", ".").astype(float)
# %%
# Create age groups
age_groups = [
    "18-19",
    "20-24",
    "25-29",
    "30-34",
    "35-39",
    "40-44",
    "45-49",
    "50-54",
    "55-59",
    "60-64",
    "65-69",
    "70-",
]
for age in age_groups:
    age_cols = [col for col in pop.columns if age in col]
    pop[age] = pop[age_cols].sum(axis=1)
    pop.drop(age_cols, axis=1, inplace=True)
# %%
pop["adults"] = pop[age_groups].sum(axis=1)

pop["-17"] = (
    pop["EV2024 - Personer efter forsørgelsestype_12. Antal personer i alt"]
    - pop.adults
)
pop["18-29"] = pop[["18-19", "20-24", "25-29"]].sum(axis=1)
pop["30-39"] = pop[["30-34", "35-39"]].sum(axis=1)
pop["40-49"] = pop[["40-44", "45-49"]].sum(axis=1)
pop["50-59"] = pop[["50-54", "55-59"]].sum(axis=1)
pop["60-69"] = pop[["60-64", "65-69"]].sum(axis=1)
pop["70-"] = pop["70-"]

# %%
rename_dict = {
    "EV2024 - Husstande efter bilrådighed_2. Husstande med 1 bil": "households_with_1_car",
    "EV2024 - Husstande efter bilrådighed_3. Husstande med 2 eller flere biler": "households_with_2_cars",
    "EV2024 - Husstande efter bilrådighed_1. Husstande uden bil": "households_without_car",
    "EV2024 - Husstandsindkomster fordelt på afstemningsområder_Under 100.000 kr.": "households_income_under_100k",
    "EV2024 - Husstandsindkomster fordelt på afstemningsområder_100.000 - 149.999 kr": "households_income_100k_150k",
    "EV2024 - Husstandsindkomster fordelt på afstemningsområder_150.000 - 199.999 kr.": "households_income_150k_200k",
    "EV2024 - Husstandsindkomster fordelt på afstemningsområder_200.000 - 299.999 kr.": "households_income_200k_300k",
    "EV2024 - Husstandsindkomster fordelt på afstemningsområder_300.000 - 399.999 kr.": "households_income_300k_400k",
    "EV2024 - Husstandsindkomster fordelt på afstemningsområder_400.000 - 499.999 kr.": "households_income_400k_500k",
    "EV2024 - Husstandsindkomster fordelt på afstemningsområder_500.000 - 749.999 kr.": "households_income_500k_750k",
    "EV2024 - Husstandsindkomster fordelt på afstemningsområder_750.000 kr.-": "households_income_750k_",
    "EV2024 - Husstandsindkomster fordelt på afstemningsområder_50%-percentil for husstandsindkomst": "households_income_50_percentile",
    "EV2024 - Husstandsindkomster fordelt på afstemningsområder_80%-percentil for husstandsindkomst": "households_income_80_percentile",
    "EV2024 - Husstandsindkomster fordelt på afstemningsområder_Antal husstande i alt": "households",
    "EV2024 - Personer efter forsørgelsestype_12. Antal personer i alt": "population",
    "EV2024 - Socio-økonomisk status og brancher fordelt på afstemningsområder_08. Uddannelsessøgende_12. Uoplyst aktivitet": "students",
}

pop.rename(columns=rename_dict, inplace=True)

# %%
pop["-17_share"] = pop["-17"] / pop.population * 100
pop["18-29_share"] = pop["18-29"] / pop.population * 100
pop["30-39_share"] = pop["30-39"] / pop.population * 100
pop["40-49_share"] = pop["40-49"] / pop.population * 100
pop["50-59_share"] = pop["50-59"] / pop.population * 100
pop["60-69_share"] = pop["60-69"] / pop.population * 100
pop["70-_share"] = pop["70-"] / pop.population * 100

pop["total_share"] = pop[
    [
        "-17_share",
        "18-29_share",
        "30-39_share",
        "40-49_share",
        "50-59_share",
        "60-69_share",
        "70-_share",
    ]
].sum(axis=1)

assert round(pop["total_share"].max(), 0) == 100
pop.drop("total_share", axis=1, inplace=True)

pop["student_share"] = pop.students / pop.population * 100
assert pop.student_share.max() <= 100
pop["student_share"] = pop.student_share.fillna(0)

# %%
keep_columns = [
    "ValgstedId",
    "-17_share",
    "18-29_share",
    "30-39_share",
    "40-49_share",
    "50-59_share",
    "60-69_share",
    "70-_share",
    "student_share",
]

keep_columns.extend(list(rename_dict.values()))

pop = pop[keep_columns]

pop.drop("students", axis=1, inplace=True)
# %%
geoms = gpd.read_file("../data/input/socioeconomic/afstemningsomraade.gpkg")

geoms["ValgstedId"] = (
    geoms["kommunekode"].astype(str).str[1:]
    + "0"
    + geoms.afstemningsomraadenummer.astype(str)
)

geoms["ValgstedId"] = geoms["ValgstedId"].astype(int)

geoms.rename(columns={"navn": "area_name", "kommunekode": "municipal_id"}, inplace=True)

geoms = geoms[["ValgstedId", "area_name", "municipal_id", "geometry"]]

geoms = geoms.merge(pop, on="ValgstedId", how="outer")

geoms.dropna(subset=["population"], inplace=True)

assert len(geoms) == 1284
# %%
# compute population density
geoms["population_density"] = geoms.fillna(0).population.astype(int) / (
    geoms.geometry.area / 10**6
)

geoms["id"] = geoms.ValgstedId
assert len(geoms.ValgstedId.unique()) == len(geoms)

# Export
geoms.to_file("../data/processed/voting_areas.gpkg", driver="GPKG")

print("Script 00 complete!")
# %%
