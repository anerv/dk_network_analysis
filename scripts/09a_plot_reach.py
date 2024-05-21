# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly_express as px
import pandas as pd

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)
# %%
# read data

hex_reach = gpd.read_postgis("SELECT * FROM reach.hex_reach", connection)

# %%
# MAPS:
# Reach length

# Reach diffs

# Reach len as share of car length


# %%
# Corr plots

# Corr between reach length and density?? (if so, join with density data)


# Corr with components?

# %%
# Distribution plots of reach length and diffs?

# KDE etc.
