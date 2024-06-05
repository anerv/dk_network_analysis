# %%
from src import plotting_functions as plot_func
from src import analysis_functions as analysis_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import plotly.express as px

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)


# %%

# TODO: Decide what to check sensitivity for? But implement general function!

# For different aggregation levels: administrative, socio, hexgrid
# For different metrics: density, fragmentation, reach

# For each aggregation level, check sensitivity for different k values (maybe 3 different?)
# TODO
# For adm, socio, hex:
# Check LTS densities (ind) and LTS share
# Check comp count, comp per km?

# for hex:
# check reach, difference reach

# %%
# Settings

# K-values to test
hex_ks = [6, 18, 36]  # 60
muni_ks = [3, 5, 7]
socio_ks = [4, 8, 12]

all_ks = [muni_ks, socio_ks, hex_ks]

id_columns = ["municipality", "id", "hex_id"]

metrics = ["density", "fragmentation", "reach"]

aggregation_levels = ["administrative", "socio", "hexgrid"]


# %%
####### DENSITY ############
############################

### READ DATA ###
density_muni = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM density.density_municipality;",
    engine,
    crs=crs,
    geom_col="geometry",
)

density_muni.replace(np.nan, 0, inplace=True)

density_socio = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM density.density_socio;",
    engine,
    crs=crs,
    geom_col="geometry",
)

density_socio.replace(np.nan, 0, inplace=True)

density_hex = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM density.density_hex;",
    engine,
    crs=crs,
    geom_col="geometry",
)

density_hex.replace(np.nan, 0, inplace=True)

gdfs = [density_muni, density_socio, density_hex]

for gdf in gdfs:

    for p in length_relative_columns:
        gdf[p] = gdf[p] * 100

    for p in length_relative_steps_columns[1:-1]:
        gdf[p] = gdf[p] * 100

# %%
####### FRAGMENTATION ######
############################

muni_components = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM fragmentation.component_length_muni;",
    engine,
    crs=crs,
    geom_col="geometry",
)

muni_components.replace(np.nan, 0, inplace=True)

socio_components = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM fragmentation.component_length_socio;",
    engine,
    crs=crs,
    geom_col="geometry",
)

socio_components.replace(np.nan, 0, inplace=True)

hex_components = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM fragmentation.component_length_hex;",
    engine,
    crs=crs,
    geom_col="geometry",
)

hex_components.replace(np.nan, 0, inplace=True)

gdfs = [muni_components, socio_components, hex_components]


# %%

all_columns = [
    # length_columns,
    # length_relative_steps_columns,
    component_count_columns,
    component_per_km_columns,
]

for i, gdf in enumerate(gdfs):

    print("Starting sensitivity analysis for aggregation level:", aggregation_levels[i])

    # Compute spatial weights
    w1 = analysis_func.compute_spatial_weights(
        gdf, id_columns[i], "knn", k=all_ks[i][0]
    )  # using filler col for subset
    w2 = analysis_func.compute_spatial_weights(
        gdf, id_columns[i], "knn", k=all_ks[i][1]
    )  # using filler col for subset
    w3 = analysis_func.compute_spatial_weights(
        gdf, id_columns[i], "knn", k=all_ks[i][2]
    )  # using filler col for subset

    all_weigths = {
        "w1": w1,
        "w2": w1,
        "w3": w3,
    }

    for columns in all_columns:

        for c in columns:

            # dictionaries for results
            all_morans = {}
            all_lisas = {}
            hotspot_count = {}
            coldspot_count = {}

            col_names = [c]
            variable_names = [c]

            for name, w in all_weigths.items():

                morans_density = analysis_func.compute_spatial_autocorrelation(
                    col_names,
                    variable_names,
                    gdf,
                    w,
                    [
                        f"../results/spatial_autocorrelation/sensitivity_test/moransi_{aggregation_levels[i]}_{name}_{c}"
                    ],
                    show_plot=False,
                )

                all_morans[name] = morans_density[c].I

                filepaths = [
                    "../results/spatial_autocorrelation/sensitivity_test/"
                    + f"lisa_{c}_{name}_{aggregation_levels[i]}.png"
                ]

                lisas_density = analysis_func.compute_lisa(
                    col_names, variable_names, gdf, w, filepaths, show_plot=False
                )

                all_lisas[name] = lisas_density[c]

                # Export
                q_columns = [v + "_q" for v in variable_names]
                q_columns.append("id")
                gdf.rename({id_columns[i]: "id"}, axis=1)[q_columns].to_csv(
                    "../results/spatial_autocorrelation/sensitivity_test/"
                    + f"spatial_autocorrelation_{name}_{c}_{aggregation_levels[i]}.csv",
                    index=True,
                )

                for v in variable_names:
                    hotspot = len(gdf[gdf[f"{v}_q"] == "HH"])
                    coldspot = len(gdf[gdf[f"{v}_q"] == "LL"])

                    print(
                        f"Using spatial weights {name}, for '{v}', {hotspot} out of {len(gdf)} units ({hotspot/len(gdf)*100:.2f}%) are part of a hotspot."
                    )
                    print(
                        f"Using spatial weights {name}, for '{v}', {coldspot} out of {len(gdf)} units ({coldspot/len(gdf)*100:.2f}%) are part of a coldspot."
                    )
                    print("\n")

                    hotspot_count[name] = hotspot
                    coldspot_count[name] = coldspot

            fig = plt.figure(figsize=(10, 5))

            # creating the bar plot
            plt.bar(all_morans.keys(), all_morans.values(), color="#AA336A", width=0.4)

            plt.xlabel("Spatial weights")
            plt.ylabel("Moran's I")
            plt.title(
                f"Comparison of global spatial autocorrelation for {c} at aggregation {aggregation_levels[i]}"
            )
            plt.show()

            fig = plt.figure(figsize=(10, 5))

            # creating the bar plot
            plt.bar(
                hotspot_count.keys(),
                hotspot_count.values(),
                color="#916E99",
                width=0.4,
            )

            plt.xlabel("Spatial weights")
            plt.ylabel("Number of units in hot spot")
            plt.title(
                f"Comparison of areas in hot spot for {c} at aggregation {aggregation_levels[i]}"
            )
            plt.show()

            fig = plt.figure(figsize=(10, 5))

            # creating the bar plot
            plt.bar(
                coldspot_count.keys(),
                coldspot_count.values(),
                color="#658CBB",
                width=0.4,
            )

            plt.xlabel("Spatial weights")
            plt.ylabel("Number of grid cells in cold spot")
            plt.title(
                f"Comparison of areas in cold spot for {c} at aggregation {aggregation_levels[i]}"
            )
            plt.show()

