# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly_express as px
import pandas as pd
import seaborn as sns

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/filepaths.py").read())
plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)


# %%
# ********** Plot total component size distributions **********

component_size_all = pd.read_sql(
    "SELECT * FROM fragmentation.component_size_all;", engine
)
component_size_1 = pd.read_sql("SELECT * FROM fragmentation.component_size_1;", engine)
component_size_2 = pd.read_sql("SELECT * FROM fragmentation.component_size_2;", engine)
component_size_3 = pd.read_sql("SELECT * FROM fragmentation.component_size_3;", engine)
component_size_4 = pd.read_sql("SELECT * FROM fragmentation.component_size_4;", engine)
component_size_car = pd.read_sql(
    "SELECT * FROM fragmentation.component_size_car;", engine
)

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
# %%
for i, df in enumerate(component_size_dfs):
    plot_func.make_zipf_component_plot(
        df,
        columns[i],
        labels[i],
        fp_zipf_lts + labels[i] + ".png",
    )

# Combined zipf plot
plot_func.combined_zipf_plot(
    component_size_all=component_size_all,
    component_size_1=component_size_1,
    component_size_2=component_size_2,
    component_size_3=component_size_3,
    component_size_4=component_size_4,
    component_size_car=component_size_car,
    lts_color_dict=lts_color_dict,
    fp=fp_zipf_combined,
)

# %%
# ************ Plot component size distribution per municipality **************************

munis = dbf.run_query_pg("SELECT DISTINCT municipality from edges;", connection)

municipalities = [m[0] for m in munis]
municipalities.remove(None)

for muni in municipalities:

    muni_edges = gpd.GeoDataFrame.from_postgis(
        f"SELECT * FROM fragmentation.component_edges WHERE municipality = '{muni}';",
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
            fp=fp_zipf_muni + muni + ".png",
            title=f"Component size distribution in {muni}",
        )

    elif len(muni_edges) == 0:
        print(f"No edges in {muni}")
        pass

# %%
# **** PLOT LOCAL COMPONENT COUNT (MAPS) ****

muni_components = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM fragmentation.comp_count_muni;",
    engine,
    crs=crs,
    geom_col="geometry",
)

muni_components.replace(0, np.nan, inplace=True)

socio_components = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM fragmentation.comp_count_socio;",
    engine,
    crs=crs,
    geom_col="geometry",
)

socio_components.replace(0, np.nan, inplace=True)

hex_components = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM fragmentation.comp_count_hex;",
    engine,
    crs=crs,
    geom_col="geometry",
)

hex_components.replace(0, np.nan, inplace=True)

gdfs = [muni_components, socio_components, hex_components]

plot_columns = component_count_columns

labels = ["LTS 1", "LTS 1-2", "LTS 1-3", "LTS 1-4", "Total car", "Total network"]

all_filepaths = filepaths_local_component_count

all_plot_titles = [
    "Municipal component count for: ",
    "Local component count for: ",
    "Hexagonal grid component count for: ",
]

for e, gdf in enumerate(gdfs):

    plot_titles = [all_plot_titles[e] + l for l in labels]
    filepaths = [all_filepaths[e] + l for l in labels]

    min_vals = [gdf[p].min() for p in plot_columns]
    max_vals = [gdf[p].max() for p in plot_columns]
    v_min = min(min_vals)
    v_max = max(max_vals)

    for i, p in enumerate(plot_columns):
        plot_func.plot_classified_poly(
            gdf=gdf,
            plot_col=p,
            scheme=scheme,
            k=k,
            cx_tile=cx_tile_2,
            plot_na=True,
            cmap=pdict["neg"],
            edgecolor="none",
            title=plot_titles[i],
            fp=filepaths[i],
        )

        plot_func.plot_unclassified_poly(
            poly_gdf=gdf,
            plot_col=p,
            plot_title=plot_titles[i],
            filepath=filepaths[i] + "_unclassified",
            cmap=pdict["neg"],
            use_norm=True,
            norm_min=v_min,
            norm_max=v_max,
            cx_tile=cx_tile_2,
        )

# %%
# ***** CORRELATION BETWEEN LOCAL COMPONENT COUNT AND NETWORK DENSITY *****

component_length_muni = pd.read_sql(
    "SELECT * FROM fragmentation.component_length_muni;", engine
)
component_length_socio = pd.read_sql(
    "SELECT * FROM fragmentation.component_length_socio;", engine
)
component_length_hex = pd.read_sql(
    "SELECT * FROM fragmentation.component_length_hex;", engine
)

