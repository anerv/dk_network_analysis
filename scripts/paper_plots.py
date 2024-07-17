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
# %%
socio = gpd.read_postgis("SELECT * FROM socio;", engine, geom_col="geometry")

# %%
plot_cols = [
    "households_with_car_share",
    "urban_pct",
    "population_density",
    "households_income_50_percentile",
]

titles = [
    "Households with car share",
    "Urban percentage",
    "Population density",
    "Households income 50 percentile",
]

for p in plot_cols:
    fig, ax = plt.subplots(1, 1, figsize=(10, 15))
    socio.plot(
        column=p,
        ax=ax,
        cmap="magma",
        legend=True,
        linewidth=0.1,
    )
    ax.set_axis_off()
    ax.set_title(titles[plot_cols.index(p)])
    plt.tight_layout()

# %%