# %%

####### REACH ##############
############################

hex_reach = gpd.read_postgis(
    "SELECT * FROM reach.hex_reach", engine, geom_col="geometry"
)

hex_reach.replace(np.nan, 0, inplace=True)

gdfs = [hex_reach]


# K-values to test
hex_ks = [6, 18, 36]  # 60

all_ks = [hex_ks]

id_columns = ["hex_id"]

metrics = ["reach"]

aggregation_levels = ["hexgrid"]


# %%

all_columns = [reach_columns]

for i, gdf in enumerate(gdfs):

    print("Starting sensitivity analysis for aggregation level:", aggregation_levels[i])

    # Compute spatial weights
    w1 = analysis_func.compute_spatial_weights(
        gdf, id_columns[i], "knn", k=all_ks[i][0]
    )  # using filler col for subset
    w2 = analysis_func.compute_spatial_weights(
        gdf, id_columns[i], "knn", k=all_ks[i][1]
    )  # using filler col for subset
    w3 = analysis_func.compute_spatial_weights(
        gdf, id_columns[i], "knn", k=all_ks[i][2]
    )  # using filler col for subset

    all_weigths = {
        "w1": w1,
        "w2": w1,
        "w3": w3,
    }

    for columns in all_columns:

        for c in columns:

            # dictionaries for results
            all_morans = {}
            all_lisas = {}
            hotspot_count = {}
            coldspot_count = {}

            col_names = [c]
            variable_names = [c]

            for name, w in all_weigths.items():

                morans_density = analysis_func.compute_spatial_autocorrelation(
                    col_names,
                    variable_names,
                    gdf,
                    w,
                    [
                        f"../results/spatial_autocorrelation/sensitivity_test/moransi_{aggregation_levels[i]}_{c}"
                    ],
                    show_plot=False,
                )

                all_morans[name] = morans_density[c].I

                filepaths = [
                    "../results/spatial_autocorrelation/sensitivity_test/"
                    + f"lisa_{c}_{name}_{aggregation_levels[i]}.png"
                ]

                lisas_density = analysis_func.compute_lisa(
                    col_names, variable_names, gdf, w, filepaths, show_plot=False
                )

                all_lisas[name] = lisas_density[c]

                # Export
                q_columns = [v + "_q" for v in variable_names]
                q_columns.append("id")
                gdf.rename({id_columns[i]: "id"}, axis=1)[q_columns].to_csv(
                    "../results/spatial_autocorrelation/sensitivity_test/"
                    + f"spatial_autocorrelation_{name}_{c}_{aggregation_levels[i]}.csv",
                    index=True,
                )

                for v in variable_names:
                    hotspot = len(gdf[gdf[f"{v}_q"] == "HH"])
                    coldspot = len(gdf[gdf[f"{v}_q"] == "LL"])

                    print(
                        f"Using spatial weights {name}, for '{v}', {hotspot} out of {len(gdf)} units ({hotspot/len(gdf)*100:.2f}%) are part of a hotspot."
                    )
                    print(
                        f"Using spatial weights {name}, for '{v}', {coldspot} out of {len(gdf)} units ({coldspot/len(gdf)*100:.2f}%) are part of a coldspot."
                    )
                    print("\n")

                    hotspot_count[name] = hotspot
                    coldspot_count[name] = coldspot

            fig = plt.figure(figsize=(10, 5))

            # creating the bar plot
            plt.bar(all_morans.keys(), all_morans.values(), color="#AA336A", width=0.4)

            plt.xlabel("Spatial weights")
            plt.ylabel("Moran's I")
            plt.title(
                f"Comparison of global spatial autocorrelation for {c} at aggregation {aggregation_levels[i]}"
            )
            plt.show()

            fig = plt.figure(figsize=(10, 5))

            # creating the bar plot
            plt.bar(
                hotspot_count.keys(),
                hotspot_count.values(),
                color="#916E99",
                width=0.4,
            )

            plt.xlabel("Spatial weights")
            plt.ylabel("Number of units in hot spot")
            plt.title(
                f"Comparison of areas in hot spot for {c} at aggregation {aggregation_levels[i]}"
            )
            plt.show()

            fig = plt.figure(figsize=(10, 5))

            # creating the bar plot
            plt.bar(
                coldspot_count.keys(),
                coldspot_count.values(),
                color="#658CBB",
                width=0.4,
            )

            plt.xlabel("Spatial weights")
            plt.ylabel("Number of grid cells in cold spot")
            plt.title(
                f"Comparison of areas in cold spot for {c} at aggregation {aggregation_levels[i]}"
            )
            plt.show()
# %%