dfs = [component_length_muni, component_length_socio, component_length_hex]

id_columns = [["municipality"], ["id"], ["hex_id"]]
titles = ["Municipalities", "Local", "Hexagonal grid"]

all_filepaths = filepaths_component_density_correlation
# %%
for i, df in enumerate(dfs):

    for c, d, l in zip(
        component_count_columns, density_steps_columns, length_steps_columns
    ):

        fig = px.scatter(
            df,
            x=d,
            y=c,
            color=l,
            # color_discrete_sequence=["black"],
            # color_continuous_scale=px.colors.sequential.Viridis,
            hover_data=id_columns[i],
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
            title=titles[i],
        )

        fig.write_image(
            all_filepaths[i] + "_".join([c, d]) + ".jpeg",
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

        dens_list = data[density_steps_columns].values[0]
        comp_list = data[component_count_columns].values[0]
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
# SCATTER AND RUG PLOTS FOR COMPONENT AND INFRASTRUCTURE DENSITY

dfs = [component_length_muni, component_length_socio, component_length_hex]

municipalities = component_length_muni.municipality.unique()
socio_ids = component_length_socio.id.unique()
hex_ids = component_length_hex.hex_id.unique()

id_lists = [municipalities, socio_ids, hex_ids]

id_columns = ["municipality", "id", "hex_id"]

scatter_titles = [
    "Municipal component count and infrastructure density",
    "Local component count and infrastructure density",
    "Hexagonal grid component count and infrastructure density",
]

rug_titles = [
    "Distribution of local component count at the municipal level",
    "Distribution of local component count at the local level",
    "Distribution of local component count at the hexagonal grid level",
]
scatter_filepaths = filepaths_components_scatter
rug_filepaths = filepaths_components_rug

for e, df in enumerate(dfs):

    dens_all = []
    comp_all = []
    lts_all = []
    ids_all = []

    for i in id_lists[e]:

        data = df[df[id_columns[e]] == i]

        if len(data) > 0:

            dens_list = data[density_steps_columns].values[0]
            comp_list = data[component_count_columns].values[0]
            lts = ["1", "1_2", "1_3", "1_4", "car", "all"]
            ids = [i] * 6

            dens_all.extend(dens_list)
            comp_all.extend(comp_list)
            lts_all.extend(lts)
            ids_all.extend(ids)

    df = pd.DataFrame(
        {
            "density": dens_all,
            "component_count": comp_all,
            "lts": lts_all,
            "id": ids_all,
        }
    )

    fig = px.scatter(
        df,
        x="density",
        y="component_count",
        color="lts",
        color_discrete_sequence=[v for v in lts_color_dict.values()],
        # color_continuous_scale=px.colors.sequential.Viridis,
        hover_data="id",
        opacity=0.6,
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
        title=scatter_titles[e],
    )

    fig.write_image(
        scatter_filepaths[e],
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
        hover_data="id",
        # text_auto=True,
        marginal="rug",
        color_discrete_sequence=[v for v in lts_color_dict.values()],
        title=rug_titles[e],
    )
    fig.update_layout(
        font=dict(size=12, color="black"),
        autosize=False,
        width=800,
        height=600,
        yaxis_title="Count",
    )
    fig.write_image(
        rug_filepaths[e],
        width=1000,
        height=750,
    )

    fig.show()

# %%

# Corr between component count and density for each step of LTS

df_1 = df.loc[df["lts"] == "1"]
df_2 = df.loc[df["lts"] == "1_2"]
df_3 = df.loc[df["lts"] == "1_3"]
df_4 = df.loc[df["lts"] == "1_4"]
df_car = df.loc[df["lts"] == "car"]
df_all = df.loc[df["lts"] == "all"]

dfs = [df_1, df_2, df_3, df_4, df_car, df_all]

scatter_filepaths_subsets = filepaths_components_scatter_lts

for i, df_subset in enumerate(dfs):

    fig = px.scatter(
        df_subset,
        x="density",
        y="component_count",
        color="lts",
        color_discrete_sequence=[v for v in lts_color_dict.values()],
        # color_continuous_scale=px.colors.sequential.Viridis,
        hover_data="id",
        opacity=0.4,
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
        title=scatter_titles[e],
    )

    fig.write_image(
        scatter_filepaths_subsets[i],
        width=1000,
        height=750,
    )
    fig.show()

# %%
# **** PLOT COMPONENTS PER LENGTH AND DENSITY ****

muni_components = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM fragmentation.component_length_muni;",
    engine,
    crs=crs,
    geom_col="geometry",
)

