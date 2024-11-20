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

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/df_styler.py").read())

plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

# %%
# TODO: Compute Regular Gini and Theil for cummulative low stress vs. cummulative people (geobook)

# TODO: Compute spatial gini for lts density and bikeability at hex and socio level

# TODO: Compute Concentration index (order by income or car ownership) (see karner et al 2024)

# %%
# Prepare data
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


# %%
def lorenz(y):
    y = np.asarray(y)
    sorted_y = np.sort(y)
    y_shares = (sorted_y / sorted_y.sum()).cumsum()
    N = y.shape[0]

    pop_shares = np.arange(1, N + 1) / N
    return pop_shares, y_shares


def plot_lorenz(
    cumulative_share,
    share_of_population,
    x_label,
    y_label,
    figsize=(6, 6),
):

    f, ax = plt.subplots(figsize=figsize)

    ax.plot(share_of_population, cumulative_share, label="Lorenz Curve")
    # Plot line of perfect equality
    ax.plot((0, 1), (0, 1), color="r", label="Perfect Equality")
    # Label horizontal axis
    ax.set_xlabel(f"Share of {x_label}")
    # Label vertical axis
    ax.set_ylabel(f"Share of {y_label}")
    # Add legend
    ax.legend()

    plt.legend(frameon=False)

    sns.despine()

    plt.show()

    plt.close()


def compute_cumulative_shares(values):

    shares = values.sort_values() / values.sum()
    return shares.cumsum()


def gini_by_col(column):
    return inequality.gini.Gini(column.values).g


# %%
# LORENZ CURVES FOR NETWORK LENGTHS PER PERSON

socio_density["low_stress_per_person"] = (
    socio_density["lts_1_2_length"] / socio_density["population"]
)

socio_density["high_stress_per_person"] = (
    socio_density["lts_3_length"] + socio_density["lts_4_length"]
) / socio_density["population"]

socio_density["network_per_person"] = (
    socio_density["total_network_length"] / socio_density["population"]
)

labels = [
    "low stress infrastructure",
    "high stress infrastructure",
    "road network",
    "lts 1 density",
    "lts ≤2 density",
]
inequality_columns = [
    "low_stress_per_person",
    "high_stress_per_person",
    "network_per_person",
    "lts_1_dens",
    "lts_1_2_dens",
]

for i, c in enumerate(inequality_columns):

    cumulative_share = compute_cumulative_shares(socio_density[c])

    pop_shares, y_shares = lorenz(cumulative_share)

    plot_lorenz(
        cumulative_share=cumulative_share,
        share_of_population=pop_shares,
        x_label="population",
        y_label=labels[i],
    )

# %%
# Compute gini


def theil(column):
    return inequality.theil.Theil(column.values).T


def gini_spatial_by_column(values, weights):
    gs = Gini_Spatial(values, weights)
    denom = 2 * values.mean() * weights.n**2
    near_diffs = gs.wg / denom
    far_diffs = gs.wcg / denom
    out = pd.Series(
        {
            "gini": gs.g,
            "near_diffs": near_diffs,
            "far_diffs": far_diffs,
            "p_sim": gs.p_sim,
        }
    )
    return out


inequalities = (
    socio_density[inequality_columns].apply(gini_by_col, axis=0).to_frame("gini")
)

inequalities["theil"] = socio_density[inequality_columns].apply(theil, axis=0)

# %%

# 1. Compute theil at hex level
# 2. Assign socio to hexes
# 3. Compute theil again, looking at within and between inequality

# Repeat for socio but using different groupings (e.g. rural vs urban, municipality, etc.)

# %%
## ************************** OLD CODE ************************** ##
# generate socio reach comparison columns
exec(open("../helper_scripts/generate_socio_reach_columns.py").read())

socio_cluster_gdf = socio_cluster_gdf[
    socio_cluster_gdf["population_density"] > 0
].copy()

socio_cluster_gdf["Low Stress Density"] = socio_cluster_gdf["lts_1_2_dens"]
socio_cluster_gdf["Low Stress Reach (median)"] = socio_cluster_gdf["lts2_reach_median"]
socio_cluster_gdf["Low Stress Reach (mean)"] = socio_cluster_gdf["lts2_reach_average"]

# TODO: compute columns for cumulative share of income and car ownership

