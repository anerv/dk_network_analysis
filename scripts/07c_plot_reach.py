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
import itertools

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/filepaths.py").read())
plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

# Read data
exec(open("../helper_scripts/read_reach.py").read())

hex_reach.replace(0, np.nan, inplace=True)
# %%
####### MAPS - HEX REACH ##################
###########################################

# Absolute reach length

plot_titles = [
    f"Network reach: LTS 1 ({reach_dist})",
    f"Network reach: LTS 1-2 ({reach_dist})",
    f"Network reach: LTS 1-3 ({reach_dist})",
    f"Network reach: LTS 1-4 ({reach_dist})",
    f"Network reach: Car network ({reach_dist})",
]

plot_columns = reach_columns
filepaths = filepaths_reach

vmin, vmax = plot_func.get_min_max_vals(hex_reach, plot_columns)

for i, p in enumerate(plot_columns):

    plot_func.plot_classified_poly(
        gdf=hex_reach,
        plot_col=p,
        scheme=scheme,
        k=k,
        #cx_tile=cx_tile_2,
        plot_na=True,
        cmap=pdict["pos"],
        edgecolor="none",
        title=plot_titles[i],
        fp=filepaths[i],
        background_color=pdict["background_color"],
    )

    plot_func.plot_unclassified_poly(
        poly_gdf=hex_reach,
        plot_col=p,
        plot_title=plot_titles[i],
        filepath=filepaths[i] + "_unclassified",
        cmap=pdict["pos"],
        use_norm=True,
        norm_min=vmin,
        norm_max=vmax,
        #cx_tile=cx_tile_2,
        background_color=pdict["background_color"],
        plot_na=True,
    )

# %%

# Absolute reach differences

plot_titles = [
    f"Difference in network reach: Car VS. LTS 1 ({reach_dist})",
    f"Difference in network reach: Car VS. LTS 1-2 ({reach_dist})",
    f"Difference in network reach: Car VS. LTS 1-3 ({reach_dist})",
    f"Difference in network reach: Car VS. LTS 1-4 ({reach_dist})",
]

filepaths = filepaths_reach_diff

plot_columns = reach_diff_columns

vmin, vmax = plot_func.get_min_max_vals(hex_reach, plot_columns)

for i, p in enumerate(plot_columns):

    plot_func.plot_classified_poly(
        gdf=hex_reach,
        plot_col=p,
        scheme=scheme,
        k=k,
        #cx_tile=cx_tile_2,
        plot_na=True,
        cmap=pdict["pos"],
        edgecolor="none",
        title=plot_titles[i],
        fp=filepaths[i],
        background_color=pdict["background_color"],
    )

    plot_func.plot_unclassified_poly(
        poly_gdf=hex_reach,
        plot_col=p,
        plot_title=plot_titles[i],
        filepath=filepaths[i] + "_unclassified",
        cmap=pdict["pos"],
        use_norm=True,
        norm_min=vmin,
        norm_max=vmax,
        #cx_tile=cx_tile_2,
        background_color=pdict["background_color"],
    )

# %%

# Pct differences between LTS and car reach
plot_titles = [
    f"Difference in network reach: Car VS. LTS 1 (%) ({reach_dist})",
    f"Difference in network reach: Car VS. LTS 1-2 (%) ({reach_dist})",
    f"Difference in network reach: Car VS. LTS 1-3 (%) ({reach_dist})",
    f"Difference in network reach: Car VS. LTS 1-4 (%) ({reach_dist})",
]

filepaths = filepaths_reach_diff_pct

plot_columns = reach_diff_pct_columns

vmin, vmax = plot_func.get_min_max_vals(hex_reach, plot_columns)

for i, p in enumerate(plot_columns):

    plot_func.plot_classified_poly(
        gdf=hex_reach,
        plot_col=p,
        scheme=scheme,
        k=k,
        #cx_tile=cx_tile_2,
        plot_na=True,
        cmap=pdict["pos"],
        edgecolor="none",
        title=plot_titles[i],
        fp=filepaths[i],
        background_color=pdict["background_color"],
    )

    plot_func.plot_unclassified_poly(
        poly_gdf=hex_reach,
        plot_col=p,
        plot_title=plot_titles[i],
        filepath=filepaths[i] + "_unclassified",
        cmap=pdict["pos"],
        use_norm=True,
        norm_min=vmin,
        norm_max=vmax,
        #cx_tile=cx_tile_2,
        background_color=pdict["background_color"],
    )

#%%
#### MAPS - HEX REACH COMPARISON ##########

exec(open("../helper_scripts/read_reach_comparison.py").read())

#hex_reach_comparison.replace(np.nan, 0, inplace=True)


plot_columns = []
filepaths = []
plot_titles = []

