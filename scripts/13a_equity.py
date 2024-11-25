# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
from src import analysis_functions as analysis_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import display
from pysal.explore import inequality
from inequality.gini import Gini_Spatial
import seaborn as sns
from pysal.lib import weights

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/df_styler.py").read())

plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

# %%


# TODO: Compute concentration index (order by income or car ownership) (see karner et al 2024)


# TODO: Look into specific questions

# %%
# Prepare data

# Hex

hex_density = pd.read_sql("SELECT * FROM density.density_hex;", engine)
hex_density.fillna(0, inplace=True)

hex_density.drop(columns=["geometry"], inplace=True)

hex_pop = pd.read_sql("SELECT * FROM hex_grid;", engine)

hexgrid = hex_pop.merge(hex_density, on="hex_id", how="left")

assert len(hexgrid == len(hex_density))

hexgrid.fillna(0, inplace=True)


labels_hex = [
    "lts 1 density",
    "lts ≤2 density",
]
inequality_columns_hex = [
    "lts_1_dens",
    "lts_1_2_dens",
]

# SOCIO
exec(open("../helper_scripts/prepare_socio_cluster_data.py").read())

socio_pop = pd.read_sql("SELECT id, population, households FROM socio;", engine)

density_socio = pd.read_sql("SELECT * FROM density.density_socio;", engine)
density_socio.drop(columns=["geometry"], inplace=True)

socio_clusters = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM clustering.socio_socio_clusters;", engine, geom_col="geometry"
)

socio_density = socio.merge(density_socio, on="id", how="left")

socio_density = socio_density.merge(socio_pop, on="id", how="left")

assert len(socio_density[socio_density["total_network_length"].isna()]) == 0
assert len(socio_density[socio_density["population"].isna()]) == 0

socio_density["low_stress_per_person"] = (
    socio_density["lts_1_2_length"] / socio_density["population"]
)

socio_density["high_stress_per_person"] = (
    socio_density["lts_3_length"] + socio_density["lts_4_length"]
) / socio_density["population"]

socio_density["network_per_person"] = (
    socio_density["total_network_length"] / socio_density["population"]
)

# %%

labels_socio = [
    "low stress infrastructure per person",
    "high stress infrastructure per person",
    "road network",
    "lts 1 density",
    "lts ≤2 density",
]
inequality_columns_socio = [
    "low_stress_per_person",
    "high_stress_per_person",
    "network_per_person",
    "lts_1_dens",
    "lts_1_2_dens",
]

############## LORENZ CURVES ##############

for i, c in enumerate(inequality_columns_socio):

    cumulative_share = analysis_func.compute_cumulative_shares(socio_density[c])

    pop_shares, y_shares = plot_func.lorenz(cumulative_share)

    plot_func.plot_lorenz(
        cumulative_share=cumulative_share,
        share_of_population=pop_shares,
        x_label="population",
        y_label=labels_socio[i],
    )

# %%
############## GINI ##############

inequalities = (
    socio_density[inequality_columns_socio]
    .apply(analysis_func.gini_by_col, axis=0)
    .to_frame("gini")
)

########## THEIL ##########

inequalities["theil"] = socio_density[inequality_columns_socio].apply(
    analysis_func.compute_theil, axis=0
)

display(inequalities)

# %%
########## SPATIAL GINI ##########

# """
# Statistical significance indicates "that inequality between neighboring pairs of counties is different
# from the inequality between county pairs that are not geographically proximate."
# """

w = weights.contiguity.Queen.from_dataframe(
    socio_density,
    use_index=False,
)

# transform to binary
w.transform = "B"

spatial_gini_results = (
    socio_density[inequality_columns_socio]
    .apply(analysis_func.gini_spatial_by_column, weights=w)
    .T
)

display(spatial_gini_results)

# %%

# TODO: Compute spatial gini for lts density and bikeability at hex level


# %%
# TODO: WORK ON THEIL

# 1. Compute theil at hex level
# 2. Assign socio to hexes
# 3. Compute theil again, looking at within and between inequality

# Repeat for socio but using different groupings (e.g. rural vs urban, municipality, etc.)


# %%
## ************************** OLD CODE ************************** ##


# %%
####### BIVARIATE MORAN's I #######

from esda.moran import Moran_BV, Moran_Local_BV
from splot.esda import plot_local_autocorrelation, moran_scatterplot
from splot.esda import plot_moran_bv
from esda.moran import Moran_Local_BV
from esda.moran import Moran_Local
from esda.moran import Moran
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import geopandas as gpd


def compute_bivariate_moransi(x, y, w):

    # Compute bivariate Moran's I
    moran_bv = Moran_BV(y, x, w)
    lisas_bv = Moran_Local_BV(y, x, w)

    return moran_bv, lisas_bv


def compare_bivariate_moransi(all_morans):

    _, axs = plt.subplots(
        1, len(all_morans), figsize=(15, 10), subplot_kw={"aspect": "equal"}
    )

    axs = axs.flatten()

    for i, mo in enumerate(all_morans):

        moran_scatterplot(mo, p=0.05, ax=axs[i])
        plt.show()


def confirm_spatial_auto(x, y, gdf, w):

    # Confirm spatial autocorrelation of individual variables
    moran_x = Moran(x, w)
    moran_y = Moran(y, w)

    print(
        f"With a p_sim value of {moran_x.p_sim}, the Moran's I value for variable x is {moran_x.I}"
    )
    print(
        f"With a p_sim value of {moran_y.p_sim}, the Moran's I value for variable y is {moran_y.I}"
    )

    lisas_x = Moran_Local(x, w)
    lisas_y = Moran_Local(y, w)

    return lisas_x, lisas_y


# %%
w = analysis_func.spatial_weights_combined(
    socio_gdf, id_columns[1], k_socio, silence_warnings=True
)

x_col = "Household income 50th percentile"
y_col = "Low Stress Density"

x = socio_gdf[x_col].values
y = socio_gdf[y_col].values

lisas_x, lisas_y = confirm_spatial_auto(x, y, socio_gdf, w)

plot_local_autocorrelation(lisas_x, socio_gdf, x_col)
plt.show()

plot_local_autocorrelation(lisas_y, socio_gdf, y_col)
plt.show()

moran_bv, lisas_bv = compute_bivariate_moransi(x, y, w)

plot_moran_bv(moran_bv)
plt.show()

all_morans = [lisas_x, lisas_y, lisas_bv]

compare_bivariate_moransi(all_morans)


# Bivariate Moran Statistics describe the correlation between one variable
# and the spatial lag of another variable.
# Therefore, we have to be careful interpreting our results.
# Bivariate Moran Statistics do not take the inherent correlation
# between the two variables at the same location into account.
# They much more offer a tool to measure the degree one polygon with a
# specific attribute is correlated with its neighboring polygons
# with a different attribute.
# %%
### NEEDS GAP

# TODO: join hex pop to density, reach?
# Define threshold for density, reach, etc.

# write code for counting areas and people in areas with high and low values
# %%

# makes sense for density - zero sum game

# what about reach? not a zero sum game, but can still show the inequality - a bit like accessiblity
# %%
