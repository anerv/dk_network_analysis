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

# LOOK INTO CORR BETWEEN POP DENS, URB CLASS (??), AND SOCIO FACTORS BETWEEN SELECT METRICS
# %%

# FIRST: LOOK INTO SPATIAL PATTERNS IN POP AND SOCIO FACTORS


# %%
## CORR BETWEEN DENSITY AND POP

# Make small multiple plot with corr between pop density and all different density metrics (length ind an step, density, relative length etc.)

## CORR BETWEEN DENSITY AND car ownership

## CORR BETWEEN DENSITY AND income
