# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
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
############# COMPONENT SIZE DISTRIBUTION #############

# **** Plot total component size distributions *****

exec(open("../helper_scripts/read_component_sizes.py").read())

component_size_dfs = [
    component_size_1,
    component_size_1_2,
    component_size_1_3,
    component_size_1_4,
    component_size_car,
    component_size_all,
]

labels = labels_step_all

columns = ["infra_length"] * 6

# %%
# Combined zipf plot
plot_func.combined_zipf_plot(
    component_size_all=component_size_all,
    component_size_1=component_size_1,
    component_size_1_2=component_size_1_2,
    component_size_1_3=component_size_1_3,
    component_size_1_4=component_size_1_4,
    component_size_car=component_size_car,
    lts_color_dict=lts_color_dict,
    fp=fp_zipf_combined,
    figsize=pdict["fsbar"],
    fs_increase=4,
)

# %%
# **** Plot component size distribution per municipality *******

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

    muni_edges["infra_length_km"] = muni_edges.geometry.length / 1000

    if len(muni_edges) > 0:
        component_size_all = (
            muni_edges[muni_edges["component_all"].notna()]
            .groupby("component_all")
            .sum("infra_length")
        )
        component_size_1 = (
            muni_edges[muni_edges["component_1"].notna()]
            .groupby("component_1")
            .sum("infra_length")
        )
        component_size_1_2 = (
            muni_edges[muni_edges["component_1_2"].notna()]
            .groupby("component_1_2")
            .sum("infra_length")
        )
        (component_size_1_3) = (
            muni_edges[muni_edges["component_1_3"].notna()]
            .groupby("component_1_3")
            .sum("infra_length")
        )
        (component_size_1_4) = (
            muni_edges[muni_edges["component_1_4"].notna()]
            .groupby("component_1_4")
            .sum("infra_length")
        )
        component_size_car = (
            muni_edges[muni_edges["component_car"].notna()]
            .groupby("component_car")
            .sum("infra_length")
        )

        plot_func.combined_zipf_plot(
            component_size_all=component_size_all,
            component_size_1=component_size_1,
            component_size_1_2=component_size_1_2,
            component_size_1_3=component_size_1_3,
            component_size_1_4=component_size_1_4,
            component_size_car=component_size_car,
            lts_color_dict=lts_color_dict,
            fp=fp_zipf_muni + muni + ".png",
            title=f"Component size distribution in {muni}",
        )

    elif len(muni_edges) == 0:
        print(f"No edges in {muni}")
        pass

# %%
########### MAPS ############

# **** PLOT LOCAL COMPONENT COUNT (MAPS) ****

exec(open("../helper_scripts/read_components.py").read())

gdfs = [muni_components, socio_components, hex_components]

plot_columns = component_count_columns

labels = labels_step_all

all_fps = filepaths_local_component_count

all_plot_titles = [
    "Municipal component count for: ",
    "Local component count for: ",
    "Hexagonal grid component count for: ",
]

for e, gdf in enumerate(gdfs):

    plot_titles = [all_plot_titles[e] + l for l in labels]
    filepaths = [all_fps[e] + l for l in labels]

    for i, p in enumerate(plot_columns):

        vmin, vmax = plot_func.get_min_max_vals(gdf, [p])

        plot_func.plot_unclassified_poly(
            poly_gdf=gdf,
            plot_col=p,
            plot_title=plot_titles[i],
            filepath=filepaths[i] + "_unclassified",
            cmap=pdict["frag"],
            use_norm=True,
            norm_min=vmin,
            norm_max=vmax,
            # cx_tile=cx_tile_2,
            background_color=pdict["background_color"],
        )

# %%
# **** MAPS: PLOT COMPONENTS PER LENGTH AND DENSITY ****

exec(open("../helper_scripts/read_component_length_agg.py").read())

gdfs = [component_length_muni, component_length_socio, component_length_hex]

# comp per km
plot_columns = component_per_km_columns

labels = labels_step_all

all_fps = fps_local_component_count

all_plot_titles = [
    "Municipal component count per km for: ",
    "Local component count per km for: ",
    "Hexagonal grid component count per km for: ",
]

for e, gdf in enumerate(gdfs):

    plot_titles = [all_plot_titles[e] + l for l in labels]
    filepaths = [all_fps[e] + l + "_per_km" for l in labels]

    for i, p in enumerate(plot_columns):

        vmin, vmax = plot_func.get_min_max_vals(gdf, [p])

        plot_func.plot_unclassified_poly(
            poly_gdf=gdf,
            plot_col=p,
            plot_title=plot_titles[i],
            filepath=filepaths[i] + "_unclassified",
            cmap=pdict["frag"],
            use_norm=True,
            norm_min=vmin,
            norm_max=vmax,
            # cx_tile=cx_tile_2,
            background_color=pdict["background_color"],
        )