muni_components.replace(0, np.nan, inplace=True)

socio_components = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM fragmentation.component_length_socio;",
    engine,
    crs=crs,
    geom_col="geometry",
)

socio_components.replace(0, np.nan, inplace=True)

hex_components = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM fragmentation.component_length_hex;",
    engine,
    crs=crs,
    geom_col="geometry",
)

hex_components.replace(0, np.nan, inplace=True)

gdfs = [muni_components, socio_components, hex_components]

# %%
# comp per km
plot_columns = component_per_km_columns

labels = ["LTS 1", "LTS 1-2", "LTS 1-3", "LTS 1-4", "Total car", "Total network"]

all_filepaths = filepaths_local_component_count

all_plot_titles = [
    "Municipal component count per km for: ",
    "Local component count per km for: ",
    "Hexagonal grid component count per km for: ",
]

for e, gdf in enumerate(gdfs):

    plot_titles = [all_plot_titles[e] + l for l in labels]
    filepaths = [all_filepaths[e] + l + "_per_km" for l in labels]

    min_vals = [gdf[p].min() for p in plot_columns]
    max_vals = [gdf[p].max() for p in plot_columns]
    v_min = min(min_vals)
    v_max = max(max_vals)

    for i, p in enumerate(plot_columns):
        plot_func.plot_classified_poly(
            gdf=gdf,
            plot_col=p,
            scheme=scheme,
            k=k,
            cx_tile=cx_tile_2,
            plot_na=True,
            cmap=pdict["neg"],
            edgecolor="none",
            title=plot_titles[i],
            fp=filepaths[i],
        )

        plot_func.plot_unclassified_poly(
            poly_gdf=gdf,
            plot_col=p,
            plot_title=plot_titles[i],
            filepath=filepaths[i] + "_unclassified",
            cmap=pdict["neg"],
            use_norm=True,
            norm_min=v_min,
            norm_max=v_max,
            cx_tile=cx_tile_2,
        )


# %%
# comp per km sqkm
all_plot_titles = [
    "Municipal component count per km/sqkm for: ",
    "Local component count per km/sqkm for: ",
    "Hexagonal grid component count per km/sqkm for: ",
]

plot_columns = component_per_km_sqkm_columns

for e, gdf in enumerate(gdfs):

    plot_titles = [all_plot_titles[e] + l for l in labels]
    filepaths = [all_filepaths[e] + l + "_per_km_sqkm" for l in labels]

    min_vals = [gdf[p].min() for p in plot_columns]
    max_vals = [gdf[p].max() for p in plot_columns]
    v_min = min(min_vals)
    v_max = max(max_vals)

    for i, p in enumerate(plot_columns):
        plot_func.plot_classified_poly(
            gdf=gdf,
            plot_col=p,
            scheme=scheme,
            k=k,
            cx_tile=cx_tile_2,
            plot_na=True,
            cmap=pdict["neg"],
            edgecolor="none",
            title=plot_titles[i],
            fp=filepaths[i],
        )

        plot_func.plot_unclassified_poly(
            poly_gdf=gdf,
            plot_col=p,
            plot_title=plot_titles[i],
            filepath=filepaths[i] + "_unclassified",
            cmap=pdict["neg"],
            use_norm=True,
            norm_min=v_min,
            norm_max=v_max,
            cx_tile=cx_tile_2,
        )

# %%

# ****** MAPS OF LARGEST COMPONENTS *******

hex_gdf = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM fragmentation.hex_largest_components;",
    engine,
    crs=crs,
    geom_col="geometry",
)

hex_gdf[largest_local_component_len_columns] = hex_gdf[
    largest_local_component_len_columns
].replace(np.nan, 0)

hex_gdf[largest_local_component_area_columns] = hex_gdf[
    largest_local_component_area_columns
].replace(np.nan, 0)


# %%
plot_columns = largest_local_component_len_columns

plot_titles = [
    "Largest component length for network LTS 1",
    "Largest component length for network LTS 2",
    "Largest component length for network LTS 3",
    "Largest component length for network LTS 4",
    "Largest component length for car network",
]

labels = [
    "LTS 1",
    "LTS 1-2",
    "LTS 1-3",
    "LTS 1-4",
    "Total car",
]
filepaths = [
    "../results/component_size_maps/largest_component_length_" + l for l in labels
]

min_vals = [hex_gdf[p].min() for p in plot_columns]
max_vals = [hex_gdf[p].max() for p in plot_columns]
v_min = min(min_vals)
v_max = max(max_vals)

