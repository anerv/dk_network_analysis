# %%
from src import db_functions as dbf
from src import h3_functions as h3f
from src import plotting_functions as plot_func
import geopandas as gpd
import numpy as np
import seaborn as sns

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

# %%
# PLOT MUNI DENSITY

density_muni = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM density_municipality;",
    engine,
    crs=crs,
    geom_col="geometry",
)
density_muni.replace(0, np.nan, inplace=True)

# %%
plot_cols = [
    "lts_1_dens",
    "lts_2_dens",
    "lts_3_dens",
    "lts_4_dens",
    "total_car_dens",
    "total_network_dens",
]
labels = ["LTS 1", "LTS 2", "LTS 3", "LTS 4", "Total car", "Total network"]
plot_titles = [f"Municipal network density for: {l}" for l in labels]
no_data_cols = plot_cols
filepaths = [f"../results/network_density/administrative/{l}" for l in labels]
cmaps = [pdict["pos"]] * len(plot_cols)

plot_func.plot_polygon_results(
    poly_gdf=density_muni,
    plot_cols=plot_cols,
    plot_titles=plot_titles,
    filepaths=filepaths,
    cmaps=cmaps,
    alpha=pdict["alpha_grid"],
    cx_tile=cx_tile_2,
    no_data_cols=no_data_cols,
)

# Stepwise density
plot_cols = [
    "lts_1_dens",
    "lts_1_2_dens",
    "lts_1_3_dens",
    "lts_1_4_dens",
    "total_car_dens",
    "total_network_dens",
]
labels = ["LTS 1", "LTS 1-2", "LTS 1-3", "LTS 1-4", "Total car", "Total network"]
plot_titles = [f"Municipal network density for: {l}" for l in labels]
no_data_cols = plot_cols
filepaths = [f"../results/network_density/administrative/{l}" for l in labels]
cmaps = [pdict["pos"]] * len(plot_cols)

plot_func.plot_polygon_results(
    poly_gdf=density_muni,
    plot_cols=plot_cols,
    plot_titles=plot_titles,
    filepaths=filepaths,
    cmaps=cmaps,
    alpha=pdict["alpha_grid"],
    cx_tile=cx_tile_2,
    no_data_cols=no_data_cols,
)

# Relative network length
plot_cols = [
    "lts_1_length_rel",
    "lts_1_2_length_rel",
    "lts_1_3_length_rel",
    "lts_1_4_length_rel",
    "lts_7_length_rel",
    # "total_car_length_rel",
]
for p in plot_cols:
    density_muni[p] = density_muni[p] * 100

labels = [
    "LTS 1 (%)",
    "LTS 1-2 (%)",
    "LTS 1-3 (%)",
    "LTS 1-4 (%)",
    "No biking (%)",
    # "Total car (%)",
]

plot_titles = [f"Municipal network length for: {l}" for l in labels]
no_data_cols = plot_cols
filepaths = [f"../results/network_density/administrative/{l}" for l in labels]
cmaps = [pdict["pos"]] * len(plot_cols)

plot_func.plot_polygon_results(
    poly_gdf=density_muni,
    plot_cols=plot_cols,
    plot_titles=plot_titles,
    filepaths=filepaths,
    cmaps=cmaps,
    alpha=pdict["alpha_grid"],
    cx_tile=cx_tile_2,
    no_data_cols=no_data_cols,
)
# %%
# SOCIO

density_socio = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM density_socio;",
    engine,
    crs=crs,
    geom_col="geometry",
)

density_socio.replace(0, np.nan, inplace=True)

plot_cols = [
    "lts_1_dens",
    "lts_2_dens",
    "lts_3_dens",
    "lts_4_dens",
    "total_car_dens",
    "total_network_dens",
]
labels = ["LTS 1", "LTS 2", "LTS 3", "LTS 4", "Total car", "Total network"]
plot_titles = [f"Socio network density for: {l}" for l in labels]
no_data_cols = plot_cols
filepaths = [f"../results/network_density/socio/{l}" for l in labels]
cmaps = [pdict["pos"]] * len(plot_cols)

plot_func.plot_polygon_results(
    poly_gdf=density_socio,
    plot_cols=plot_cols,
    plot_titles=plot_titles,
    filepaths=filepaths,
    cmaps=cmaps,
    alpha=pdict["alpha_grid"],
    cx_tile=cx_tile_2,
    no_data_cols=no_data_cols,
)

# Stepwise density
plot_cols = [
    "lts_1_dens",
    "lts_1_2_dens",
    "lts_1_3_dens",
    "lts_1_4_dens",
    "total_car_dens",
    "total_network_dens",
]
labels = ["LTS 1", "LTS 1-2", "LTS 1-3", "LTS 1-4", "Total car", "Total network"]
plot_titles = [f"Socio network density for: {l}" for l in labels]
no_data_cols = plot_cols
filepaths = [f"../results/network_density/socio/{l}" for l in labels]
cmaps = [pdict["pos"]] * len(plot_cols)

