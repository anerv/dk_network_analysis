# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
from src import analysis_functions as analysis_func
import geopandas as gpd
import numpy as np
import json

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/filepaths.py").read())
plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)


# %%

### READ DATA ###
exec(open("../helper_scripts/read_density.py").read())

gdfs = [density_muni, density_socio, density_hex]

for gdf in gdfs:
    gdf.replace(np.nan, 0, inplace=True)


# %%
k_values = [k_muni, k_socio, k_hex]
spatial_weights_values = [f"queen_{k}" for k in k_values]

spatial_weights = []

for i, gdf in enumerate(gdfs):

    w = analysis_func.spatial_weights_combined(gdf, id_columns[i], k_values[i])

    spatial_weights.append(w)

# %%
all_density_columns = [
    density_columns,
    density_steps_columns[1:-2],
    length_relative_columns,
    length_relative_steps_columns[1:-1],
]

for i, gdf in enumerate(gdfs):

    print(f"At aggregation level: {aggregation_levels[i]}:")

    global_morans_results = {}

    for columns in all_density_columns:

        fps_morans = [
            fp_spatial_auto_density
            + f"{aggregation_levels[i]}/morans_{c}.png".replace(" ", "_")
            for c in columns
        ]

        fps_lisa = [
            fp_spatial_auto_density
            + f"{aggregation_levels[i]}/lisa_{c}.png".replace(" ", "_")
            for c in columns
        ]

        morans_results = analysis_func.compute_spatial_autocorrelation(
            columns, columns, gdf, spatial_weights[i], fps_morans, show_plot=False
        )

        lisa_results = analysis_func.compute_lisa(
            columns,
            columns,
            gdf,
            spatial_weights[i],
            fps_lisa,
            show_plot=False,
        )

        for key, value in morans_results.items():
            global_morans_results[key] = value.I

    with open(
        fp_spatial_auto_density
        + f"{aggregation_levels[i]}/global_moransi_{spatial_weights_values[i]}.json",
        "w",
    ) as outfile:
        json.dump(global_morans_results, outfile)

    q_columns = [c for c in gdf.columns if c.endswith("_q")]
    q_columns.extend(["geometry", id_columns[i]])

    gdf[q_columns].to_parquet(
        fp_spatial_auto_density + f"{aggregation_levels[i]}/lisas.parquet"
    )

# %%
### FRAGMENTATION ###

# READ DATA

exec(open("../helper_scripts/read_component_length_agg.py").read())

gdfs = [component_length_muni, component_length_socio, component_length_hex]

for gdf in gdfs:
    gdf.replace(np.nan, 0, inplace=True)

# %%
# Define spatial weights

k_values = [k_muni, k_socio, k_hex]
spatial_weights_values = [f"queen_{k}" for k in k_values]

spatial_weights = []

for i, gdf in enumerate(gdfs):

    w = analysis_func.spatial_weights_combined(gdf, id_columns[i], k_values[i])

    spatial_weights.append(w)

# %%

all_fragmentation_columns = [
    component_count_columns,
    component_per_km_columns,
    component_per_km_sqkm_columns,
]

for i, gdf in enumerate(gdfs):

    print(f"At aggregation level: {aggregation_levels[i]}:")

    global_morans_results = {}

    for columns in all_fragmentation_columns:

        fps_morans = [
            fp_spatial_auto_fragmentation
            + f"{aggregation_levels[i]}/morans_{c}.png".replace(" ", "_")
            for c in columns
        ]

        fps_lisa = [
            fp_spatial_auto_fragmentation
            + f"{aggregation_levels[i]}/lisa_{c}.png".replace(" ", "_")
            for c in columns
        ]

        morans_results = analysis_func.compute_spatial_autocorrelation(
            columns, columns, gdf, spatial_weights[i], fps_morans, show_plot=False
        )

        lisa_results = analysis_func.compute_lisa(
            columns,
            columns,
            gdf,
            spatial_weights[i],
            fps_lisa,
            show_plot=False,
        )

        for key, value in morans_results.items():
            global_morans_results[key] = value.I

    with open(
        fp_spatial_auto_fragmentation
        + f"{aggregation_levels[i]}/global_moransi_{spatial_weights_values[i]}.json",
        "w",
    ) as outfile:
        json.dump(global_morans_results, outfile)

    q_columns = [c for c in gdf.columns if c.endswith("_q")]
    q_columns.extend(["geometry", id_columns[i]])

    gdf[q_columns].to_parquet(
        fp_spatial_auto_fragmentation + f"{aggregation_levels[i]}/lisas.parquet"
    )