# comp per km sqkm
all_plot_titles = [
    "Municipal component count per km/sqkm for: ",
    "Local component count per km/sqkm for: ",
    "Hexagonal grid component count per km/sqkm for: ",
]

plot_columns = component_per_km_sqkm_columns

for e, gdf in enumerate(gdfs):

    plot_titles = [all_plot_titles[e] + l for l in labels]
    filepaths = [all_fps[e] + l + "_per_km_sqkm" for l in labels]

    # vmin, vmax = plot_func.get_min_max_vals(gdf, plot_columns)

    for i, p in enumerate(plot_columns):

        vmin, vmax = plot_func.get_min_max_vals(gdf, [p])

        plot_func.plot_unclassified_poly(
            poly_gdf=gdf,
            plot_col=p,
            plot_title=plot_titles[i],
            filepath=filepaths[i] + "_unclassified",
            cmap=pdict["frag"],
            use_norm=True,
            norm_min=vmin,
            norm_max=vmax,
            # cx_tile=cx_tile_2,
            background_color=pdict["background_color"],
        )

# %%
# ****** MAPS OF LARGEST COMPONENTS *******

exec(open("../helper_scripts/read_largest_components.py").read())
gdf = hex_largest_components

# Largest component length
plot_columns = largest_local_component_len_columns

plot_titles = labels_step

labels = labels_step
filepaths = [fp_largest_component_length + l for l in labels]

for i, p in enumerate(plot_columns):

    vmin, vmax = plot_func.get_min_max_vals(gdf, [p])

    plot_func.plot_unclassified_poly(
        poly_gdf=gdf,
        plot_col=p,
        plot_title=plot_titles[i],
        filepath=filepaths[i] + "_unclassified",
        cmap=pdict["largest_comp"],
        use_norm=True,
        norm_min=vmin,
        norm_max=vmax,
        background_color=pdict["background_color"],
    )
# %%
# Largest component area
plot_columns = largest_local_component_area_columns
plot_titles = labels_step
labels = labels_step
filepaths = [fp_largest_component_area + l for l in labels]

for i, p in enumerate(plot_columns):

    vmin, vmax = plot_func.get_min_max_vals(gdf, [p])

    plot_func.plot_unclassified_poly(
        poly_gdf=gdf,
        plot_col=p,
        plot_title=plot_titles[i],
        filepath=filepaths[i] + "_unclassified",
        cmap=pdict["largest_comp"],
        use_norm=True,
        norm_min=vmin,
        norm_max=vmax,
        background_color=pdict["background_color"],
    )

# %%
# Make zoomed component plot

component_edges = gpd.GeoDataFrame.from_postgis(
    "SELECT * FROM fragmentation.component_edges;", engine, geom_col="geometry"
)

lts_subset = component_edges[component_edges.component_1.notna()]

xmin, ymin = (639464.351371, 6120027.316230)
xmax, ymax = (699033.929025, 6173403.495114)

plot_func.plot_components_zoom(
    lts_subset,
    "component_1",
    "Set2",
    fp_components_zoom,
    xmin,
    ymin,
    xmax,
    ymax,
)

del component_edges
del lts_subset

# %%
##### CORRELATION AND DENSITY PLOTS #####

# *** Correlation between hex largest component length and area ***

exec(open("../helper_scripts/read_largest_components.py").read())

labels = labels_step

colors = [v for v in lts_color_dict.values()]

for i in range(len(labels)):
    fig = px.scatter(
        hex_largest_components,
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
        fp_correlation + f"comp_len_area_{labels[i]}.jpg",
        width=1000,
        height=750,
    )
    fig.show()

# **** KDES OF LARGEST COMPONENT DISTRIBUTIONS

df = hex_largest_components[largest_local_component_len_columns].melt()

df.rename(columns={"variable": "Network level", "value": "length"}, inplace=True)

