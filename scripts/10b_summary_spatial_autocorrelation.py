# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
from src import analysis_functions as analysis_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json

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
rename_dicts = [
    rename_index_dict_density,
    rename_index_dict_fragmentation,
    rename_index_dict_reach,
]

# %%

for i, metric in enumerate(metrics[:-1]):

    dfs = []

    for e, a in enumerate(aggregation_levels):

        # print(f"Global Moran's I for {metric} for {a}:")

        fp = f"../results/spatial_autocorrelation/{metric}/{a}/global_moransi_k{k_values[e]}.json"

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


df = pd.read_json(
    f"../results/spatial_autocorrelation/reach/hexgrid/global_moransi_k{k_values[2]}.json",
    orient="index",
)

df.rename(columns={0: "morans I: hexgrid"}, inplace=True)

df.rename(
    index=rename_dicts[i],
    inplace=True,
)

display(df.style.pipe(format_style_index))

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
        for i, c in enumerate(joined_df.columns):
            new_cols_dict[c] = new_col_names[i]
        joined_df.rename(columns=new_cols_dict, inplace=True)

        print(f"LISA summary for {metric} at {a}")
        display(joined_df.style.pipe(format_style_index))
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

print(f"LISA summary for reach at hexgrid")
display(joined_df.style.pipe(format_style_index))
# %%
