from src import db_functions as dbf
import geopandas as gpd

exec(open("../settings/yaml_variables.py").read())

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

socio = gpd.read_postgis("SELECT * FROM socio", engine, geom_col="geometry")

rename_dict = {
    "households_income_under_100k_share": "Income under 100k",
    "households_income_100_150k_share": "Income 100-150k",
    "households_income_150_200k_share": "Income 150-200k",
    "households_income_200_300k_share": "Income 200-300k",
    "households_income_300_400k_share": "Income 300-400k",
    "households_income_400_500k_share": "Income 400-500k",
    "households_income_500_750k_share": "Income 500-750k",
    "households_income_750k_share": "Income 750k",
    "households_with_car_share": "Households w car",
    "households_1car_share": "Households 1 car",
    "households_2cars_share": "Households 2 cars",
    "households_nocar_share": "Households no car",
}

socio.rename(columns=rename_dict, inplace=True)

socio_corr_variables = [
    "Income under 100k",
    "Income 100-150k",
    "Income 150-200k",
    "Income 200-300k",
    "Income 300-400k",
    "Income 400-500k",
    "Income 500-750k",
    "Income 750k",
    "Households w car",
    "Households 1 car",
    "Households 2 cars",
    "Households no car",
    "population_density",
    "urban_pct",
]

keep_columns = socio_corr_variables + ["id"]

socio = socio[keep_columns]