for i, n in enumerate(network_levels_step):

    for comb in itertools.combinations(all_reach_distances, 2):

        plot_columns.append(f"{n}_pct_diff_{comb[0]}_{comb[1]}")

        plot_titles.append(f"% difference in network reach for {labels_step[i]} ({comb[0]} - {comb[1]})")

        filepaths.append(fp_reach_diff_pct + f"{network_levels_step[i]}_{comb[0]}-{comb[1]}")

vmin, vmax = plot_func.get_min_max_vals(hex_reach_comparison, plot_columns)
#%%
# Get subset
plot_columns = [c for c in plot_columns if "diff_1_5" in c or "diff_1_10" in c or "diff_1_15" in c]

plot_titles = [t for t in plot_titles if "1 - 5" in t or "1 - 10" in t or "1 - 15" in t]

filepaths = [f for f in filepaths if "1-5" in f or "1-10" in f or "1-15" in f]

assert len(plot_columns) == len(plot_titles) == len(filepaths)
#%%
for i, c in enumerate(plot_columns):
        
        plot_func.plot_classified_poly(
            gdf=hex_reach_comparison,
            plot_col=c,
            scheme=scheme,
            k=k,
            #cx_tile=cx_tile_2,
            plot_na=True,
            cmap=pdict["pos"],
            edgecolor="none",
            title=plot_titles[i],
            fp=filepaths[i],
            background_color=pdict["background_color"],
        )

        plot_func.plot_unclassified_poly(
            poly_gdf=hex_reach_comparison,
            plot_col=c,
            plot_title=plot_titles[i],
            filepath=filepaths[i] + "_unclassified",
            cmap="magma", #pdict["pos"],
            use_norm=True,
            norm_min=vmin,
            norm_max=vmax,
            #cx_tile=cx_tile_2,
            background_color=pdict["background_color"],
            plot_na=True,
        )

#%%
#### MAPS - SOCIO REACH ###################

# Read data
socio_reach = gpd.read_postgis(
    f"SELECT * FROM reach.socio_reach_{reach_dist}", engine, geom_col="geometry"
)

average_columns = [c for c in socio_reach.columns if "average" in c]
median_columns = [c for c in socio_reach.columns if "median" in c]
min_columns = [c for c in socio_reach.columns if "min" in c]
max_columns = [c for c in socio_reach.columns if "max" in c]

metrics = ["Average", "Median", "Min", "Max"]

network_levels = labels

for i, plot_columns in enumerate(
    [average_columns, median_columns, min_columns, max_columns]
):

    plot_titles = [
        f"{metrics[i]} network reach at the socio level using the {n} network"
        for n in network_levels
    ]

    filepaths = [
        fp_socio_reach + f"{metrics[i].lower()}_{n.replace(" ", "_")}" for n in network_levels
    ]

    vmin, vmax = plot_func.get_min_max_vals(socio_reach, plot_columns)


    for i, p in enumerate(plot_columns):

        plot_func.plot_classified_poly(
            gdf=socio_reach,
            plot_col=p,
            scheme=scheme,
            k=k,
            #cx_tile=cx_tile_2,
            plot_na=True,
            cmap=pdict["pos"],
            edgecolor="none",
            title=plot_titles[i],
            fp=filepaths[i],
            background_color=pdict["background_color"],
        )

        plot_func.plot_unclassified_poly(
            poly_gdf=socio_reach,
            plot_col=p,
            plot_title=plot_titles[i],
            filepath=filepaths[i] + "_unclassified",
            cmap=pdict["pos"],
            use_norm=True,
            norm_min=vmin,
            norm_max=vmax,
            #cx_tile=cx_tile_2,
            background_color=pdict["background_color"],
        )
# %%
###########################################
####### Histograms ########################
###########################################

plot_titles = [
    f"Network reach: LTS 1 ({reach_dist})",
    f"Network reach: LTS 1-2 ({reach_dist})",
    f"Network reach: LTS 1-3 ({reach_dist})",
    f"Network reach: LTS 1-4 ({reach_dist})",
    f"Network reach: Car network ({reach_dist})",
]

for i, p in enumerate(reach_columns):

    plt.figure()

    fig = sns.histplot(
        data=hex_reach,
        x=p,
        binwidth=20,
    )  # kde=True
    fig.set_title(plot_titles[i])
    fig.set_xlabel("Local network reach (km)")
    plt.savefig(filepaths_reach_hist[i])

    plt.show()
    plt.close()

# %%
###########################################
####### KDE PLOTS #########################
###########################################

# NETWORK REACH LENGTH
reach_len = []
lts_all = []

lts = labels

for i, l in enumerate(lts):

    reach_len.extend(hex_reach[reach_columns[i]].values)
    lts_all.extend([l] * len(hex_reach))

