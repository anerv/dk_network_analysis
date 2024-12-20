# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
from src import analysis_functions as analysis_func
import geopandas as gpd
import pandas as pd
from IPython.display import display
from pysal.explore import inequality
from pysal.lib import weights
import matplotlib.pyplot as plt
import seaborn as sns

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
    # "total network density",
    "LTS 1 length",
    "LTS ≤2 length",
    "LTS ≤3 length",
    "LTS ≤4 length",
    "total network length",
    "bikeability rank",
]
inequality_columns_hex = [
    "lts_1_dens",
    "lts_1_2_dens",
    "lts_1_3_dens",
    "lts_1_4_dens",
    # "total_network_dens",
    "lts_1_length",
    "lts_1_2_length",
    "lts_1_3_length",
    "lts_1_4_length",
    # "total_network_length",
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

socio_gdf["lts_1_per_capita"] = socio_gdf["lts_1_dens"] / socio_gdf["population"]
socio_gdf["lts_1_2_per_capita"] = socio_gdf["lts_1_2_dens"] / socio_gdf["population"]
socio_gdf["lts_1_3_per_capita"] = socio_gdf["lts_1_3_dens"] / socio_gdf["population"]
socio_gdf["lts_1_4_per_capita"] = socio_gdf["lts_1_4_dens"] / socio_gdf["population"]


labels_socio = [
    "LTS 1 density",
    "LTS ≤2 density",
    "LTS ≤3 density",
    "LTS ≤4 density",
    # "total network density",
    "LTS 1 length",
    "LTS ≤2 length",
    "LTS ≤3 length",
    "LTS ≤4 length",
    "LTS 1 per capita",
    "LTS ≤2 per capita",
    "LTS ≤3 per capita",
    "LTS ≤4 per capita",
    # "total network length",
]
inequality_columns_socio = [
    "lts_1_dens",
    "lts_1_2_dens",
    "lts_1_3_dens",
    "lts_1_4_dens",
    # "total_network_dens",
    "lts_1_length",
    "lts_1_2_length",
    "lts_1_3_length",
    "lts_1_4_length",
    "lts_1_per_capita",
    "lts_1_2_per_capita",
    "lts_1_3_per_capita",
    "lts_1_4_per_capita",
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
        fp=fp_equity_plots_base + f"lorenz_{c}.png",
    )

# %%
# Combine all lorenz curves into one plot

fig, axes = plt.subplots(2, 4, figsize=(18, 10))

axes = axes.flatten()

for i, c in enumerate(inequality_columns_socio[0:8]):

    axes[i].set_aspect(1)

    cumulative_share = analysis_func.compute_cumulative_shares(socio_gdf[c])

    pop_shares, y_shares = analysis_func.lorenz(cumulative_share)

    plot_func.plot_lorenz_combined(
        ax=axes[i],
        cumulative_share=cumulative_share,
        share_of_population=pop_shares,
        x_label="population",
        y_label=labels_socio[i],
        fontsize=14,
    )

plt.tight_layout()


plt.savefig(fp_equity_lorenz_combined, dpi=pdict["dpi"])

plt.show()

plt.close()

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

inequalities_socio.to_csv(fp_inequalities_socio)

"""
The within regions term is a weighted average of inequality between economies belonging to the same region

"""

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

spatial_gini_results_socio.to_csv(fp_inequalities_socio_spatial_gini)

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

spatial_gini_results_hex.to_csv(fp_inequalities_hex_spatial_gini)

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

inequalities_hex.to_csv(fp_inequalities_theil_hex_socio)
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
    "Households 1 car (%)",
    "Households 2 cars (%)",
    "Households no car (%)",
]

rank_labels = [
    "low income %",
    "medium income %",
    "high income %",
    "income 50th percentile",
    "income 80th percentile",
    "households with car (%)",
    "households with 1 car (%)",
    "households with 2 cars (%)",
    "households no car (%)",
]

analysis_columns = []
ranking_columns = []
cci_results = []

for socioeconomic_column in rank_columns:

    for analysis_column in inequality_columns_socio:

        cci = analysis_func.corrected_concentration_index(
            data=socio_gdf,
            opportunity=analysis_column,
            population="population",
            income=socioeconomic_column,
        )
        # cci = analysis_func.concentr(
        #     socio_gdf[analysis_column],
        #     socio_gdf[socioeconomic_column],
        #     socio_gdf["population"],
        # )

        analysis_columns.append(analysis_column)
        ranking_columns.append(socioeconomic_column)
        cci_results.append(cci)


cci_df = pd.DataFrame(
    {
        "analysis_column": analysis_columns,
        "ranking_column": ranking_columns,
        "cci": cci_results,
    }
)

cci_df.to_csv(fp_inequalities_cci, index=False)

# %%
# Make tables for the report

cci_subset = cci_df.loc[
    cci_df.ranking_column.isin(
        [
            "household_low_income_pct",
            "household_medium_income_pct",
            "household_high_income_pct",
            "Households w car (%)",
            # "Households 1 car (%)",
            # "Households 2 cars (%)",
        ]
    )
]

# %%
# Restructure cci_subset
cci_pivot = cci_subset.pivot(
    index="ranking_column", columns="analysis_column", values="cci"
).rename_axis(index=None, columns=None)