plot_func.plot_polygon_results(
    poly_gdf=density_socio,
    plot_cols=plot_cols,
    plot_titles=plot_titles,
    filepaths=filepaths,
    cmaps=cmaps,
    alpha=pdict["alpha_grid"],
    cx_tile=cx_tile_2,
    no_data_cols=no_data_cols,
)

# Relative network length
plot_cols = [
    "lts_1_length_rel",
    "lts_1_2_length_rel",
    "lts_1_3_length_rel",
    "lts_1_4_length_rel",
    "lts_7_length_rel",
    # "total_car_length_rel",
]
for p in plot_cols:
    density_socio[p] = density_socio[p] * 100

labels = [
    "LTS 1 (%)",
    "LTS 1-2 (%)",
    "LTS 1-3 (%)",
    "LTS 1-4 (%)",
    "No biking (%)",
    # "Total car (%)",
]

plot_titles = [f"Socio network length for: {l}" for l in labels]
no_data_cols = plot_cols
filepaths = [f"../results/network_density/socio/{l}" for l in labels]
cmaps = [pdict["pos"]] * len(plot_cols)

plot_func.plot_polygon_results(
    poly_gdf=density_socio,
    plot_cols=plot_cols,
    plot_titles=plot_titles,
    filepaths=filepaths,
    cmaps=cmaps,
    alpha=pdict["alpha_grid"],
    cx_tile=cx_tile_2,
    no_data_cols=no_data_cols,
)

# %%
# H3

density_h3 = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM density_h3;",
    engine,
    crs=crs,
    geom_col="geometry",
)

density_h3.replace(0, np.nan, inplace=True)

plot_cols = [
    "lts_1_dens",
    "lts_2_dens",
    "lts_3_dens",
    "lts_4_dens",
    "total_car_dens",
    "total_network_dens",
]
labels = ["LTS 1", "LTS 2", "LTS 3", "LTS 4", "Total car", "Total network"]
plot_titles = [f"Local network density for: {l}" for l in labels]
no_data_cols = plot_cols
filepaths = [f"../results/network_density/administrative/{l}.png" for l in labels]
cmaps = [pdict["pos"]] * len(plot_cols)

plot_polygon_results(
    poly_gdf=density_h3,
    plot_cols=plot_cols,
    plot_titles=plot_titles,
    filepaths=filepaths,
    cmaps=cmaps,
    alpha=pdict["alpha_grid"],
    cx_tile=cx_tile_2,
    no_data_cols=no_data_cols,
)

# %%
# Stepwise density
plot_cols = [
    "lts_1_dens",
    "lts_1_2_dens",
    "lts_1_3_dens",
    "lts_1_4_dens",
    "total_car_dens",
    "total_network_dens",
]
labels = ["LTS 1", "LTS 1-2", "LTS 1-3", "LTS 1-4", "Total car", "Total network"]
plot_titles = [f"Local network density for: {l}" for l in labels]
no_data_cols = plot_cols
filepaths = [f"../results/network_density/administrative/{l}.png" for l in labels]
cmaps = [pdict["pos"]] * len(plot_cols)

plot_polygon_results(
    poly_gdf=density_h3,
    plot_cols=plot_cols,
    plot_titles=plot_titles,
    filepaths=filepaths,
    cmaps=cmaps,
    alpha=pdict["alpha_grid"],
    cx_tile=cx_tile_2,
    no_data_cols=no_data_cols,
)

# %%
# Relative network length
plot_cols = [
    "lts_1_length_rel",
    "lts_1_2_length_rel",
    "lts_1_3_length_rel",
    "lts_1_4_length_rel",
    "lts_7_length_rel",
    # "total_car_length_rel",
]
for p in plot_cols:
    density_h3[p] = density_h3[p] * 100

labels = [
    "LTS 1 (%)",
    "LTS 1-2 (%)",
    "LTS 1-3 (%)",
    "LTS 1-4 (%)",
    "No biking (%)",
    # "Total car (%)",
]

plot_titles = [f"Local network length for: {l}" for l in labels]
no_data_cols = plot_cols
filepaths = [f"../results/network_density/administrative/{l}.png" for l in labels]
cmaps = [pdict["pos"]] * len(plot_cols)

plot_polygon_results(
    poly_gdf=density_h3,
    plot_cols=plot_cols,
    plot_titles=plot_titles,
    filepaths=filepaths,
    cmaps=cmaps,
    alpha=pdict["alpha_grid"],
    cx_tile=cx_tile_2,
    no_data_cols=no_data_cols,
)

# %%
# TODO: Plot distribution of network densities for each lts
import seaborn as sns

sns.displot(density_muni, x="lts_1_dens", kind="kde")

sns.histplot(density_muni, x="lts_1_dens", kde=True)
