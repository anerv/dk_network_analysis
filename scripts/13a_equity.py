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
import seaborn as sns

# from pysal.explore import inequality
# from inequality.gini import Gini_Spatial
# import seaborn as sns
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

hex_pop_clusters = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM clustering.hex_clusters;", engine, geom_col="geometry"
)

hexgrid = hex_pop_clusters.merge(hex_density, on="hex_id", how="left")

assert len(hexgrid == len(hex_density))

hexgrid.fillna(0, inplace=True)

labels_hex = [
    "lts 1 length",
    "lts ≤2 length",
    "lts ≤3 length",
    "lts ≤4 length",
    "total network length",
    "bikeability rank",
]
inequality_columns_hex = [
    "lts_1_length",
    "lts_1_2_length",
    "lts_1_3_length",
    "lts_1_4_length",
    "total_network_length",
    "kmeans_net",
]

# %%

# SOCIO
# get socio gdf (with shares of socio vars)
exec(open("../helper_scripts/prepare_socio_cluster_data.py").read())
socio.drop(columns=["geometry"], inplace=True)

socio_pop = pd.read_sql(
    "SELECT id, population, households, municipal_id FROM socio;", engine
)

density_socio = pd.read_sql("SELECT * FROM density.density_socio;", engine)
density_socio.drop(columns=["geometry"], inplace=True)

socio_clusters = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM clustering.socio_socio_clusters;", engine, geom_col="geometry"
)

socio_density = socio.merge(density_socio, on="id", how="left")

socio_density = socio_density.merge(socio_pop, on="id", how="left")

socio_gdf = socio_clusters.merge(socio_density, on="id", how="left")

socio_gdf.fillna(0, inplace=True)

assert len(socio_gdf[socio_gdf["total_network_length"].isna()]) == 0
assert len(socio_gdf[socio_gdf["population"].isna()]) == 0
assert len(socio_gdf) == len(socio_density) == len(socio_clusters)

# socio_gdf["low_stress_per_person"] = (
#     socio_gdf["lts_1_2_length"] / socio_gdf["population"]
# )

# socio_gdf["high_stress_per_person"] = (
#     socio_gdf["lts_3_length"] + socio_gdf["lts_4_length"]
# ) / socio_density["population"]

# socio_gdf["network_per_person"] = (
#     socio_gdf["total_network_length"] / socio_gdf["population"]
# )
# %%
labels_socio = [
    # "low stress infrastructure per person",
    # "high stress infrastructure per person",
    # "road network",
    # "lts 1 density",
    # "lts ≤2 density",
    "lts 1 length",
    "lts ≤2 length",
    "lts ≤3 length",
    "lts ≤4 length",
    "total network length",
]
inequality_columns_socio = [
    # "low_stress_per_person",
    # "high_stress_per_person",
    # "network_per_person",
    # "lts_1_dens",
    # "lts_1_2_dens",
    "lts_1_length",
    "lts_1_2_length",
    "lts_1_3_length",
    "lts_1_4_length",
    "total_network_length",
]
# %%
############## LORENZ CURVES ##############

for i, c in enumerate(inequality_columns_socio):

    cumulative_share = analysis_func.compute_cumulative_shares(socio_gdf[c])

    pop_shares, y_shares = analysis_func.lorenz(cumulative_share)

    plot_func.plot_lorenz(
        cumulative_share=cumulative_share,
        share_of_population=pop_shares,
        x_label="population",
        y_label=labels_socio[i],
    )

# %%
############## GINI ##############

inequalities_socio = (
    socio_gdf[inequality_columns_socio]
    .apply(analysis_func.gini_by_col, axis=0)
    .to_frame("gini")
)

inequalities_socio.index.name = "socio variable"

########## THEIL ##########

inequalities_socio["theil"] = socio_gdf[inequality_columns_socio].apply(
    analysis_func.compute_theil, axis=0
)

display(inequalities_socio)

# NOTE: Use this to say that even though inequality exists for the entire road network, it is larger for low stress!


# %%

socio_gdf["urban_rural"] = socio_gdf["Urban area (%)"].apply(
    analysis_func.classify_urban_rural
)

# %%
for c, l in zip(
    ["socio_label", "municipal_id", "urban_rural"],
    ["socio_clusters", "municipality", "urban_rural"],
):

    theil_dr = inequality.theil.TheilD(
        socio_gdf[inequality_columns_socio].values, socio_gdf[c]
    )

    inequalities_socio[f"theil_between_{l}"] = theil_dr.bg
    inequalities_socio[f"theil_within_{l}"] = theil_dr.wg

    inequalities_socio[f"theil_between_share_{l}"] = (
        inequalities_socio[f"theil_between_{l}"] / inequalities_socio["theil"]
    )

    theil_ds = inequality.theil.TheilDSim(
        socio_gdf[inequality_columns_socio].values, socio_gdf[c], 999
    )

    inequalities_socio[f"theil_psim_{l}"] = theil_ds.bg_pvalue