df.replace(
    {
        "component_length_1": "LTS 1",
        "component_length_1_2": "LTS 2",
        "component_length_1_3": "LTS 3",
        "component_length_1_4": "LTS 4",
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
plt.savefig(fp_comp_length_kde)

plt.show()

plt.close()
# %%

# ***** CORRELATION BETWEEN LOCAL COMPONENT COUNT AND NETWORK DENSITY *****

exec(open("../helper_scripts/read_component_length_agg.py").read())

dfs = [component_length_muni, component_length_socio, component_length_hex]
# %%
titles = [a.capitalize() for a in aggregation_levels]

all_fps = fps_comp_dens_correlation

for i, df in enumerate(dfs):

    for c, d, l in zip(
        component_count_columns, density_steps_columns, length_steps_columns
    ):

        fig = px.scatter(
            df,
            x=d,
            y=c,
            color=l,
            hover_data=[id_columns[i]],
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
            plot_bgcolor="rgba(0, 0, 0, 0)",
            # paper_bgcolor="rgba(0, 0, 0, 0)",
        )

        fig.update_xaxes({"gridcolor": "lightgrey", "linewidth": 0.5})
        fig.update_yaxes({"gridcolor": "lightgrey", "linewidth": 0.5})

        fig.write_image(
            all_fps[i] + "_".join([c, d]) + ".jpeg",
            width=1000,
            height=750,
        )
        fig.show()

# %%
# SCATTER AND RUG PLOTS FOR COMPONENT AND INFRASTRUCTURE DENSITY

dfs = [component_length_muni, component_length_socio, component_length_hex]

municipalities = component_length_muni.municipality.unique()
socio_ids = component_length_socio.id.unique()
hex_ids = component_length_hex.hex_id.unique()

id_lists = [municipalities, socio_ids, hex_ids]

scatter_titles = [
    f"{i.capitalize()} component count and infrastructure density"
    for i in aggregation_levels
]

rug_titles = [
    f"Distribution of local component count at the {i} level"
    for i in aggregation_levels
]
scatter_filepaths = fps_components_scatter
rug_filepaths = fps_components_rug

new_dfs = []

for e, df in enumerate(dfs):

    dens_all = []
    component_all = []
    lts_all = []
    ids_all = []

    for i in id_lists[e]:

        data = df[df[id_columns[e]] == i]

        if len(data) > 0:

            dens_list = data[density_steps_columns].values[0]
            component_list = data[component_count_columns].values[0]
            lts = labels_step_all
            ids = [i] * 6

            dens_all.extend(dens_list)
            component_all.extend(component_list)
            lts_all.extend(lts)
            ids_all.extend(ids)

    new_df = pd.DataFrame(
        {
            "density": dens_all,
            "component_count": component_all,
            "lts": lts_all,
            "id": ids_all,
        }
    )

    new_dfs.append(new_df)

# %%
# scatter
for e, df in enumerate(new_dfs):

    fig = px.scatter(
        df,
        x="density",
        y="component_count",
        color="lts",
        color_discrete_sequence=[v for v in lts_color_dict.values()],
        # color_continuous_scale=px.colors.sequential.Viridis,
        hover_data="id",
        opacity=0.8,
        labels=plotly_labels,
        log_x=True,
        log_y=True,
    )

    fig.update_layout(
        font=dict(size=12, color="black"),
        autosize=False,
        yaxis_title="Component count",
        title=scatter_titles[e],
        plot_bgcolor="rgba(0, 0, 0, 0)",
        legend_title=None,
        width=500,
        height=500,
    )

    fig.update_xaxes(
        {"gridcolor": "lightgrey", "linewidth": 0.5},
        title_font={"size": 12},
    )
    fig.update_yaxes(
        {"gridcolor": "lightgrey", "linewidth": 0.5},
        title_font={"size": 12},
    )

    fig.write_image(
        scatter_filepaths[e],
    )
    fig.show()
# %%
# rug plots
for e, df in enumerate(new_dfs):

    new_df_subset = df.loc[df["component_count"] > 0]

    fig = px.histogram(
        new_df_subset,
        x="component_count",
        color="lts",
        labels=plotly_labels,
        category_orders={"lts": labels_step_all},
        nbins=40,
        opacity=[0.8],
        hover_data="id",
        # text_auto=True,
        marginal="rug",
        color_discrete_sequence=[v for v in lts_color_dict.values()],
        # title=rug_titles[e],
    )

    fig.update_layout(
        font=dict(size=pdict["fontsize"], color="black"),
        yaxis_title="Count",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        legend_title=None,
        legend=dict(yanchor="bottom", xanchor="left", y=0.1, x=0.82),
        # showlegend=False,
        autosize=False,
        width=700,
        height=500,
        margin=dict(l=50, r=50, t=20, b=50),
    )

    fig.update_xaxes(
        {"gridcolor": "lightgrey", "linewidth": 0.5},
        title_font={"size": pdict["ax_fs"]},
    )
    fig.update_yaxes(
        {"gridcolor": "lightgrey", "linewidth": 0.5},
        title_font={"size": pdict["ax_fs"]},
    )

    fig.write_image(
        rug_filepaths[e],
        format="jpg",
        scale=15,
    )

    fig.show()


# %%
