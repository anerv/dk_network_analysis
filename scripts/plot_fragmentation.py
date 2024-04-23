# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly_express as px

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)


# %%
# Plot total component size distributions
component_size_all = pd.read_sql("SELECT * FROM component_size_all;", engine)
component_size_1 = pd.read_sql("SELECT * FROM component_size_1;", engine)
component_size_2 = pd.read_sql("SELECT * FROM component_size_2;", engine)
component_size_3 = pd.read_sql("SELECT * FROM component_size_3;", engine)
component_size_4 = pd.read_sql("SELECT * FROM component_size_4;", engine)
component_size_car = pd.read_sql("SELECT * FROM component_size_car;", engine)

component_size_dfs = [
    component_size_all,
    component_size_1,
    component_size_2,
    component_size_3,
    component_size_4,
    component_size_car,
]

labels = [
    "total network",
    "LTS 1 network",
    "LTS 2 network",
    "LTS 3 network",
    "LTS 4 network",
    "total car network",
]
columns = ["bike_length"] * 5 + ["geom_length"]

for i, df in enumerate(component_size_dfs):
    plot_func.make_zipf_component_plot(
        df,
        columns[i],
        labels[i],
        f"../results/component_size_distribution/{labels[i]}_zipf.png",
    )

# %%
plot_func.combined_zipf_plot(
    component_size_all=component_size_all,
    component_size_1=component_size_1,
    component_size_2=component_size_2,
    component_size_3=component_size_3,
    component_size_4=component_size_4,
    component_size_car=component_size_car,
    lts_color_dict=lts_color_dict,
    fp="../results/component_size_distribution/combined_zipf.png",
)

# %%
# Plot component size distribution per municipality

munis = dbf.run_query_pg("SELECT DISTINCT municipality from edges;", connection)

municipalities = [m[0] for m in munis]
municipalities.remove(None)

component_columns = [
    "component_all",
    "component_1",
    "component_1_2",
    "component_1_3",
    "component_1_4",
    "component_car",
]

success = []
for muni in municipalities:

    muni_edges = gpd.GeoDataFrame.from_postgis(
        f"SELECT * FROM component_edges WHERE municipality = '{muni}';",
        engine,
        crs=crs,
        geom_col="geometry",
    )

    muni_edges.loc[muni_edges.bike_length.isna(), "bike_length"] = (
        muni_edges.geometry.length
    )
    muni_edges["bike_length"] = muni_edges["bike_length"] / 1000
    muni_edges["geom_length"] = muni_edges.geometry.length / 1000

    if len(muni_edges) > 0:
        component_size_all = (
            muni_edges[muni_edges["component_all"].notna()]
            .groupby("component_all")
            .sum("bike_length")
        )
        component_size_1 = (
            muni_edges[muni_edges["component_1"].notna()]
            .groupby("component_1")
            .sum("bike_length")
        )
        component_size_2 = (
            muni_edges[muni_edges["component_1_2"].notna()]
            .groupby("component_1_2")
            .sum("bike_length")
        )
        component_size_3 = (
            muni_edges[muni_edges["component_1_3"].notna()]
            .groupby("component_1_3")
            .sum("bike_length")
        )
        component_size_4 = (
            muni_edges[muni_edges["component_1_4"].notna()]
            .groupby("component_1_4")
            .sum("bike_length")
        )
        component_size_car = (
            muni_edges[muni_edges["component_car"].notna()]
            .groupby("component_car")
            .sum("geom_length")
        )

        plot_func.combined_zipf_plot(
            component_size_all=component_size_all,
            component_size_1=component_size_1,
            component_size_2=component_size_2,
            component_size_3=component_size_3,
            component_size_4=component_size_4,
            component_size_car=component_size_car,
            lts_color_dict=lts_color_dict,
            fp=f"../results/component_size_distribution/administrative/combined_zipf_{muni}.png",
            title=f"Component size distribution in {muni}",
        )

        success.append(muni)

    elif len(muni_edges) == 0:
        print(f"No edges in {muni}")
        pass

# %%
# **** PLOT LOCAL COMPONENT COUNT ****

# Municipalities

muni_components = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM comp_count_muni;",
    engine,
    crs=crs,
    geom_col="geometry",
)

muni_components.replace(0, np.nan, inplace=True)

plot_cols = [
    "comp_1_count",
    "comp_2_count",
    "comp_3_count",
    "comp_4_count",
    "comp_car_count",
    "comp_all_count",
]
labels = ["LTS 1", "LTS 1-2", "LTS 1-3", "LTS 1-4", "Total car", "Total network"]
plot_titles = [f"Municipal component count for: {l}" for l in labels]
filepaths = [f"../results/component_count/administrative/{l}" for l in labels]

