# %%

from src import plotting_functions as plot_func
import seaborn as sns
import pandas as pd
from matplotlib import pyplot as plt
import plotly.express as px

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/filepaths.py").read())

# %%
exec(open("../helper_scripts/read_density.py").read())

# %%

####### MAPS ##############################
###########################################

gdfs = [density_muni, density_socio, density_hex]

all_fps = all_fps_map_density

for e, gdf in enumerate(gdfs):

    ###### Plot individual LTS densities #####

    plot_columns = density_columns

    labels = labels_all

    plot_titles = labels_all
    filepaths = [all_fps[e] + l for l in labels]

    for i, p in enumerate(plot_columns):

        if p in ["lts_1_dens", "lts_2_dens"]:
            vmin, vmax = plot_func.get_min_max_vals(gdf, plot_columns[0:2])
        elif p in ["lts_3_dens", "lts_4_dens"]:
            vmin, vmax = plot_func.get_min_max_vals(gdf, plot_columns[2:4])
        elif p in ["total_car_dens", "total_network_dens"]:
            vmin, vmax = plot_func.get_min_max_vals(gdf, plot_columns[4:6])
        else:
            vmin, vmax = plot_func.get_min_max_vals(gdf, [p])

        plot_func.plot_unclassified_poly(
            poly_gdf=gdf,
            plot_col=p,
            plot_title=plot_titles[i],
            filepath=filepaths[i],
            cmap=pdict["dens"],
            edgecolor="none",
            linewidth=0,
            use_norm=True,
            norm_min=vmin,
            norm_max=vmax,
            background_color=pdict["background_color"],
        )

    ###### Plot stepwise LTS densities #####
    plot_columns = density_steps_columns[1:]

    labels = labels_step_all[1:]

    plot_titles = labels_step_all[1:]
    filepaths = [all_fps[e] + l for l in labels]

    for i, p in enumerate(plot_columns):

        if p in ["lts_1_dens", "lts_2_dens"]:
            vmin, vmax = plot_func.get_min_max_vals(gdf, plot_columns[0:2])
        elif p in ["lts_3_dens", "lts_4_dens"]:
            vmin, vmax = plot_func.get_min_max_vals(gdf, plot_columns[2:4])
        elif p in ["total_car_dens", "total_network_dens"]:
            vmin, vmax = plot_func.get_min_max_vals(gdf, plot_columns[4:6])
        else:
            vmin, vmax = plot_func.get_min_max_vals(gdf, [p])

        plot_func.plot_unclassified_poly(
            poly_gdf=gdf,
            plot_col=p,
            plot_title=plot_titles[i],
            filepath=filepaths[i],
            cmap=pdict["dens"],
            edgecolor="none",
            linewidth=0,
            use_norm=True,
            norm_min=vmin,
            norm_max=vmax,
            background_color=pdict["background_color"],
            # legend_fs=20,
        )

    ###### Plot relative network length #####
    plot_columns = length_relative_columns

    labels = labels_pct

    plot_titles = labels_all
    filepaths = [all_fps[e] + l for l in labels]

    for i, p in enumerate(plot_columns):

        vmin, vmax = plot_func.get_min_max_vals(gdf, [p])

        plot_func.plot_unclassified_poly(
            poly_gdf=gdf,
            plot_col=p,
            plot_title=plot_titles[i],
            filepath=filepaths[i],
            cmap=pdict["dens_rel"],
            edgecolor="none",
            linewidth=0,
            use_norm=True,
            norm_min=vmin,
            norm_max=vmax,
            background_color=pdict["background_color"],
        )

    ###### Plot relative network length #####
    plot_columns = length_relative_steps_columns

    convert_columns = [
        l for l in length_relative_steps_columns if l not in length_relative_columns
    ]

    labels = labels_pct_step

    plot_titles = labels_step_all
    filepaths = [all_fps[e] + l for l in labels]

    for i, p in enumerate(plot_columns):

        vmin, vmax = plot_func.get_min_max_vals(gdf, [p])

        plot_func.plot_unclassified_poly(
            poly_gdf=gdf,
            plot_col=p,
            plot_title=plot_titles[i],
            filepath=filepaths[i],
            cmap=pdict["dens_rel"],
            edgecolor="none",
            linewidth=0,
            use_norm=True,
            norm_min=vmin,
            norm_max=vmax,
            background_color=pdict["background_color"],
        )

# %%
####### PLOTS #############################
###########################################

gdfs = [density_muni, density_socio, density_hex]

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

type_columns = aggregation_levels

municipalities = density_muni.municipality.unique()
socio_ids = density_socio.id.unique()
hex_ids = density_hex.hex_id.unique()

id_lists = [municipalities, socio_ids, hex_ids]

stacked_dfs = {}

## Make stacked dfs
for e, gdf in enumerate(gdfs):

    dens_all = []
    length_all = []
    lts_all = []
    ids_all = []

    for i in id_lists[e]:
        data = gdf[gdf[id_columns[e]] == i]

        if len(data) > 0:

            dens_list = data[density_columns].values[0]
            length_list = data[length_columns].values[0]
            lts = ["1", "2", "3", "4", "car", "total"]
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

    stacked_dfs[type_columns[e]] = df


# %%
# ***** KDE PLOTS *****

filepaths_length = fps_kde_length
filepaths_density = fps_kde_density

for label, df in stacked_dfs.items():

    df.rename(columns={"lts": "Network level"}, inplace=True)

    fig = sns.kdeplot(
        data=df,
        x="length",
        hue="Network level",
        log_scale=True,
        palette=lts_color_dict.values(),
    )

    fig.set_xlabel("Length (km)")
    fig.set_title(f"Network length KDE at the {label.lower()} level")
    plt.savefig(filepaths_length[list(stacked_dfs.keys()).index(label)])

    plt.show()

    plt.close()

    fig = sns.kdeplot(
        data=df,
        x="density",
        hue="Network level",
        log_scale=True,
        palette=lts_color_dict.values(),
    )

    fig.set_xlabel("Density (km/sqkm)")
    fig.set_title(f"Network density KDE at the {label.lower()} level")
    plt.savefig(filepaths_density[list(stacked_dfs.keys()).index(label)])

    plt.show()
    plt.close

# %%
# **** BAR CHARTS - MUNI ****

dfs = [
    stacked_dfs[aggregation_levels[0]],
]

filepaths_density = fps_bar_density
filepaths_length = fps_bar_length

plotly_labels["id"] = "municipality"

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
        filepaths_length[i],
        width=2000,
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

    fig.write_image(
        filepaths_density[i],
        width=1000,
        height=750,
    )

# %%
# **** VIOLIN PLOTS ****

filepaths = fps_violin_density

for e, gdf in enumerate(gdfs):

    colors = [v for v in lts_color_dict.values()]

    for i, d in enumerate(density_columns):
        fig = px.violin(
            gdf,
            y=d,
            hover_name=id_columns[e],
            points="all",
            box=False,
            labels=plotly_labels,
            color_discrete_sequence=[colors[i]],
            title=type_columns[e],
        )
        fig.show()

        fig.write_image(
            filepaths[e] + d + ".jpg",
            width=1000,
            height=750,
        )

    for i, l in enumerate(length_columns):
        fig = px.violin(
            gdf,
            y=l,
            hover_name=id_columns[e],
            points="all",
            box=False,
            labels=plotly_labels,
            color_discrete_sequence=[colors[i]],
            title=type_columns[e],
        )
        fig.show()

        fig.write_image(
            filepaths[e] + l + ".jpg",
            width=1000,
            height=750,
        )

# %%
