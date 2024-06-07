# %%
from src import plotting_functions as plot_func
from src import analysis_functions as analysis_func
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from src import db_functions as dbf

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

# %%
# Settings

# K-values to test
hex_ks = [6, 18, 36]  # 60
muni_ks = [3, 5, 7]
socio_ks = [4, 8, 12]

all_ks = [muni_ks, socio_ks, hex_ks]

id_columns = ["municipality", "id", "hex_id"]

fp = fp_spatial_weights_sensitivity
# %%
####### DENSITY ############
############################

### READ DATA ###
exec(open("../settings/read_density.py").read())

gdfs = [density_muni, density_socio, density_hex]

for gdf in gdfs:

    for p in length_relative_columns:
        gdf[p] = gdf[p] * 100

    for p in length_relative_steps_columns[1:-1]:
        gdf[p] = gdf[p] * 100

all_columns = [
    length_columns,
    length_relative_steps_columns,
]

for i, gdf in enumerate(gdfs):

    analysis_func.compare_spatial_weights_sensitivity(
        gdf=gdf,
        id_column=id_columns[i],
        aggregation_level=aggregation_levels[i],
        k_values=all_ks[i],
        all_columns=all_columns,
        fp=fp,
    )

# %%
####### FRAGMENTATION ######
############################

exec(open("../settings/read_components.py").read())

gdfs = [muni_components, socio_components, hex_components]


all_columns = [
    component_count_columns,
    component_per_km_columns,
]

for i, gdf in enumerate(gdfs):

    compare_spatial_weights_sensitivity(
        gdf=gdf,
        id_column=id_columns[i],
        aggregation_level=aggregation_levels[i],
        k_values=all_ks[i],
        all_columns=all_columns,
        fp=fp,
    )

# %%

####### REACH ##############
############################

exec(open("../settings/read_reach.py").read())

hex_reach.replace(np.nan, 0, inplace=True)

# K-values to test
hex_ks = [6, 18, 36]  # 60

all_columns = [reach_columns]

analysis_func.compare_spatial_weights_sensitivity(
    gdf=hex_reach,
    id_column="hex_id",
    aggregation_level=aggregation_levels[-1],
    k_values=hex_ks,
    all_columns=all_columns,
    fp=fp,
)

# %%