for i, p in enumerate(plot_cols):

    plot_func.plot_classified_poly(
        gdf=muni_components,
        plot_col=p,
        scheme="quantiles",
        cx_tile=cx_tile_2,
        plot_na=True,
        cmap=pdict["neg"],
        edgecolor="none",
        title=plot_titles[i],
        fp=filepaths[i],
    )


# %%
# Socio-economic areas
socio_components = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM comp_count_socio;",
    engine,
    crs=crs,
    geom_col="geometry",
)

socio_components.replace(0, np.nan, inplace=True)

plot_cols = [
    "comp_1_count",
    "comp_2_count",
    "comp_3_count",
    "comp_4_count",
    "comp_car_count",
    "comp_all_count",
]
labels = ["LTS 1", "LTS 1-2", "LTS 1-3", "LTS 1-4", "Total car", "Total network"]
plot_titles = [f"Local component count for: {l}" for l in labels]
filepaths = [f"../results/component_count/socio/{l}" for l in labels]

for i, p in enumerate(plot_cols):

    plot_func.plot_classified_poly(
        gdf=socio_components,
        plot_col=p,
        scheme="quantiles",
        cx_tile=cx_tile_2,
        plot_na=True,
        cmap=pdict["neg"],
        edgecolor="none",
        title=plot_titles[i],
        fp=filepaths[i],
    )


# %%
# H3
h3_components = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM comp_count_h3;",
    engine,
    crs=crs,
    geom_col="geometry",
)

h3_components.replace(0, np.nan, inplace=True)

plot_cols = [
    "comp_1_count",
    "comp_2_count",
    "comp_3_count",
    "comp_4_count",
    "comp_car_count",
    "comp_all_count",
]
labels = ["LTS 1", "LTS 1-2", "LTS 1-3", "LTS 1-4", "Total car", "Total network"]
plot_titles = [f"H3 component count for: {l}" for l in labels]
filepaths = [f"../results/component_count/h3/{l}" for l in labels]

for i, p in enumerate(plot_cols):

    plot_func.plot_classified_poly(
        gdf=h3_components,
        plot_col=p,
        scheme="quantiles",
        cx_tile=cx_tile_2,
        plot_na=True,
        cmap=pdict["neg"],
        edgecolor="none",
        linewidth=0.0,
        title=plot_titles[i],
        fp=filepaths[i],
    )

# %%
# ***** CORRELATION BETWEEN LOCAL COMPONENT COUNT AND NETWORK DENSITY *****
component_length_muni = pd.read_sql("SELECT * FROM component_length_muni;", engine)
component_length_socio = pd.read_sql("SELECT * FROM component_length_socio;", engine)
component_length_h3 = pd.read_sql("SELECT * FROM component_length_h3;", engine)

component_cols = [
    "comp_1_count",
    "comp_2_count",
    "comp_3_count",
    "comp_4_count",
    "comp_car_count",
    "comp_all_count",
]

length_cols = [
    "lts_1_length",
    "lts_1_2_length",
    "lts_1_3_length",
    "lts_1_4_length",
    "total_car_length",
    "total_network_length",
]

density_cols = [
    "lts_1_dens",
    "lts_1_2_dens",
    "lts_1_3_dens",
    "lts_1_4_dens",
    "total_car_dens",
    "total_network_dens",
]

dfs = [component_length_muni, component_length_socio, component_length_h3]

for df in dfs:
    df["lts_1_2_length"] = df.lts_1_length + df.lts_2_length
    df["lts_1_3_length"] = df.lts_1_length + df.lts_2_length + df.lts_3_length
    df["lts_1_4_length"] = (
        df.lts_1_length + df.lts_2_length + df.lts_3_length + df.lts_4_length
    )

# %%

# MUNICIPALITIES

for c, d, l in zip(component_cols, density_cols, length_cols):

    fig = px.scatter(
        component_length_muni,
        x=d,
        y=c,
        color=l,
        # color_discrete_sequence=["black"],
        # color_continuous_scale=px.colors.sequential.Viridis,
        hover_data=["municipality"],
        opacity=0.5,
        labels=plotly_labels,
        log_x=True,
        log_y=True,
    )

    fig.update_layout(
        font=dict(size=12, color="black"),
        autosize=False,
        width=800,
        height=600,
        yaxis_title="Component count",
        title=f"Municipalities",
    )

    fig.write_image(
        f"../results/component_correlation/administrative/component_count_infra_density_{c}_{d}.jpeg",
        width=1000,
        height=750,
    )
    fig.show()

