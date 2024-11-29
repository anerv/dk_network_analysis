# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
from src import analysis_functions as analysis_func
import geopandas as gpd
import pandas as pd
from IPython.display import display
from pysal.explore import inequality
from pysal.lib import weights

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/df_styler.py").read())

plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

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
    "LTS 1 density",
    "LTS ≤2 density",
    "LTS ≤3 density",
    "LTS ≤4 density",
    "total network density",
    "bikeability rank",
]
inequality_columns_hex = [
    "lts_1_dens",
    "lts_1_2_dens",
    "lts_1_3_dens",
    "lts_1_4_dens",
    "total_network_dens",
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

socio_gdf["household_low_income_pct"] = (
    socio_gdf["Income under 150k (%)"]
    + socio_gdf["Income 150-200k (%)"]
    + socio_gdf["Income 200-300k (%)"]
)
socio_gdf["household_medium_income_pct"] = (
    socio_gdf["Income 300-400k (%)"] + socio_gdf["Income 400-500k (%)"]
)
socio_gdf["household_high_income_pct"] = (
    socio_gdf["Income 500-750k (%)"] + socio_gdf["Income 750k+ (%)"]
)

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
    "lts 1 density",
    "lts ≤2 density",
    "lts ≤3 density",
    "lts ≤4 density",
    "total network density",
    # "lts 1 length",
    # "lts ≤2 length",
    # "lts ≤3 length",
    # "lts ≤4 length",
    # "total network length",
]
inequality_columns_socio = [
    "lts_1_dens",
    "lts_1_2_dens",
    "lts_1_3_dens",
    "lts_1_4_dens",
    "total_network_dens",
    # "lts_1_length",
    # "lts_1_2_length",
    # "lts_1_3_length",
    # "lts_1_4_length",
    # "total_network_length",
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
hexgrid_centroids["geometry"] = hexgrid["geometry"].apply(
    lambda opportunity: opportunity.centroid
)

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

check_significance = False
if check_significance:

    theil_ds = inequality.theil.TheilDSim(
        hexjoin[inequality_columns_hex].values, hexjoin.socio_id, 999
    )

# %%

# Compute CCI for inequity columns - rank by income and car ownership

# CCI: "Negative values indicate that inequalities favor the poor, while positive values indicate a pro-rich bias"
# https://github.com/ipeaGIT/accessibility/blob/HEAD/R/concentration_index.R

rank_columns = [
    "household_low_income_pct",
    "household_medium_income_pct",
    "household_high_income_pct",
    "Household income 50th percentile",
    "Household income 80th percentile",
    "Households w car (%)",
    "Households no car (%)",
]

rank_labels = [
    "low income %",
    "medium income %",
    "high income %",
    "income 50th percentile",
    "income 80th percentile",
    "households with car",
    "households without car",
]

analysis_columns = []
ranking_columns = []
cci_results = []

for socioeconomic_column in rank_columns:

    for analysis_column in inequality_columns_socio:

        cci = analysis_func.concentration_index(
            data=socio_gdf,
            opportunity=analysis_column,
            population="population",
            income=socioeconomic_column,
        )

        analysis_columns.append(analysis_column)
        ranking_columns.append(socioeconomic_column)
        cci_results.append(cci)

        # cci2 = analysis_func.concentr(
        #     socio_gdf[analysis_column],
        #     socio_gdf[socioeconomic_column],
        #     socio_gdf["population"],
        # )


cci_df = pd.DataFrame(
    {
        "analysis_column": analysis_columns,
        "ranking_column": ranking_columns,
        "cci": cci_results,
    }
)
# %%

for e, socioeconomic_column in enumerate(rank_columns):

    for i, analysis_column in enumerate(inequality_columns_socio):

        plot_func.plot_concentration_curves(
            socio_gdf,
            analysis_column,
            "population",
            "Households w car (%)",
            income_label=rank_labels[e],
            oppportunity_label=labels_socio[i],
        )

# NOTE: Should use density instead of length for this step?? Does not normalize by population

# %%

# TODO: Check results!

# TODO: Examine and identify outlier areas!
# %%


# %%