df = pd.DataFrame(
    {
        "reach_len": reach_len,
        "lts": lts_all,
    }
)

df.rename(columns={"lts": "Network level"}, inplace=True)

fig = sns.kdeplot(
    data=df,
    x="reach_len",
    hue="Network level",
    # multiple="stack",
    # fill=True,
    # log_scale=True,
    palette=lts_color_dict.values(),
)

fig.set_xlabel("Length (km)")
fig.set_title(f"Network reach ({reach_dist})")
plt.savefig(fp_network_reach_kde)

plt.show()

plt.close()

# NETWORK REACH LENGTH DIFFERENCE
reach_len_diff = []
lts_all = []

lts = labels[:-1]

for i, l in enumerate(lts):

    reach_len_diff.extend(hex_reach[reach_diff_columns[i]].values)
    lts_all.extend([l] * len(hex_reach))

df = pd.DataFrame(
    {
        "reach_len_diff": reach_len_diff,
        "lts": lts_all,
    }
)

df.rename(columns={"lts": "Network level"}, inplace=True)

fig = sns.kdeplot(
    data=df,
    x="reach_len_diff",
    hue="Network level",
    # multiple="stack",
    # fill=True,
    # log_scale=True,
    palette=lts_color_dict.values(),
)

fig.set_xlabel("Difference in network reach (km)")
fig.set_title(f"Network reach difference ({reach_dist})")
plt.savefig(fp_network_reach_diff_kde)

plt.show()

plt.close()

# %%
####### Violin plots ######################
###########################################

# REACH

colors = [v for v in lts_color_dict.values()]

filepaths = filepaths_violin_reach

titles = [
    f"Network reach: LTS 1 ({reach_dist})",
    f"Network reach: LTS 1-2 ({reach_dist})",
    f"Network reach: LTS 1-3 ({reach_dist})",
    f"Network reach: LTS 1-4 ({reach_dist})",
    f"Network reach: Car network ({reach_dist})",
]

for i, r in enumerate(reach_columns):

    fig = px.violin(
        hex_reach,
        y=r,
        points="all",
        box=False,
        labels=plotly_labels,
        color_discrete_sequence=[colors[i]],
        title=titles[i],
    )
    fig.show()

    fig.write_image(
        filepaths[i],
        width=1000,
        height=750,
    )

# %%

# REACH DIFF

filepaths = filepaths_violin_reach_diff

titles = [
    f"Network reach difference: Car - LTS 1 ({reach_dist})",
    f"Network reach difference: Car - LTS 1-2 ({reach_dist})",
    f"Network reach difference: Car - LTS 1-3 ({reach_dist})",
    f"Network reach difference: Car - LTS 1-4 ({reach_dist})",
]

for i, r in enumerate(reach_diff_columns):

    fig = px.violin(
        hex_reach,
        y=r,
        points="all",
        box=False,
        labels=plotly_labels,
        color_discrete_sequence=[colors[i]],
        title=titles[i],
    )
    fig.show()

    fig.write_image(
        filepaths[i],
        width=1000,
        height=750,
    )

# %%
# REACH DIFF PCT

filepaths = filepaths_violin_reach_diff_pct

titles = [
    f"Network reach difference: Car - LTS 1 (%) ({reach_dist})",
    f"Network reach difference: Car - LTS 1-2 (%) ({reach_dist})",
    f"Network reach: Car - LTS 1-3 (%) ({reach_dist})",
    f"Network reach: Car - LTS 1-4 (%) ({reach_dist})",
]

for i, r in enumerate(reach_diff_pct_columns):

    fig = px.violin(
        hex_reach,
        y=r,
        points="all",
        box=False,
        labels=plotly_labels,
        color_discrete_sequence=[colors[i]],
        title=titles[i],
    )
    fig.show()

    fig.write_image(
        filepaths[i],
        width=1000,
        height=750,
    )

# %%
##### CORRELATION PLOTS ###################

# REACH VS DENSITY

df = pd.read_sql(f"SELECT * FROM reach.reach_{reach_dist}_component_length_hex;", engine)

labels = labels_step
for c, d, r, l in zip(
    component_count_columns[:-1], density_steps_columns[:-1], reach_columns, labels
):

    fig = px.scatter(
        df,
        x=d,
        y=r,
        opacity=0.3,
        labels=plotly_labels,
        # log_x=True,
        # log_y=True,
    )

    fig.update_layout(
        font=dict(size=12, color="black"),
        autosize=False,
        width=800,
        height=600,
        yaxis_title="Network reach",
        title=f"Correlation between reach and density: {l} ({reach_dist})",
    )

    fig.write_image(
        fp_reach_density_corr + l + ".jpeg",
        width=1000,
        height=750,
    )
    fig.show()

# %%