# %%
# SOCIO-ECONOMIC AREAS
for c, d, l in zip(component_cols, density_cols, length_cols):

    fig = px.scatter(
        component_length_socio,
        x=d,
        y=c,
        color=l,
        # color_discrete_sequence=["black"],
        # color_continuous_scale=px.colors.sequential.Viridis,
        # hover_data=["municipality"],
        opacity=0.5,
        labels=plotly_labels,
        log_x=True,
        log_y=True,
    )

    fig.update_layout(
        font=dict(size=12, color="black"),
        autosize=False,
        width=800,
        height=600,
        yaxis_title="Component count",
        title=f"Socio-economic areas",
    )

    fig.write_image(
        f"../results/component_correlation/socio/component_count_infra_density_{c}_{d}.jpeg",
        width=1000,
        height=750,
    )
    fig.show()

# %%
# H3 GRID
for c, d, l in zip(component_cols, density_cols, length_cols):

    fig = px.scatter(
        component_length_h3,
        x=d,
        y=c,
        color=l,
        # color_discrete_sequence=["black"],
        # color_continuous_scale=px.colors.sequential.Viridis,
        # hover_data=["municipality"],
        opacity=0.5,
        labels=plotly_labels,
        # log_x=True,
        # log_y=True,
    )

    fig.update_layout(
        font=dict(size=12, color="black"),
        autosize=False,
        width=800,
        height=600,
        yaxis_title="Component count",
        title=f"Hexagonal grid",
    )

    fig.write_image(
        f"../results/component_correlation/h3/component_count_infra_density_{c}_{d}.jpeg",
        width=1000,
        height=750,
    )
    fig.show()

# %%
# **** FOR EACH MUNICIPALITY ****
munis = dbf.run_query_pg("SELECT DISTINCT municipality from edges;", connection)

municipalities = [m[0] for m in munis]
municipalities.remove(None)

for m in municipalities:
    data = component_length_muni[component_length_muni.municipality == m]

    if len(data) > 0:

        dens_list = data[density_cols].values[0]
        comp_list = data[component_cols].values[0]
        lts = ["1", "1_2", "1_3", "1_4", "car", "all"]

        df = pd.DataFrame(
            {"density": dens_list, "component_count": comp_list, "lts": lts}
        )

        fig = px.scatter(
            df,
            x="density",
            y="component_count",
            color="lts",
            # color_discrete_sequence=["black"],
            # color_continuous_scale=px.colors.sequential.Viridis,
            hover_data="lts",
            opacity=0.8,
            labels=plotly_labels,
            # log_x=True,
            # log_y=True,
        )

        fig.update_layout(
            font=dict(size=12, color="black"),
            autosize=False,
            width=800,
            height=600,
            yaxis_title="Component count",
            title=f"Municipality: {m}",
        )

        # fig.write_image(
        #     f"../results/component_correlation/administrative/component_count_infra_density_{m}.jpeg",
        #     width=1000,
        #     height=750,
        # )
    fig.show()

# %%
# ALL MUNICIPALITIES

dens_all = []
comp_all = []
lts_all = []
munis_all = []

for m in municipalities:
    data = component_length_muni[component_length_muni.municipality == m]

    if len(data) > 0:

        dens_list = data[density_cols].values[0]
        comp_list = data[component_cols].values[0]
        lts = ["1", "1_2", "1_3", "1_4", "car", "all"]
        munis = [m] * 6

        dens_all.extend(dens_list)
        comp_all.extend(comp_list)
        lts_all.extend(lts)
        munis_all.extend(munis)

df = pd.DataFrame(
    {
        "density": dens_all,
        "component_count": comp_all,
        "lts": lts_all,
        "municipality": munis_all,
    }
)

fig = px.scatter(
    df,
    x="density",
    y="component_count",
    color="lts",
    color_discrete_sequence=[v for v in lts_color_dict.values()],
    # color_continuous_scale=px.colors.sequential.Viridis,
    hover_data="municipality",
    opacity=0.8,
    labels=plotly_labels,
    log_x=True,
    log_y=True,
)

fig.update_layout(
    font=dict(size=12, color="black"),
    autosize=False,
    width=800,
    height=600,
    yaxis_title="Component count",
    title=f"Municipal component count and infrastructure density",
)

fig.write_image(
    f"../results/component_correlation/administrative/component_count_infra_density_all_areas.jpeg",
    width=1000,
    height=750,
)
fig.show()

fig = px.histogram(
    df,
    x="component_count",
    color="lts",
    labels=plotly_labels,
    nbins=18,
    opacity=[0.8],
    hover_data=["municipality"],
    # text_auto=True,
    marginal="rug",
    color_discrete_sequence=[v for v in lts_color_dict.values()],
    # title="Distribution of local component count in OSM and GeoDanmark data",
)
fig.update_layout(
    font=dict(size=12, color="black"),
    autosize=False,
    width=800,
    height=600,
    yaxis_title="Count",
)
fig.write_image(
    f"../results/component_correlation/administrative/component_distribution_muni.jpeg",
    width=1000,
    height=750,
)

