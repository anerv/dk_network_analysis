# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
from src import analysis_functions as analysis_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import plotly.express as px

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/df_styler.py").read())
plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

# %%

metrics = ["density", "fragmentation", "reach"]
aggregation_levels = ["administrative", "socio", "hexgrid"]
k_values = [k_muni, k_socio, k_hex]
spatial_weights_values = [f"queen_{k}" for k in k_values]
rename_dicts = [
    rename_index_dict_density,
    rename_index_dict_fragmentation,
    rename_index_dict_reach,
]

# %%

# DENSITY AND FRAGMENTATION

for i, metric in enumerate(metrics[:-1]):

    dfs = []

    for e, a in enumerate(aggregation_levels):

        # print(f"Global Moran's I for {metric} for {a}:")
        fp = f"../results/spatial_autocorrelation/{metric}/{a}/global_moransi_{spatial_weights_values[e]}.json"

        df = pd.read_json(
            fp,
            orient="index",
        )

        df.rename(columns={0: f"morans I: {a}"}, inplace=True)

        df.rename(
            index=rename_dicts[i],
            inplace=True,
        )

        dfs.append(df)

    joined_df = pd.concat(dfs, axis=1)

    display(joined_df.style.pipe(format_style_index))

    fig = px.bar(
        df.reset_index(),
        x="index",
        y=f"morans I: {a}",
        # color="Network level",
        title=f"Moran's I for {metric} at {a}",
        labels={
            "index": "Metric type",
        },
    )

    fig.show()


# %%
# REACH

df = pd.read_json(
    f"../results/spatial_autocorrelation/reach/hexgrid/global_moransi_{spatial_weights_values[e]}.json",
    orient="index",
)

df.rename(columns={0: "morans I: hexgrid"}, inplace=True)

df.rename(
    index=rename_dicts[2],
    inplace=True,
)

display(df.style.pipe(format_style_index))

fig = px.bar(
    df.reset_index(),
    x="index",
    y="morans I: hexgrid",
    # color="Network level",
    title="Moran's I for network reach",
    labels={
        "index": "Metric type",
    },
)

fig.show()

# %%
for i, metric in enumerate(metrics[:-1]):

    for e, a in enumerate(aggregation_levels):

        summary = {}

        fp = f"../results/spatial_autocorrelation/{metric}/{a}/lisas.parquet"

        gdf = gpd.read_parquet(fp)

        cols = [
            c
            for c in gdf.columns
            if c not in ["geometry", "hex_id", "municipality", "id"]
        ]

        for c in cols:
            summary[c] = gdf[c].value_counts().to_dict()

        dfs = []
        for c in summary.keys():
            df = pd.DataFrame.from_dict(summary[c], orient="index", columns=[c])

            dfs.append(df)

        joined_df = pd.concat(dfs, axis=1)

        new_col_names = [c.strip("_q") for c in joined_df.columns]
        new_cols_dict = {}
        for z, c in enumerate(joined_df.columns):
            new_cols_dict[c] = new_col_names[z]
        joined_df.rename(columns=new_cols_dict, inplace=True)

        joined_df.rename(columns=rename_dicts[i], inplace=True)

        print(f"LISA summary for {metric} at {a}")
        display(joined_df.style.pipe(format_style_index))

        long_df = joined_df.reset_index().melt(
            id_vars="index", var_name="Metric", value_name="Count"
        )

        # Create the stacked bar chart
        fig = px.bar(
            long_df,
            x="Metric",
            y="Count",
            color="index",
            title=f"LISA for {metric} at {a}",
            labels={"index": "LISA Type", "Count": "Count", "Metric": "Metric"},
            hover_data=["Metric", "index", "Count"],
            color_discrete_map={
                "Non-Significant": "#d3d3d3",
                "HH": "#d62728",
                "HL": "#e6bbad",
                "LH": "#add8e6",
                "LL": "#1f77b4",
            },
        )

        # Show the figure
        fig.show()

# %%
summary = {}

fp = f"../results/spatial_autocorrelation/reach/hexgrid/lisas.parquet"

gdf = gpd.read_parquet(fp)

cols = [c for c in gdf.columns if c not in ["geometry", "hex_id", "municipality", "id"]]

for c in cols:
    summary[c] = gdf[c].value_counts().to_dict()

dfs = []
for c in summary.keys():
    df = pd.DataFrame.from_dict(summary[c], orient="index", columns=[c])

    dfs.append(df)

joined_df = pd.concat(dfs, axis=1)

new_col_names = [c.strip("_q") for c in joined_df.columns]
new_cols_dict = {}
for i, c in enumerate(joined_df.columns):
    new_cols_dict[c] = new_col_names[i]
joined_df.rename(columns=new_cols_dict, inplace=True)

joined_df.rename(columns=rename_dicts[2], inplace=True)

print(f"LISA summary for reach at hexgrid")
display(joined_df.style.pipe(format_style_index))

long_df = joined_df.reset_index().melt(
    id_vars="index", var_name="Metric", value_name="Count"
)

# Create the stacked bar chart
fig = px.bar(
    long_df,
    x="Metric",
    y="Count",
    color="index",
    title=f"LISA for reach at hexgrid",
    labels={"index": "LISA Type", "Count": "Count", "Metric": "Metric"},
    hover_data=["Metric", "index", "Count"],
    color_discrete_map={
        "Non-Significant": "#d3d3d3",
        "HH": "#d62728",
        "HL": "#e6bbad",
        "LH": "#add8e6",
        "LL": "#1f77b4",
    },
)

# Show the figure
fig.show()
# %%
