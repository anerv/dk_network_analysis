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

sns.set_theme("paper")

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/filepaths.py").read())
plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)
# %%
# Read data

hex_reach = gpd.read_postgis(
    "SELECT * FROM reach.hex_reach", engine, geom_col="geometry"
)

for p in reach_columns:
    hex_reach[p] = hex_reach[p] / 1000  # Convert to km

for p in reach_diff_columns:
    hex_reach[p] = hex_reach[p] / 1000  # Convert to km

# %%
###########################################
####### MAPS ##############################
###########################################

# Absolute reach length

# Use norm/same color scale for all maps?

plot_titles = [
    "Network reach: LTS 1",
    "Network reach: LTS 1-2",
    "Network reach: LTS 1-3",
    "Network reach: LTS 1-4",
    "Network reach: Car network",
]

plot_columns = reach_columns
filepaths = filepaths_reach

min_vals = [hex_reach[p].min() for p in plot_columns]
max_vals = [hex_reach[p].max() for p in plot_columns]
v_min = min(min_vals)
v_max = max(max_vals)

for i, p in enumerate(plot_columns):

    plot_func.plot_classified_poly(
        gdf=hex_reach,
        plot_col=p,
        scheme=scheme,
        k=k,
        cx_tile=cx_tile_2,
        plot_na=True,
        cmap=pdict["pos"],
        edgecolor="none",
        title=plot_titles[i],
        fp=filepaths[i],
    )

    plot_func.plot_unclassified_poly(
        poly_gdf=hex_reach,
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
# Absolute reach differences

# Use diverging color map
# Use norm/same color scale for all maps?

plot_titles = [
    "Difference in network reach: Car VS. LTS 1",
    "Difference in network reach: Car VS. LTS 1-2",
    "Difference in network reach: Car VS. LTS 1-3",
    "Difference in network reach: Car VS. LTS 1-4",
]

filepaths = filepaths_reach_diff

plot_columns = reach_diff_columns


min_vals = [hex_reach[p].min() for p in plot_columns]
max_vals = [hex_reach[p].max() for p in plot_columns]
v_min = min(min_vals)
v_max = max(max_vals)

for i, p in enumerate(plot_columns):

    plot_func.plot_classified_poly(
        gdf=hex_reach,
        plot_col=p,
        scheme=scheme,
        k=k,
        cx_tile=cx_tile_2,
        plot_na=True,
        cmap=pdict["pos"],
        edgecolor="none",
        title=plot_titles[i],
        fp=filepaths[i],
    )

    plot_func.plot_unclassified_poly(
        poly_gdf=hex_reach,
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
# Pct differences between LTS and car reach

# Use diverging color map
# Use norm/same color scale for all maps?

plot_titles = [
    "Difference in network reach: Car VS. LTS 1 (%)",
    "Difference in network reach: Car VS. LTS 1-2 (%)",
    "Difference in network reach: Car VS. LTS 1-3 (%)",
    "Difference in network reach: Car VS. LTS 1-4 (%)",
]

filepaths = filepaths_reach_diff_pct

plot_columns = reach_diff_pct_columns


min_vals = [hex_reach[p].min() for p in plot_columns]
max_vals = [hex_reach[p].max() for p in plot_columns]
v_min = min(min_vals)
v_max = max(max_vals)


for i, p in enumerate(plot_columns):

    plot_func.plot_classified_poly(
        gdf=hex_reach,
        plot_col=p,
        scheme=scheme,
        k=k,
        cx_tile=cx_tile_2,
        plot_na=True,
        cmap=pdict["pos"],
        edgecolor="none",
        title=plot_titles[i],
        fp=filepaths[i],
    )

    plot_func.plot_unclassified_poly(
        poly_gdf=hex_reach,
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
###########################################
####### Histograms ########################
###########################################

plot_titles = [
    "Network reach: LTS 1",
    "Network reach: LTS 1-2",
    "Network reach: LTS 1-3",
    "Network reach: LTS 1-4",
    "Network reach: Car network",
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

    plt.show()
    plt.close()
# %%
###########################################
####### KDE PLOTS #########################
###########################################

# NETWORK REACH LENGTH
reach_len = []
lts_all = []

lts = ["1", "2", "3", "4", "car"]

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
fig.set_title(f"Network reach")
plt.savefig(fp_network_reach_kde)

plt.show()

plt.close()

# NETWORK REACH LENGTH DIFFERENCE
reach_len_diff = []
lts_all = []

lts = ["1", "2", "3", "4"]

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
fig.set_title(f"Network reach difference")
plt.savefig(fp_network_reach_diff_kde)

plt.show()

plt.close()

# %%
###########################################
####### Violin plots ######################
###########################################

colors = [v for v in lts_color_dict.values()]

# reach

filepaths = filepaths_violin_reach

titles = [
    "Network reach: LTS 1",
    "Network reach: LTS 1-2",
    "Network reach: LTS 1-3",
    "Network reach: LTS 1-4",
    "Network reach: Car network",
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

# reach_diff

filepaths = filepaths_violin_reach_diff

titles = [
    "Network reach difference: Car - LTS 1",
    "Network reach difference: Car - LTS 1-2",
    "Network reach difference: Car - LTS 1-3",
    "Network reach difference: Car - LTS 1-4",
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

# reach_diff_pct

filepaths = filepaths_violin_reach_diff_pct

titles = [
    "Network reach difference: Car - LTS 1 (%)",
    "Network reach difference: Car - LTS 1-2 (%)",
    "Network reach: Car - LTS 1-3 (%)",
    "Network reach: Car - LTS 1-4 (%)",
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

# Correlation plots

df = pd.read_sql("SELECT * FROM reach.reach_component_length_h3;", engine)

labels = ["LTS 1", "LTS 1-2", "LTS 1-3", "LTS 1-4", "Car network"]
for c, d, r, l in zip(
    component_count_columns[:-1], density_steps_columns[:-1], reach_columns, labels
):

    fig = px.scatter(
        df,
        x=d,
        y=r,
        # color=c,
        # color_discrete_sequence=["black"],
        # color_continuous_scale=px.colors.sequential.Viridis,
        opacity=0.3,
        labels=plotly_labels,
        log_x=True,
        log_y=True,
    )

    fig.update_layout(
        font=dict(size=12, color="black"),
        autosize=False,
        width=800,
        height=600,
        yaxis_title="Network reach",
        title=f"Correlation between reach and density: {l}",
    )

    fig.write_image(
        fp_reach_density_corr + l + ".jpeg",
        width=1000,
        height=750,
    )
    fig.show()

# %%
