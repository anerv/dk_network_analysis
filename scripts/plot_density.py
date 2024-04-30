# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
import geopandas as gpd
import numpy as np
import seaborn as sns
import pandas as pd
from matplotlib import pyplot as plt
import plotly.express as px

sns.set_theme("paper")

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

# %%
### READ DATA ###
density_muni = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM density_municipality;",
    engine,
    crs=crs,
    geom_col="geometry",
)
density_muni.replace(0, np.nan, inplace=True)

density_socio = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM density_socio;",
    engine,
    crs=crs,
    geom_col="geometry",
)

density_socio.replace(0, np.nan, inplace=True)

density_h3 = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM density_h3;",
    engine,
    crs=crs,
    geom_col="geometry",
)

density_h3.replace(0, np.nan, inplace=True)


# %%
### COMPARE MUNICIPAL NETWORK DISTRIBUTION ####

municipalities = density_muni.municipality.unique()

for m in municipalities:
    data = density_muni[density_muni.municipality == m]

    if len(data) > 0:

        dens_list = data[density_columns].values[0]
        length_list = data[length_columns].values[0]
        lts = ["1", "2", "3", "4", "car", "all"]

        df = pd.DataFrame({"density": dens_list, "length": length_list, "lts": lts})

        plt.figure()

        fig = sns.barplot(df, x="lts", y="length").set(title=f"{m} network length")

        plt.show()

        plt.close()

for m in municipalities:
    data = density_muni[density_muni.municipality == m]

    if len(data) > 0:

        dens_list = data[density_steps_columns].values[0]
        length_list = data[length_steps_columns].values[0]
        lts = ["1", "1-2", "1-3", "1-4", "car", "all"]

        df = pd.DataFrame({"density": dens_list, "length": length_list, "lts": lts})

        plt.figure()

        fig = sns.barplot(df, x="lts", y="length").set(
            title=f"{m} network length (stepwise)"
        )

        plt.show()

        plt.close()

# %%
####### MAPS ##############################
###########################################
gdfs = [density_muni, density_socio, density_h3]

all_plot_titles = [
    "Municipal network density for: ",
    "Socio network density for: ",
    "Local network density for: ",
]
all_file_paths = [
    "../results/network_density/administrative/",
    "../results/network_density/socio/",
    "../results/network_density/h3/",
]

for e, gdf in enumerate(gdfs):

    print("At iteration: ", e)
    ###### Plot individual LTS densities #####

    plot_cols = density_columns

    labels = ["LTS 1", "LTS 2", "LTS 3", "LTS 4", "Total car", "Total network"]
    plot_titles = [all_plot_titles[e] + l for l in labels]
    filepaths = [all_file_paths[e] + l for l in labels]

    for i, p in enumerate(plot_cols):

        plot_func.plot_classified_poly(
            gdf=gdf,
            plot_col=p,
            scheme="quantiles",
            cx_tile=cx_tile_2,
            plot_na=True,
            cmap=pdict["pos"],
            edgecolor="none",
            title=plot_titles[i],
            fp=filepaths[i],
        )

    ###### Plot stepwise LTS densities #####
    plot_cols = density_steps_columns

    labels = ["LTS 1", "LTS 1-2", "LTS 1-3", "LTS 1-4", "Total car", "Total network"]
    plot_titles = [all_plot_titles[e] + l for l in labels]
    filepaths = [all_file_paths[e] + l for l in labels]

    for i, p in enumerate(plot_cols):

        plot_func.plot_classified_poly(
            gdf=gdf,
            plot_col=p,
            scheme="quantiles",
            cx_tile=cx_tile_2,
            plot_na=True,
            cmap=pdict["pos"],
            edgecolor="none",
            title=plot_titles[i],
            fp=filepaths[i],
        )

    ###### Plot relative network length #####
    plot_cols = length_relative_columns

    for p in plot_cols:
        gdf[p] = gdf[p] * 100

    labels = [
        "LTS 1 (%)",
        "LTS 1-2 (%)",
        "LTS 1-3 (%)",
        "LTS 1-4 (%)",
        "No biking (%)",
        # "Total car (%)",
    ]
    plot_titles = [all_plot_titles[e] + l for l in labels]
    filepaths = [all_file_paths[e] + l for l in labels]

    for i, p in enumerate(plot_cols):

        plot_func.plot_classified_poly(
            gdf=gdf,
            plot_col=p,
            scheme="quantiles",
            cx_tile=cx_tile_2,
            plot_na=True,
            cmap=pdict["pos"],
            edgecolor="none",
            title=plot_titles[i],
            fp=filepaths[i],
        )