fig.show()


# %%
# ALL SOCIO

socio_id = dbf.run_query_pg(
    "SELECT DISTINCT id from component_length_socio", connection
)

socio_id = [s[0] for s in socio_id]

dens_all = []
comp_all = []
lts_all = []
socio_all = []

for s in socio_id:
    data = component_length_socio[component_length_socio.id == s]

    if len(data) > 0:

        dens_list = data[density_cols].values[0]
        comp_list = data[component_cols].values[0]
        lts = ["1", "1_2", "1_3", "1_4", "car", "all"]
        socio_id = [s] * 6

        dens_all.extend(dens_list)
        comp_all.extend(comp_list)
        lts_all.extend(lts)
        socio_all.extend(socio_id)

df = pd.DataFrame(
    {
        "density": dens_all,
        "component_count": comp_all,
        "lts": lts_all,
        "area": socio_all,
    }
)

fig = px.scatter(
    df,
    x="density",
    y="component_count",
    color="lts",
    color_discrete_sequence=[v for v in lts_color_dict.values()],
    # color_continuous_scale=px.colors.sequential.Viridis,
    hover_data="area",
    opacity=0.8,
    labels=plotly_labels,
    log_x=True,
    log_y=True,
)

fig.update_layout(
    font=dict(size=12, color="black"),
    autosize=False,
    width=800,
    height=600,
    yaxis_title="Component count",
    title=f"Local component count and infrastructure density",
)

fig.write_image(
    f"../results/component_correlation/socio/component_count_infra_density_all_socio.jpeg",
    width=1000,
    height=750,
)
fig.show()


fig = px.histogram(
    df,
    x="component_count",
    color="lts",
    labels=plotly_labels,
    nbins=18,
    opacity=[0.8],
    hover_data=["area"],
    # text_auto=True,
    marginal="rug",
    color_discrete_sequence=[v for v in lts_color_dict.values()],
    # title="Distribution of local component count in OSM and GeoDanmark data",
)
fig.update_layout(
    font=dict(size=12, color="black"),
    autosize=False,
    width=800,
    height=600,
    yaxis_title="Count",
)
fig.write_image(
    f"../results/component_correlation/socio/component_distribution_socio.jpeg",
    width=1000,
    height=750,
)

fig.show()

# %%
# ALL H3

all_hex_ids = dbf.run_query_pg(
    "SELECT DISTINCT hex_id from component_length_h3", connection
)

all_hex_ids = [h[0] for h in all_hex_ids]
# %%
dens_all = []
comp_all = []
lts_all = []
hex_all = []

for h in all_hex_ids:
    data = component_length_h3[component_length_h3.hex_id == h]

    if len(data) > 0:

        dens_list = data[density_cols].values[0]
        comp_list = data[component_cols].values[0]
        lts = ["1", "1_2", "1_3", "1_4", "car", "all"]
        hex_ids = [s] * 6

        dens_all.extend(dens_list)
        comp_all.extend(comp_list)
        lts_all.extend(lts)
        hex_all.extend(hex_ids)

df = pd.DataFrame(
    {
        "density": dens_all,
        "component_count": comp_all,
        "lts": lts_all,
        "hex_id": hex_all,
    }
)
# %%

fig = px.scatter(
    df,
    x="density",
    y="component_count",
    color="lts",
    color_discrete_sequence=[v for v in lts_color_dict.values()],
    # color_continuous_scale=px.colors.sequential.Viridis,
    hover_data="area",
    opacity=0.8,
    labels=plotly_labels,
    log_x=True,
    log_y=True,
)

fig.update_layout(
    font=dict(size=12, color="black"),
    autosize=False,
    width=800,
    height=600,
    yaxis_title="Component count",
    title=f"Local component count and infrastructure density",
)

fig.write_image(
    f"../results/component_correlation/h3/component_count_infra_density_all_hex.jpeg",
    width=1000,
    height=750,
)
fig.show()


fig = px.histogram(
    df,
    x="component_count",
    color="lts",
    labels=plotly_labels,
    nbins=18,
    opacity=[0.8],
    hover_data=["hex_id"],
    # text_auto=True,
    marginal="rug",
    color_discrete_sequence=[v for v in lts_color_dict.values()],
    # title="Distribution of local component count in OSM and GeoDanmark data",
)
fig.update_layout(
    font=dict(size=12, color="black"),
    autosize=False,
    width=800,
    height=600,
    yaxis_title="Count",
)
fig.write_image(
    f"../results/component_correlation/h3/component_distribution_h3.jpeg",
    width=1000,
    height=750,
)

fig.show()