#### Differences in network reach: DIST ###
###########################################

reach_df = pd.read_sql(f"SELECT * FROM reach.compare_reach;", engine)

network_levels = labels

reach_columns = reach_df.columns.to_list()
reach_columns.remove("hex_id")
reach_columns.remove("geometry")

#%%
keep_columns = [c for c in reach_columns if "diff" not in c ]

reach_df = reach_df[keep_columns]

labels_stat = ["Median", "Mean", "Max", "Std"]
#%%
for i, e in enumerate([np.median, np.mean, np.max, np.std]):

    reach_melt = reach_df.melt()

    #reach_melt["distance"] = reach_melt["variable"].str.split("_").str[2]

    reach_melt["distance"] = reach_melt["variable"].str[-2:]

    reach_melt["distance"] = reach_melt["distance"].str.replace(r'_', '', regex=True)

    reach_melt["network"] = reach_melt["variable"].str.split("reach").str[0]

    reach_melt["network"] = reach_melt["network"].str[:-1]

    reach_melt["distance"] = reach_melt["distance"].astype(int)

    reach_melt = reach_melt.sort_values("distance")

    org_labels_rename = {
        "lts_1": labels[0],
        "lts_1_2": labels[1],
        "lts_1_3": labels[2],
        "lts_1_4": labels[3],
        "car": labels[4],
    }
    reach_melt.replace(org_labels_rename, inplace=True)

    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=reach_melt,
        x="network",
        y="value",
        hue="distance",
        errorbar=None,
        order=network_levels,
        palette=sns.color_palette("pastel")[: len(all_reach_distances)],
        estimator=e,
    )

    # Set the labels and title
    plt.xlabel("Network type")
    plt.ylabel("Reach (km)")
    plt.title(f"{labels_stat[i]} network reach per network type")

    plt.savefig(fp_reach_compare_dist_bars + labels_stat[i].lower() + ".png")
    plt.show()
    plt.close()

# %%

# Violin plots - showing distribution of reach per distance

plt.figure(figsize=(10, 6))
sns.violinplot(
    data=reach_melt,
    x="network",
    y="value",
    hue="distance",
    order=network_levels,
    palette=sns.color_palette("pastel")[: len(distances)],
    fill=False,
)

# Set the labels and title
plt.xlabel("Network type")
plt.ylabel("Reach (km)")
plt.title(f"Network reach per network type")

plt.savefig(fp_reach_compare_dist_violin)
plt.show()
plt.close()

# %%
# KDE plots - differences in reach per distance

reach_df = pd.read_sql(f"SELECT * FROM reach.compare_reach;", engine)

for n in list(org_labels_rename.keys()):
    n_reach = n+"_reach"
    cols = [c for c in reach_df.columns if n_reach in c and "diff" not in c]

    df = reach_df[cols]
    values = df.values.flatten()
    labels_dist = []
    for d in all_reach_distances:
        labels_dist.extend([d] * len(df))

    df_flat = pd.DataFrame({"reach_length": values, "reach_distance": labels_dist})

    fig = sns.kdeplot(
        data=df_flat,
        x="reach_length",
        hue="reach_distance",
        palette="Set2",
        #multiple="stack",
        # fill=True,
        #log_scale=True,
    )

    fig.set_xlabel("Network reach (km)")
    fig.set_title(f"Network reach KDE for {n} network")

    plt.show()

    plt.close()

# %%
# KDE PLOTS - DIFFERENCES IN REACH PER DISTANCE (%)

exec(open("../helper_scripts/read_reach_comparison.py").read())
hex_reach_comparison.replace(np.nan, 0, inplace=True)

comparison_types = ['1_5', '1_10', '1_15']

plot_cols = []

for n in network_levels_step:

    for c in comparison_types:
        plot_cols.append(f"{n}_pct_diff_{c}")


rename_dict = {}

for n, l in zip(network_levels_step, labels):
    rename_dict[n] = l

for c in comparison_types:
    # Get columns which ends with c
    cols = [col for col in plot_cols if c in col]

    df = hex_reach_comparison[cols]

    df_flat = df.melt()
    df_flat["network"] = df_flat["variable"].str.split("pct").str[0]
    df_flat["network"] = df_flat["network"].str[:-1]
    df_flat.replace(rename_dict, inplace=True)

    fig = sns.kdeplot(
        data=df_flat,
        x="value",
        hue="network",
        #multiple="stack",
        # fill=True,
        palette=lts_color_dict.values(),
    )

    fig.set_xlabel(f"% difference between in network reach")
    fig.set_title(f"Comparison of network reach between distance {c.split('_')[0]} and {c.split('_')[1]} km")

    plt.savefig(fp_reach_diff_pct_kde + c + ".png")
    plt.show()

    plt.close()
# %%
