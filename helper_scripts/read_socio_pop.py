# %%

from src import db_functions as dbf
import geopandas as gpd

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

socio = gpd.read_postgis("SELECT * FROM socio", engine, geom_col="geometry")

socio["households_income_under_150k_share"] = (
    socio["households_income_under_100k_share"]
    + socio["households_income_100_150k_share"]
)

socio.rename(columns=population_rename_dict, inplace=True)

keep_columns = socio_corr_variables + ["id", "area_name", "geometry"]

socio = socio[keep_columns]
# %%