# COMPUTE share of high, medium, low income
socio_cluster_gdf["Low income households (share)"] = (
    socio_cluster_gdf["households_income_under_100k_share"]
    + socio_cluster_gdf["households_income_100_150k_share"]
    + socio_cluster_gdf["households_income_150_200k_share"]
)

socio_cluster_gdf["Medium income households (share)"] = socio_cluster_gdf[
    "households_income_200_300k_share"
    + socio_cluster_gdf["households_income_300_400k_share"]
    + socio_cluster_gdf["households_income_400_500k_share"]
]
socio_cluster_gdf["High income households (share)"] = (
    socio_cluster_gdf["households_income_500_750k_share"]
    + socio_cluster_gdf["households_income_750k_share"]
)

assert (
    socio_cluster_gdf["Low income households (share)"]
    + socio_cluster_gdf["Medium income households (share)"]
    + socio_cluster_gdf["High income households (share)"]
    == 1  # socio_cluster_gdf["households"]
)

socio_gdf = socio_cluster_gdf[
    [
        "id",
        "geometry",
        "Households w car (share)",
        "Household income 50th percentile",
        "Low income households (share)",
        "Medium income households (share)",
        "High income households (share)",
        "Low Stress Density",
        "Low Stress Reach (median)",
        "Low Stress Reach (mean)",
        "urban_pct",
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
    "Households w car (share)",
    "Low income households (share)",
    "Medium income households (share)",
    "High income households (share)",
]

for c in columns:
    plot_func.make_gini_plot(socio_gdf, c, fp_equity + "gini_lorenz_" + c + ".png")


inequalities = (
    socio_gdf[columns].apply(analysis_func.gini_by_col, axis=0).to_frame("gini")
)


# %%
########## SPATIAL GINI ##########

w = analysis_func.spatial_weights_combined(
    socio_gdf, id_columns[1], k_socio, silence_warnings=True
)

# transform to binary
w.transform = "B"

for c in columns:
    gini_spatial = Gini_Spatial(socio_gdf[c], w)

    gini_spatial.g
    print(f"Gini for {c}: {gini_spatial.g:.2f}")

    gini_spatial.wcg_share
    print(f"Share of within-cluster inequality for {c}: {gini_spatial.wcg_share:.2f}")

    gini_spatial.p_sim
    print(f"p-value for {c}: {gini_spatial.p_sim}")

    print("\n")


spatial_gini_results = (
    socio_gdf[columns].apply(analysis_func.gini_spatial_by_column, weights=w).T
)

display(spatial_gini_results)

# """
# Statistical significance indicates "that inequality between neighboring pairs of counties is different
# from the inequality between county pairs that are not geographically proximate."
# """

spatial_gini_results.to_csv(fp_equity + "spatial_gini_results.csv")
# %%
############# THEIL INDEX #############

inequalities["theil"] = socio_gdf[columns].apply(analysis_func.theil, axis=0)

display(inequalities)

# %%
## decomposition

# define groups!
# based on urban percentage

socio_gdf["group"] = None


socio_gdf["group"] = np.where(socio_gdf["urban_pct"] < 0.2, 5, socio_gdf.group)
socio_gdf["group"] = np.where(socio_gdf["urban_pct"] < 0.05, 6, socio_gdf.group)
socio_gdf["group"] = np.where(socio_gdf["urban_pct"] > 0.2, 4, socio_gdf.group)
socio_gdf["group"] = np.where(socio_gdf["urban_pct"] > 0.4, 3, socio_gdf.group)
socio_gdf["group"] = np.where(socio_gdf["urban_pct"] > 0.6, 2, socio_gdf.group)
socio_gdf["group"] = np.where(socio_gdf["urban_pct"] > 0.8, 1, socio_gdf.group)
socio_gdf["group"] = np.where(socio_gdf["urban_pct"] > 0.95, 0, socio_gdf.group)


# %%

# TODO: INTERPRETATION
theil_dr = inequality.theil.TheilD(socio_gdf[columns].values, socio_gdf.group)

theil_dr.bg

inequalities["theil_between"] = theil_dr.bg
inequalities["theil_within"] = theil_dr.wg

inequalities["theil_between_share"] = (
    inequalities["theil_between"] / inequalities["theil"]
)


inequalities[["theil_between", "theil_within", "theil_between_share"]].plot(
    subplots=True, figsize=(10, 8)
)

inequalities.to_csv(fp_equity + "inequalities.csv")

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