cci_pivot = cci_pivot[inequality_columns_socio]
# %%
cci_values = cci_pivot.reindex(
    [
        "household_low_income_pct",
        "household_medium_income_pct",
        "household_high_income_pct",
        "Households w car (%)",
        # "Households 1 car (%)",
        # "Households 2 cars (%)",
    ]
)
display(cci_values)

cci_values.to_csv(fp_inequalities_cci_subset)

# %%

for e, socioeconomic_column in enumerate(rank_columns):

    for i, analysis_column in enumerate(inequality_columns_socio):

        plot_func.plot_concentration_curves(
            data=socio_gdf,
            opportunity=analysis_column,
            population="population",
            income=socioeconomic_column,
            income_label=rank_labels[e],
            oppportunity_label=labels_socio[i],
        )

# %%

# Make subplots for each rank column

for e, socioeconomic_column in enumerate(rank_columns):

    fp = (
        fp_equity_plots_base
        + f"concentration_curve_subplots_{socioeconomic_column}.png"
    )

    fig, axes = plt.subplots(3, 4, figsize=(15, 12))

    axes = axes.flatten()

    for i, analysis_column in enumerate(inequality_columns_socio):

        axes[i].set_aspect(1)

        plot_func.plot_concentration_curves_subplots(
            ax=axes[i],
            data=socio_gdf,
            opportunity=analysis_column,
            population="population",
            income=socioeconomic_column,
            # income_label=rank_labels[e],
            oppportunity_label=labels_socio[i],
        )

    plt.suptitle(f"Concentration curves for {rank_labels[e]}")
    sns.despine()

    plt.tight_layout()

    if fp:
        plt.savefig(fp, dpi=pdict["dpi"])

    plt.show()

    plt.close()


# %%
density_columns = ["lts_1_dens", "lts_1_2_dens", "lts_1_3_dens", "lts_1_4_dens"]
length_columns = ["lts_1_length", "lts_1_2_length", "lts_1_3_length", "lts_1_4_length"]
per_capita_columns = [
    "lts_1_per_capita",
    "lts_1_2_per_capita",
    "lts_1_3_per_capita",
    "lts_1_4_per_capita",
]
general_labels = ["LTS 1", "LTS 2", "LTS 3", "LTS 4"]


labels_dens = [
    "LTS 1 density",
    "LTS ≤2 density",
    "LTS ≤3 density",
    "LTS ≤4 density",
]

labels_length = [
    "LTS 1 length",
    "LTS ≤2 length",
    "LTS ≤3 length",
    "LTS ≤4 length",
]

labels_capita = [
    "LTS 1 per capita",
    "LTS ≤2 per capita",
    "LTS ≤3 per capita",
    "LTS ≤4 per capita",
]

for e, socioeconomic_column in enumerate(rank_columns):

    fp = (
        fp_equity_plots_base
        + f"concentration_curve_subplots_combined_{socioeconomic_column}.png"
    )

    fig, axes = plt.subplots(1, len(density_columns), figsize=(20, 6))

    axes = axes.flatten()

    for i, (dens_col, len_col, cap_col) in enumerate(
        zip(density_columns, length_columns, per_capita_columns)
    ):
        axes[i].set_aspect(1)

        plot_func.plot_concentration_curves_combined(
            ax=axes[i],
            data=socio_gdf,
            opportunities=[dens_col, len_col, cap_col],
            population="population",
            income=socioeconomic_column,
            oppportunity_labels=[labels_dens[i], labels_length[i], labels_capita[i]],
            general_opportunity_label=f"{general_labels[i]} infrastructure",
            opportunity_colors=["#882255", "#009988", "#EE7733"],
            fontsize=14,
        )

    sns.despine()

    # plt.suptitle(f"Concentration curves for {rank_labels[e]}", fontsize=14)

    plt.tight_layout()

    if fp:
        plt.savefig(fp, dpi=pdict["dpi"])

    plt.show()

    plt.close()

# %%

fp = fp_equity_plots_base + f"concentration_curves_combined_lts1.png"

rank_columns_subset = [
    "household_low_income_pct",
    "household_medium_income_pct",
    "household_high_income_pct",
    "Households w car (%)",
]

fig, axes = plt.subplots(1, len(rank_columns_subset), figsize=(20, 5))

axes = axes.flatten()

for e, socioeconomic_column in enumerate(rank_columns_subset):

    axes[e].set_aspect(1)

    plot_func.plot_concentration_curves_combined(
        ax=axes[e],
        data=socio_gdf,
        opportunities=[
            density_columns[0],
            length_columns[0],
            per_capita_columns[0],
        ],
        population="population",
        income=socioeconomic_column,
        oppportunity_labels=[labels_dens[0], labels_length[0], labels_capita[0]],
        general_opportunity_label=f"{general_labels[0]} infrastructure",
        opportunity_colors=["#882255", "#009988", "#EE7733"],
        fontsize=14,
    )


sns.despine()

# plt.suptitle(f"Concentration curves for LTS 1", fontsize=14)

plt.tight_layout()

if fp:
    plt.savefig(fp, dpi=pdict["dpi"])

plt.show()

plt.close()

# %%
