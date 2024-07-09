# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
from src import analysis_functions as analysis_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import contextily as cx
from matplotlib.patches import Patch
from IPython.display import display
import plotly_express as px
from pysal.explore import inequality
from inequality.gini import Gini_Spatial

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/df_styler.py").read())

plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

# %%
# Prepare data

exec(open("../settings/prepare_socio_cluster_data.py").read())

# generate socio reach comparison columns
exec(open("../settings/read_reach_comparison.py").read())
hex_reach_component_cols = [c for c in hex_reach_comparison.columns if "pct_diff" in c]
hex_reach_component_cols = [
    c
    for c in hex_reach_component_cols
    if "_15" not in c and "5_15" not in c and "2_" not in c
]
socio_reach_compare_columns = [c + "_median" for c in hex_reach_component_cols]
del hex_reach_comparison

socio_cluster_gdf = socio_cluster_gdf[
    socio_cluster_gdf["population_density"] > 0
].copy()

socio_cluster_gdf["Low Stress Density"] = socio_cluster_gdf["lts_1_2_dens"]
socio_cluster_gdf["Low Stress Reach (median)"] = socio_cluster_gdf["lts2_reach_median"]
socio_cluster_gdf["Low Stress Reach (mean)"] = socio_cluster_gdf["lts2_reach_average"]


socio_gdf = socio_cluster_gdf[
    [
        "id",
        "geometry",
        "Households w car (share)",
        "Household income 50th percentile",
        "Low Stress Density",
        "Low Stress Reach (median)",
        "Low Stress Reach (mean)",
    ]
].copy()

del socio_cluster_gdf
# %%
###### GINI INDEX ######
# based on https://geographicdata.science/book/notebooks/09_spatial_inequality.html

columns = [
    "Low Stress Density",
    "Low Stress Reach (median)",
    "Low Stress Reach (mean)",
    "Household income 50th percentile",
]

for c in columns:
    plot_func.make_gini_plot(socio_gdf, c)


inequalities = (
    socio_gdf[columns].apply(analysis_func.gini_by_col, axis=0).to_frame("gini")
)

# %%
########## SPATIAL GINI ##########

w = analysis_func.spatial_weights_combined(socio_gdf, id_columns[1], k_socio)

# transform to binary
w.transform = "B"

for c in columns:
    gini_spatial = Gini_Spatial(socio_gdf[c], w)

    gini_spatial.g
    print(f"Spatial Gini for {c}: {gini_spatial.g:.2f}")

    gini_spatial.wcg_share
    print(f"Share of within-cluster inequality for {c}: {gini_spatial.wcg_share:.2f}")

    gini_spatial.p_sim
    print(f"p-value for {c}: {gini_spatial.p_sim}")

    print("\n")


spatial_gini_results = (
    socio_gdf[columns].apply(analysis_func.gini_spatial_by_column, weights=w).T
)

"""
Statistical significance indicates "that inequality between neighboring pairs of counties is different 
from the inequality between county pairs that are not geographically proximate."
"""

# TODO: EXPORT RESULTS
# %%
############# THEIL INDEX #############

inequalities["theil"] = socio_gdf[columns].apply(analysis_func.theil, axis=0)

# TODO: EXPORT RESULTS
# %%
## decomposition

# define groups!

theil_dr = inequality.theil.TheilD(socio_gdf[years].values, socio_gdf.Region)

theil_dr.bg


inequalities["theil_between"] = theil_dr.bg
inequalities["theil_within"] = theil_dr.wg

inequalities["theil_between_share"] = (
    inequalities["theil_between"] / inequalities["theil"]
)


inequalities[["theil_between", "theil_within", "theil_between_share"]].plot(
    subplots=True, figsize=(10, 8)
)


# %%
####### BIVARIATE MORAN's I #######

from esda.moran import Moran_BV, Moran_Local_BV
from splot.esda import plot_local_autocorrelation, moran_scatterplot
from splot.esda import plot_moran_bv_simulation, plot_moran_bv
from esda.moran import Moran_Local_BV
from esda.moran import Moran_Local
from esda.moran import Moran
import matplotlib.pyplot as plt
from libpysal.weights.contiguity import Queen
from libpysal import examples
import np as np
import pandas as pd
import geopandas as gpd
import os
import splot
from splot.esda import lisa_cluster

y = gdf["Donatns"].values
w = Queen.from_dataframe(gdf)
w.transform = "r"

x = gdf["Suicids"].values


moran = Moran(y, w)
moran_bv = Moran_BV(y, x, w)
moran_loc = Moran_Local(y, w)
moran_loc_bv = Moran_Local_BV(y, x, w)

fig, axs = plt.subplots(2, 2, figsize=(15, 10), subplot_kw={"aspect": "equal"})

moran_scatterplot(moran, ax=axs[0, 0])
moran_scatterplot(moran_loc, p=0.05, ax=axs[1, 0])
moran_scatterplot(moran_bv, ax=axs[0, 1])
moran_scatterplot(moran_loc_bv, p=0.05, ax=axs[1, 1])
plt.show()

plot_moran_bv(moran_bv)
plt.show()


moran_loc_bv = Moran_Local_BV(x, y, w)
fig, ax = moran_scatterplot(moran_loc_bv, p=0.05)
ax.set_xlabel("Donatns")
ax.set_ylabel("Spatial lag of Suicids")
plt.show()

plot_local_autocorrelation(moran_loc_bv, gdf, "Suicids")
plt.show()

# %%
### NEEDS GAP

# Requires higher areas density data set!!


# %%

# Suits index ??