for i, p in enumerate(plot_columns):

    k_check = plot_func.get_unique_bins(hex_gdf, p, scheme, k)

    try:
        plot_func.plot_classified_poly(
            gdf=hex_gdf,
            plot_col=p,
            scheme=scheme,
            k=k_check,
            cx_tile=cx_tile_2,
            plot_na=True,
            cmap=pdict["pos"],
            edgecolor="none",
            title=plot_titles[i],
            fp=filepaths[i],
        )
    except ValueError:

        k_check -= 1

        plot_func.plot_classified_poly(
            gdf=hex_gdf,
            plot_col=p,
            scheme=scheme,
            k=k_check,
            cx_tile=cx_tile_2,
            plot_na=True,
            cmap=pdict["pos"],
            edgecolor="none",
            title=plot_titles[i],
            fp=filepaths[i],
        )

    plot_func.plot_unclassified_poly(
        poly_gdf=hex_gdf,
        plot_col=p,
        plot_title=plot_titles[i],
        filepath=filepaths[i] + "_unclassified",
        cmap=pdict["pos"],
        use_norm=True,
        norm_min=v_min,
        norm_max=v_max,
        cx_tile=cx_tile_2,
    )

# %%
plot_columns = largest_local_component_area_columns

plot_titles = [
    "Largest component area for network LTS 1",
    "Largest component area for network LTS 2",
    "Largest component area for network LTS 3",
    "Largest component area for network LTS 4",
    "Largest component area for car network",
]

labels = [
    "LTS 1",
    "LTS 1-2",
    "LTS 1-3",
    "LTS 1-4",
    "Total car",
]
filepaths = [
    "../results/component_size_maps/largest_component_area_" + l for l in labels
]


min_vals = [hex_gdf[p].min() for p in plot_columns]
max_vals = [hex_gdf[p].max() for p in plot_columns]
v_min = min(min_vals)
v_max = max(max_vals)


for i, p in enumerate(plot_columns):

    k_check = plot_func.get_unique_bins(hex_gdf, p, scheme, k)

    try:
        plot_func.plot_classified_poly(
            gdf=hex_gdf,
            plot_col=p,
            scheme=scheme,
            k=k_check,
            cx_tile=cx_tile_2,
            plot_na=True,
            cmap=pdict["pos"],
            edgecolor="none",
            title=plot_titles[i],
            fp=filepaths[i],
        )
    except ValueError:

        k_check -= 1

    plot_func.plot_unclassified_poly(
        poly_gdf=hex_gdf,
        plot_col=p,
        plot_title=plot_titles[i],
        filepath=filepaths[i] + "_unclassified",
        cmap=pdict["pos"],
        use_norm=True,
        norm_min=v_min,
        norm_max=v_max,
        cx_tile=cx_tile_2,
    )


# %%
# *** Correlation between hex largest component length and area ***

labels = ["LTS 1", "LTS 1-2", "LTS 1-3", "LTS 1-4", "Total car"]

colors = [v for v in lts_color_dict.values()]

for i in range(len(labels)):
    fig = px.scatter(
        hex_gdf,
        x=largest_local_component_len_columns[i],
        y=largest_local_component_area_columns[i],
        hover_data="hex_id",
        color_discrete_sequence=[colors[i]],
        opacity=0.6,
        labels=plotly_labels,
        log_x=True,
        log_y=True,
    )

    fig.update_layout(
        font=dict(size=12, color="black"),
        autosize=False,
        width=800,
        height=600,
        yaxis_title="Area",
        xaxis_title="Length",
        title="Correlation between largest component length and area for: " + labels[i],
    )

    fig.write_image(
        f"../results/component_len_area_correlation/{labels[i]}.jpg",
        width=1000,
        height=750,
    )
    fig.show()
# %%

# **** KDES OF LARGEST COMPONENT DISTRIBUTIONS

df = hex_gdf[largest_local_component_len_columns].melt()

df.rename(columns={"variable": "Network level", "value": "length"}, inplace=True)

df.replace(
    {
        "component_length_1": "LTS 1",
        "component_length_2": "LTS 2",
        "component_length_3": "LTS 3",
        "component_length_4": "LTS 4",
        "component_length_car": "Car network",
    },
    inplace=True,
)
fig = sns.kdeplot(
    data=df,
    x="length",
    hue="Network level",
    palette=lts_color_dict.values(),
)

fig.set_xlabel("Length")
fig.set_title(f"Length of the largest component in each hexagon")
plt.savefig("../results/component_size_distribution/largest_component_length_kde.png")

plt.show()

plt.close()
# %%