# %%
# *** Largest component size ****

hex_component_size = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM fragmentation.hex_largest_components;",
    engine,
    crs=crs,
    geom_col="geometry",
)

hex_component_size[largest_local_component_len_columns] = hex_component_size[
    largest_local_component_len_columns
].replace(np.nan, 0)


gdfs = [hex_component_size]

# Define spatial weights
id_columns = id_columns[-1:]
k_values = [k_hex]
spatial_weights_values = [f"queen_{k}" for k in k_values]

spatial_weights = []

for i, gdf in enumerate(gdfs):

    w = analysis_func.spatial_weights_combined(gdf, id_columns[i], k_values[i])

    spatial_weights.append(w)

aggregation_level = aggregation_levels[-1:]

all_component_size_columns = [largest_local_component_len_columns]

for i, gdf in enumerate(gdfs):

    print(f"At aggregation level: {aggregation_level[i]}:")

    global_morans_results = {}

    for columns in all_component_size_columns:

        fps_morans = [
            fp_spatial_auto_fragmentation
            + f"{aggregation_level[i]}/morans_{c}.png".replace(" ", "_")
            for c in columns
        ]

        fps_lisa = [
            fp_spatial_auto_fragmentation
            + f"{aggregation_level[i]}/lisa_{c}.png".replace(" ", "_")
            for c in columns
        ]

        morans_results = analysis_func.compute_spatial_autocorrelation(
            columns, columns, gdf, spatial_weights[i], fps_morans, show_plot=False
        )

        lisa_results = analysis_func.compute_lisa(
            columns,
            columns,
            gdf,
            spatial_weights[i],
            fps_lisa,
            show_plot=False,
        )

        for key, value in morans_results.items():
            global_morans_results[key] = value.I

    with open(
        fp_spatial_auto_fragmentation
        + f"{aggregation_level[i]}/global_moransi_largest_component_size_{spatial_weights_values[i]}.json",
        "w",
    ) as outfile:
        json.dump(global_morans_results, outfile)

    q_columns = [c for c in gdf.columns if c.endswith("_q")]
    q_columns.extend(["geometry", id_columns[i]])

    gdf[q_columns].to_parquet(
        fp_spatial_auto_fragmentation
        + f"{aggregation_level[i]}/lisas_largest_component_size_.parquet"
    )

# %%
### REACH #####

exec(open("../helper_scripts/read_reach.py").read())

hex_reach.replace(np.nan, 0, inplace=True)

gdfs = [hex_reach]

# Define spatial weights
id_columns = id_columns[-1:]
k_values = [k_hex]
spatial_weights_values = [f"queen_{k}" for k in k_values]

spatial_weights = []

for i, gdf in enumerate(gdfs):

    w = analysis_func.spatial_weights_combined(gdf, id_columns[i], k_values[i])

    spatial_weights.append(w)

all_reach_columns = [reach_columns, reach_diff_columns, reach_diff_pct_columns]

aggregation_level = aggregation_levels[-1:]

for i, gdf in enumerate(gdfs):

    print(f"At aggregation level: {aggregation_level[i]}:")

    global_morans_results = {}

    for columns in all_reach_columns:

        fps_morans = [
            fp_spatial_auto_reach
            + f"{aggregation_level[i]}/morans_{c}.png".replace(" ", "_")
            for c in columns
        ]

        fps_lisa = [
            fp_spatial_auto_reach
            + f"{aggregation_level[i]}/lisa_{c}.png".replace(" ", "_")
            for c in columns
        ]

        morans_results = analysis_func.compute_spatial_autocorrelation(
            columns, columns, gdf, spatial_weights[i], fps_morans, show_plot=False
        )

        lisa_results = analysis_func.compute_lisa(
            columns,
            columns,
            gdf,
            spatial_weights[i],
            fps_lisa,
            show_plot=False,
        )

        for key, value in morans_results.items():
            global_morans_results[key] = value.I

    with open(
        fp_spatial_auto_reach
        + f"{aggregation_level[i]}/global_moransi_{spatial_weights_values[i]}.json",
        "w",
    ) as outfile:
        json.dump(global_morans_results, outfile)

    q_columns = [c for c in gdf.columns if c.endswith("_q")]
    q_columns.extend(["geometry", id_columns[i]])

    gdf[q_columns].to_parquet(
        fp_spatial_auto_reach + f"{aggregation_level[i]}/lisas.parquet"
    )