display(inequalities_socio)

# %%
########## SPATIAL GINI ##########

# """
# Statistical significance indicates "that inequality between neighboring pairs of counties is different
# from the inequality between county pairs that are not geographically proximate."
# """

w_socio = weights.contiguity.Queen.from_dataframe(
    socio_gdf,
    use_index=False,
)

# transform to binary
w_socio.transform = "B"

spatial_gini_results_socio = (
    socio_gdf[inequality_columns_socio]
    .apply(analysis_func.gini_spatial_by_column, weights=w_socio)
    .T
)

spatial_gini_results_socio.index.name = "socio variable"
display(spatial_gini_results_socio)

# %%

# Compute spatial gini for lts density at hex level
w_hex = weights.contiguity.Queen.from_dataframe(
    hexgrid,
    use_index=False,
)

# transform to binary
w_hex.transform = "B"

spatial_gini_results_hex = (
    hexgrid[inequality_columns_hex]
    .apply(analysis_func.gini_spatial_by_column, weights=w_hex)
    .T
)

spatial_gini_results_hex.index.name = "hex variable"
display(spatial_gini_results_hex)

# %%
# Theil at hex level

# join socio id to hexes
socio_geoms = socio_gdf[["id", "geometry"]]

hexgrid_centroids = hexgrid.copy()
hexgrid_centroids["geometry"] = hexgrid["geometry"].apply(lambda x: x.centroid)

hexjoin = gpd.sjoin(hexgrid_centroids, socio_geoms, how="inner", predicate="intersects")
assert len(hexjoin.hex_id.unique()) == len(hexjoin)

hexjoin.drop(columns=["index_right"], inplace=True)

unjoined = hexgrid[~hexgrid_centroids["hex_id"].isin(hexjoin["hex_id"])]
assert len(unjoined) == len(hexgrid_centroids) - len(hexjoin)

hexjoin2 = gpd.sjoin(unjoined, socio_geoms, how="inner", predicate="intersects")
hexjoin2.drop(columns=["index_right"], inplace=True)
hexjoin2.drop_duplicates(subset="hex_id", inplace=True)

hexjoin = pd.concat([hexjoin, hexjoin2])
assert len(hexjoin) <= len(hexgrid)

hexjoin.rename(columns={"id": "socio_id"}, inplace=True)

# %%

inequalities_hex = (
    hexjoin[inequality_columns_hex]
    .apply(analysis_func.compute_theil, axis=0)
    .to_frame("theil")
)

theil_dr = inequality.theil.TheilD(
    hexjoin[inequality_columns_hex].values, hexjoin.socio_id
)

inequalities_hex["theil_between"] = theil_dr.bg
inequalities_hex["theil_within"] = theil_dr.wg

inequalities_hex["theil_between_share"] = (
    inequalities_hex["theil_between"] / inequalities_hex["theil"]
)

display(inequalities_hex)

# NOTE: Use this to say that there still is a lot of inequality within the same socio group

# %%

theil_ds = inequality.theil.TheilDSim(
    hexjoin[inequality_columns_hex].values, hexjoin.socio_id, 999
)

# %%

# Compute CCI for inequity columns - rank by income and car ownership


