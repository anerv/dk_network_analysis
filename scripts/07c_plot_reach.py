# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
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

plot_titles = labels_step

plot_columns = reach_columns
filepaths = fps_reach

for i, p in enumerate(plot_columns):

    vmin, vmax = plot_func.get_min_max_vals(hex_reach, [p])

    plot_func.plot_unclassified_poly(
        poly_gdf=hex_reach,
        plot_col=p,
        plot_title=plot_titles[i],
        filepath=filepaths[i],
        cmap=pdict["reach"],
        edgecolor="none",
        linewidth=0.0,
        use_norm=True,
        norm_min=vmin,
        norm_max=vmax,
        background_color=pdict["background_color"],
        plot_na=True,
    )

#%%
# Zoomed map
fp = fps_reach[0] +"_zoom"
plot_column = reach_columns[0]

xmin, ymin = (689922.425333, 6161099.004817)
xmax, ymax = (734667.301464 - 900, 6202301.965700) 

vmin, vmax = plot_func.get_min_max_vals(hex_reach, [plot_column])

plot_func.plot_poly_zoom(
    poly_gdf=hex_reach,
    plot_col=plot_column,
    plot_title="LTS 1",
    filepath=fp,
    cmap=pdict["reach"],
    edgecolor="none",
    linewidth=0.1,
    use_norm=True,
    norm_min=vmin,
    norm_max=vmax,
    plot_na=True,
    xmin=xmin,
    xmax=xmax,
    ymin=ymin,
    ymax=ymax
)
# %%

# Absolute reach differences

plot_titles = [
    f"Difference in network reach: Car VS. LTS 1 ({reach_dist})",
    f"Difference in network reach: Car VS. LTS 1-2 ({reach_dist})",
    f"Difference in network reach: Car VS. LTS 1-3 ({reach_dist})",
    f"Difference in network reach: Car VS. LTS 1-4 ({reach_dist})",
]

filepaths = fps_reach_diff

plot_columns = reach_diff_columns

vmin, vmax = plot_func.get_min_max_vals(hex_reach, plot_columns)

for i, p in enumerate(plot_columns):

    plot_func.plot_unclassified_poly(
        poly_gdf=hex_reach,
        plot_col=p,
        plot_title=plot_titles[i],
        filepath=filepaths[i],
        cmap=pdict["reach"],
        edgecolor="none",
        linewidth=0.0,
        use_norm=True,
        norm_min=vmin,
        norm_max=vmax,
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

filepaths = fps_reach_diff_pct

plot_columns = reach_diff_pct_columns

vmin, vmax = plot_func.get_min_max_vals(hex_reach, plot_columns)

for i, p in enumerate(plot_columns):


    plot_func.plot_unclassified_poly(
        poly_gdf=hex_reach,
        plot_col=p,
        plot_title=plot_titles[i],
        filepath=filepaths[i],
        cmap=pdict["reach"],
        edgecolor="none",
        linewidth=0.0,
        use_norm=True,
        norm_min=vmin,
        norm_max=vmax,
        background_color=pdict["background_color"],
    )

#%%
#### MAPS - HEX REACH COMPARISON ##########

exec(open("../helper_scripts/read_reach_comparison.py").read())

#hex_reach_comparison.replace(np.nan, 0, inplace=True)
#%%
plot_columns = []
filepaths = []

for i, n in enumerate(network_levels_step):

    for comb in itertools.combinations(all_reach_distances, 2):

        plot_columns.append(f"{n}_pct_diff_{comb[0]}_{comb[1]}")
        
        filepaths.append(fp_reach_diff_pct + f"{network_levels_step[i]}_{comb[0]}-{comb[1]}")

# Get subsets
plot_columns = [c for c in plot_columns if "diff_1_5" in c or "diff_5_10" in c or "diff_10_15" in c]

filepaths = [f for f in filepaths if "1-5" in f or "1-10" in f or "1-15" in f]

multiplier = len(plot_columns) / len(labels_step)
plot_titles = []
for l in labels_step:
    plot_titles.extend([l]*3)

assert len(plot_columns) == len(filepaths) 

vmin, vmax = plot_func.get_min_max_vals(hex_reach_comparison, plot_columns)

for i, c in enumerate(plot_columns):

    plot_func.plot_unclassified_poly(
        poly_gdf=hex_reach_comparison,
        plot_col=c,
        plot_title=plot_titles[i],
        filepath=filepaths[i],
        cmap=pdict["reach"],
        edgecolor="none",
        linewidth=0.0,
        use_norm=True,
        norm_min=vmin,
        norm_max=vmax,
        background_color=pdict["background_color"],
        plot_na=True,
    )

#%%
# Zoomed map
fp = fp_reach_diff_pct + "1-5_unclassified_zoom_lts1"
plot_column = 'lts_1_pct_diff_1_5'

xmin, ymin = (639464.351371, 6120027.316230)
xmax, ymax = (699033.929025, 6173403.495114)  

vmin, vmax = plot_func.get_min_max_vals(hex_reach_comparison, [plot_column])

plot_func.plot_poly_zoom(
    poly_gdf=hex_reach_comparison,
    plot_col=plot_column,
    plot_title="LTS 1",
    filepath=fp,
    cmap=pdict["reach"],
    edgecolor="none",
    linewidth=0.1,
    use_norm=True,
    norm_min=vmin,
    norm_max=vmax,
    plot_na=True,
    xmin=xmin,
    xmax=xmax,
    ymin=ymin,
    ymax=ymax
)
# %%
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
    )  
    fig.set_title(plot_titles[i])
    fig.set_xlabel("Local network reach (km)")
    plt.savefig(fps_reach_hist[i])

    plt.show()
    plt.close()