# %%
# Reach distance comparison

exec(open("../helper_scripts/read_reach_comparison.py").read())

hex_reach_comparison.replace(np.nan, 0, inplace=True)

gdfs = [hex_reach_comparison]

# Define spatial weights
id_column = id_columns[-1:]
k_values = [k_hex]
spatial_weights_values = [f"queen_{k}" for k in k_values]

spatial_weights = []

for i, gdf in enumerate(gdfs):

    w = analysis_func.spatial_weights_combined(gdf, id_column[i], k_values[i])

    spatial_weights.append(w)

compare_reach_columns = hex_reach_comparison.columns.to_list()
# %%
compare_reach_columns = [
    c
    for c in compare_reach_columns
    if "pct_diff" in c
    and "diff_2" not in c
    and "10_15" not in c
    and "diff_1_2" not in c
    and "1_10" not in c
    and "1_15" not in c
]
# %%
all_reach_columns = [compare_reach_columns]

aggregation_level = aggregation_levels[-1:]

for i, gdf in enumerate(gdfs):

    print(f"At aggregation level: {aggregation_level[i]}:")

    global_morans_results = {}

    for columns in all_reach_columns:

        fps_morans = [
            fp_spatial_auto_reach
            + f"{aggregation_level[i]}/morans_{c}.png".replace(" ", "_")
            for c in columns
        ]

        fps_lisa = [
            fp_spatial_auto_reach
            + f"{aggregation_level[i]}/lisa_{c}.png".replace(" ", "_")
            for c in columns
        ]

        morans_results = analysis_func.compute_spatial_autocorrelation(
            columns, columns, gdf, spatial_weights[i], fps_morans, show_plot=False
        )

        lisa_results = analysis_func.compute_lisa(
            columns,
            columns,
            gdf,
            spatial_weights[i],
            fps_lisa,
            show_plot=False,
        )

        for key, value in morans_results.items():
            global_morans_results[key] = value.I

    with open(
        fp_spatial_auto_reach
        + f"{aggregation_level[i]}/global_moransi_compare_reach_{spatial_weights_values[i]}.json",
        "w",
    ) as outfile:
        json.dump(global_morans_results, outfile)

    q_columns = [c for c in gdf.columns if c.endswith("_q")]
    q_columns.extend(["geometry", id_columns[2]])

    gdf[q_columns].to_parquet(
        fp_spatial_auto_reach + f"{aggregation_level[i]}/lisas_compare_reach.parquet"
    )

# %%
## Confirm spatial clustering of population density and socio-economic variables

# socio_gdf = gpd.read_postgis("SELECT * FROM socio;", engine, geom_col="geometry")

exec(open("../helper_scripts/read_socio_pop.py").read())

# org_len = len(socio_gdf)

socio.dropna(subset=["population_density"], inplace=True)

# print("Dropped rows with missing population density:", org_len - len(socio_gdf))

socio.replace(np.nan, 0, inplace=True)

w = analysis_func.spatial_weights_combined(socio, id_columns[1], k_socio)

columns = socio_corr_variables

global_morans_results = {}


fps_morans = [
    fp_spatial_auto_socio + f"morans_{c}.png".replace(" ", "_") for c in columns
]

fps_lisa = [
    fp_spatial_auto_socio + f"lisa_{c}.png".replace(" ", "_") for c in columns
]

morans_results = analysis_func.compute_spatial_autocorrelation(
    columns, columns, socio, w, fps_morans, show_plot=False
)

lisa_results = analysis_func.compute_lisa(
    columns,
    columns,
    socio,
    w,
    fps_lisa,
    show_plot=False,
)

for key, value in morans_results.items():
    global_morans_results[key] = value.I

with open(
    fp_spatial_auto_socio + f"global_moransi_queens_{k_socio}.json",
    "w",
) as outfile:
    json.dump(global_morans_results, outfile)

q_columns = [c for c in socio.columns if c.endswith("_q")]
q_columns.extend(["geometry", "id"])

socio[q_columns].to_parquet(fp_spatial_auto_socio + f"lisas.parquet")

# %%