# %%

####### PLOTS ##############################
###########################################

gdfs = [density_muni, density_socio, density_h3]
length_titles = [
    "Municipal network length (km)",
    "Local network length (km)",
    "Grid network length (km)",
]
density_titles = [
    "Municipal network density (km/sqkm)",
    "Local network density (km/sqkm)",
    "Grid network density (km/sqkm)",
]
id_cols = ["municipality", "id", "hex_id"]

type_cols = ["Municipal", "Local", "Grid"]

municipalities = density_muni.municipality.unique()
socio_ids = density_socio.id.unique()
h3_ids = density_h3.hex_id.unique()

id_lists = [municipalities, socio_ids, h3_ids]

filepaths_kde = [
    "../results/network_density/administrative/lts_kde.jpg",
    "../results/network_density/socio/lts_kde.jpg",
    "../results/network_density/h3/lts_kde.jpg",
]

filepaths_bar = [
    "../results/network_density/administrative/lts_stacked_bar.jpg",
    "../results/network_density/socio/lts_stacked_bar.jpg",
    "../results/network_density/h3/lts_stacked_bar.jpg",
]

filepaths_violin = [
    "../results/network_density/administrative/violin_",
    "../results/network_density/socio/violin_",
    "../results/network_density/h3/violin_",
]

stacked_dfs = {}


## Make stacked dfs
for e, gdf in enumerate(gdfs):

    dens_all = []
    length_all = []
    lts_all = []
    ids_all = []

    for i in id_lists[e]:
        data = gdf[gdf[id_cols[e]] == i]

        if len(data) > 0:

            dens_list = data[density_columns].values[0]
            length_list = data[length_columns].values[0]
            lts = ["1", "2", "3", "4", "car", "all"]
            ids = [i] * 6

            dens_all.extend(dens_list)
            length_all.extend(length_list)
            lts_all.extend(lts)
            ids_all.extend(ids)

    df = pd.DataFrame(
        {
            "density": dens_all,
            "length": length_all,
            "lts": lts_all,
            "id": ids_all,
        }
    )

    stacked_dfs[type_cols[e]] = df


# %%
# ***** KDE PLOTS *****

# cumulative=True, common_norm=False, common_grid=True,
# palette="crest", alpha=.5, linewidth=0,

for label, df in stacked_dfs.items():

    df.rename(columns={"lts": "Network level"}, inplace=True)

    fig = sns.kdeplot(
        data=df,
        x="length",
        hue="Network level",
        # multiple="stack",
        # fill=True,
        log_scale=True,
        palette=lts_color_dict.values(),
    )

    fig.set_xlabel("Length (km)")
    fig.set_title(f"Network length KDE at the {label.lower()} level")
    plt.savefig(filepaths_kde[list(stacked_dfs.keys()).index(label)])

    plt.show()

# %%
# **** BAR CHARTS ****

dfs = [
    stacked_dfs["Municipal"],
    stacked_dfs["Local"],
]  # Do not make stacked bar chart for grid cells

for i, df in enumerate(dfs):

    fig = px.bar(
        df.sort_values("length", ascending=False),
        x="id",
        y="length",
        color="Network level",
        title=length_titles[i],
        labels=plotly_labels,
        color_discrete_map=lts_color_dict,
    )

    fig.show()

    fig.write_image(
        filepaths_bar[i],
        width=1000,
        height=750,
    )

    fig = px.bar(
        df.sort_values("density", ascending=False),
        x="id",
        y="density",
        color="Network level",
        title=density_titles[i],
        labels=plotly_labels,
        color_discrete_map=lts_color_dict,
    )
    fig.show()

# %%
# **** VIOLIN PLOTS ****
for e, gdf in enumerate(gdfs):

    colors = [v for v in lts_color_dict.values()]

    for i, d in enumerate(density_columns):
        fig = px.violin(
            gdf,
            y=d,
            hover_name=id_cols[e],
            points="all",
            box=False,
            labels=plotly_labels,
            color_discrete_sequence=[colors[i]],
            title=type_cols[e],
        )
        fig.show()

        fig.write_image(
            filepaths_violin[e] + d + ".jpg",
            width=1000,
            height=750,
        )

    for i, l in enumerate(length_columns):
        fig = px.violin(
            gdf,
            y=l,
            hover_name=id_cols[e],
            points="all",
            box=False,
            labels=plotly_labels,
            color_discrete_sequence=[colors[i]],
            title=type_cols[e],
        )
        fig.show()

        fig.write_image(
            filepaths_violin[e] + d + ".jpg",
            width=1000,
            height=750,
        )
# %%