####### KDE PLOTS #########################
###########################################

# NETWORK REACH LENGTH
reach_len = []
lts_all = []

lts = labels_step

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

lts = labels_step[:-1]

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

#%%
# KDE PLOTS
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

filepaths = fps_violin_reach

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

filepaths = fps_violin_reach_diff

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

filepaths = fps_violin_reach_diff_pct

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

for c, d, r, l in zip(
    component_count_columns[:-1], density_steps_columns[:-1], reach_columns, labels_step
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

network_levels = labels_step

reach_columns = reach_df.columns.to_list()
reach_columns.remove("hex_id")
reach_columns.remove("geometry")

keep_columns = [c for c in reach_columns if "diff" not in c ]

reach_df = reach_df[keep_columns]

labels_stat = ["Median", "Mean", "Max", "Std"]
#%%

reach_melt = reach_df.melt()

reach_melt["distance"] = reach_melt["variable"].str[-2:]

reach_melt["distance"] = reach_melt["distance"].str.replace(r'_', '', regex=True)

reach_melt["network"] = reach_melt["variable"].str.split("reach").str[0]

reach_melt["network"] = reach_melt["network"].str[:-1]

reach_melt["distance"] = reach_melt["distance"].astype(int)

reach_melt = reach_melt.sort_values("distance")

org_labels_rename = {
    "lts_1": labels_step[0],
    "lts_1_2": labels_step[1],
    "lts_1_3": labels_step[2],
    "lts_1_4": labels_step[3],
    "car": labels_step[4],
}
reach_melt.replace(org_labels_rename, inplace=True)

#%%
for i, e in enumerate([np.median, np.mean, np.max, np.std]):

    #plt.figure(figsize=(15,8))
    plt.figure(figsize=pdict["fsbar"])
    ax = sns.barplot(
        data=reach_melt,
        x="network",
        y="value",
        hue="distance",
        errorbar=None,
        order=network_levels,
        palette=list(distance_color_dict.values()),# sns.color_palette(pdict["cat"])[: len(all_reach_distances)],
        estimator=e,
        #width=0.8
    )

    for z, a in enumerate(ax.containers):
        if z == 0:
            ax.bar_label(a,fmt="{:,.1f}", label_type='edge', fontsize=8)
        # else:
        #     ax.bar_label(a,fmt="{:,.0f}", label_type='edge', fontsize=8)

    sns.despine()

    # Set the labels and title
    plt.xlabel("")
    plt.ylabel("Reach (km)")
    #plt.title(f"{labels_stat[i]} network reach per network type")
    #plt.legend(title="Distance threshold (km)", loc="upper left", fontsize=10, title_fontsize=12, frameon=False)
    leg = plt.legend(title="Distance threshold (km)", loc="upper left", fontsize=10, title_fontsize=10, frameon=False)
    leg._legend_box.align = "left"
    plt.savefig(fp_reach_compare_dist_bars + labels_stat[i].lower() + ".png", dpi=pdict["dpi"])
    plt.show()
    plt.close()

# %%

# Violin plots - showing distribution of reach per distance

plt.figure(figsize=pdict["fsbar"])
sns.violinplot(
    data=reach_melt,
    x="network",
    y="value",
    hue="distance",
    order=network_levels,
    palette=list(distance_color_dict.values()),#sns.color_palette(pdict["cat"])[: len(all_reach_distances)],
    fill=False,
    saturation=0.8,
    linewidth=1,
    inner="box",
    density_norm="count",
    native_scale=True,

    )

sns.despine()

# Set the labels and title
plt.xlabel("")
plt.ylabel("Reach (km)")
plt.title(f"Network reach per network type")
plt.legend(title="Distance (km)", loc="upper left", fontsize=10, title_fontsize=12)

plt.savefig(fp_reach_compare_dist_violin, dpi=pdict["dpi"])
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
        palette=pdict["cat"],
        #multiple="stack",
        #fill=True,
        #log_scale=True,
    )

    fig.set_xlabel("Network reach (km)")
    #fig.set_title(f"Network reach KDE for {n} network")

    plt.savefig(fp_reach_diff_dist_kde + n + ".png", dpi=pdict["dpi"])
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

for n, l in zip(network_levels_step, labels_step):
    rename_dict[n] = l


for c in comparison_types:
    # Get columns which ends with c
    cols = [col for col in plot_cols if c in col]

    df = hex_reach_comparison[cols]

    df_flat = df.melt()
    df_flat["network"] = df_flat["variable"].str.split("pct").str[0]
    df_flat["network"] = df_flat["network"].str[:-1]
    df_flat.replace(rename_dict, inplace=True)

    fig, ax = plt.subplots(figsize=pdict["fsbar"])
    g = sns.kdeplot(
        data=df_flat,
        x="value",
        hue="network",
        #multiple="stack",
        # fill=True,
        palette=lts_color_dict.values(),
        ax=ax
    )

    # Set the labels and title
    plt.xlabel(f"% difference in network reach: {c.split("_")[0]} vs. {c.split("_")[1]} km", fontdict={"size": 12})
    plt.ylabel("Reach (km)",fontdict={"size": 12})

    legend = ax.get_legend()
    if legend:
        legend.set_title(None)
        legend.set_frame_on(False)
        plt.setp(legend.get_texts(), fontsize=10)

    sns.despine()   
    plt.savefig(fp_reach_diff_pct_kde + c + ".png", dpi=pdict["dpi"])
    plt.show()

    plt.close()
# %%