def concentration_index(
    data,
    opportunity,
    population,
    income,
):
    # Based on/copied from https://github.com/ipeaGIT/accessibility/blob/main/R/concentration_index.R

    """
    Calculate the concentration index.

    Parameters:
    - data (pd.DataFrame): The dataset.
    - opportunity (str): Column name representing the opportunity measure (e.g. access to low stress infrastructure).
    - population (str): Column name representing the population.
    - socioeconomic (str): Column name representing socioeconic variable (e.g. income).

    Returns:
    - pd.DataFrame: Results with concentration index calculations by group.
    """

    assert isinstance(opportunity, str), "'opportunity' must be a string."
    assert isinstance(population, str), "'population' must be a string."
    assert isinstance(income, str), "'income' must be a string."

    # Sort data by income and group_by columns
    sort_cols = [income]
    data = data.sort_values(by=sort_cols)

    # Fractional rank calculation (based on Equation 4 of the referenced paper)
    def calculate_fractional_rank(df):
        df["pop_share"] = df[population] / df[population].sum()
        df["fractional_rank"] = (
            df["pop_share"].cumsum().shift(fill_value=0) + df["pop_share"] / 2
        )
        return df

    data = calculate_fractional_rank(data)

    # Calculate average accessibility
    def calculate_avg_access(df):
        avg_access = np.average(df[opportunity], weights=df[population])
        df["avg_access"] = avg_access
        df["diff_from_avg"] = df[opportunity] - avg_access
        return df

    data = calculate_avg_access(data)

    # Contribution to total calculation
    data["cont_to_total"] = (
        (data["fractional_rank"] - 0.5)
        * data["diff_from_avg"]
        * data["pop_share"]
        / data["avg_access"]
    )

    # If no rows and no grouping, return empty result
    if data.empty:
        return pd.DataFrame(columns=["concentration_index"])

    # Calculate the concentration index

    # Handle corrected type
    def add_correction_factor(df):
        upper = df[opportunity].max()
        lower = df[opportunity].min()
        avg_access = df["avg_access"].iloc[0]  # Same within group
        correction_factor = 4 * avg_access / (upper - lower) if upper != lower else 0
        df["correction_factor"] = correction_factor
        return df

    data = add_correction_factor(data)

    data["cont_to_total_corrected"] = data["cont_to_total"] * data["correction_factor"]

    concentration_index_value = 2 * data["cont_to_total_corrected"].sum()
    result = pd.DataFrame({"concentration_index": [concentration_index_value]})

    return result  # , data


def concentr(x, y, w=None):
    if w is None:
        w = np.ones(len(x))

    # Ensure x, y, and w are numpy arrays
    x = np.array(x)
    y = np.array(y)
    w = np.array(w)

    # Complete cases: valid values for x, y, and w
    complete = (np.isfinite(x) & np.isfinite(y) & np.isfinite(w)) & (x >= 0) & (y >= 0)
    x_c = x[complete]
    y_c = y[complete]
    w_c = w[complete]

    # Order by y values
    o = np.argsort(y_c)
    x_o = x_c[o]
    y_o = y_c[o]
    w_o = w_c[o]

    # Cumulative sums for x and weights
    x_cum = np.concatenate(([0], np.cumsum((x_o * w_o) / np.sum(x_o * w_o))))
    w_cum = np.concatenate(([0], np.cumsum(w_o / np.sum(w_o))))

    b = x_cum[:-1]
    B = x_cum[1:]
    h = np.diff(w_cum)

    # Calculate area under the concentration curve
    area_under_concentrationCurve = np.sum(((B + b) * h) / 2)

    return 1 - 2 * area_under_concentrationCurve


# %%
test = concentr(
    socio_gdf["lts_1_dens"],
    socio_gdf["Income 750k+ (share)"],
    socio_gdf["population"],
)

test2 = concentration_index(
    socio_gdf,
    "lts_1_dens",
    "population",
    "Income 750k+ (share)",
)

# %%

socio_gdf["household_low_income_share"] = (
    socio_gdf["Income under 150k (share)"]
    + socio_gdf["Income 150-200k (share)"]
    + socio_gdf["Income 200-300k (share)"]
)
socio_gdf["household_medium_income_share"] = (
    socio_gdf["Income 300-400k (share)"] + socio_gdf["Income 400-500k (share)"]
)
socio_gdf["household_high_income_share"] = (
    socio_gdf["Income 500-750k (share)"] + socio_gdf["Income 750k+ (share)"]
)

rank_columns = [
    "household_low_income_share",
    "household_medium_income_share",
    "household_high_income_share",
    "Household income 50th percentile",
    "Households w car (share)",
    "Population density",
]

# %%

for socioeconomic_column in rank_columns:

    for analysis_column in inequality_columns_socio[:1]:

        cci = concentration_index(
            data=socio_gdf,
            opportunity=analysis_column,
            population="population",
            income=socioeconomic_column,
        )

        print(
            f"The CCI for {analysis_column}, ranked by {socioeconomic_column}, is {cci.loc[0,"concentration_index"]:.4f}"
        )

# %%

# TODO: Implement for various variables!

plot_func.plot_concentration_curves(
    socio_gdf,
    "lts_1_dens",
    "population",
    "Income 750k+ (share)",
    income_label="share of high income households",
    oppportunity_label="low stress infrastructure",
    # "Households no car (share)",
)

# NOTE: Should use density instead of length for this step? Does not normalize by population

# TODO: How is population used? Does it make normalizing by population redundant?
# TODO: Check results!

# TODO: Check interpretation - meaning of negative vs. positive values

# TODO: Test for differences in results between the two methods
# TODO: get chatten to explain differences in functions
