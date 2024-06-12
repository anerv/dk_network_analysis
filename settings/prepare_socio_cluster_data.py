# %%
from src import db_functions as dbf
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly_express as px
import pandas as pd

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())

# Read socio pop
exec(open("../settings/read_socio_pop.py").read())

socio.dropna(subset=["population_density"], inplace=True)

exec(open("../settings/read_socio_results.py").read())

# Merge all
socio_gdf = socio.merge(socio_density, on="id", how="inner")
socio_gdf = socio.merge(socio_components, on="id", how="inner")
socio_gdf = socio.merge(socio_largest_components, on="id", how="inner")
socio_gdf = socio.merge(socio_reach, on="id", how="inner")
socio_gdf = socio.merge(socio_reach_comparison, on="id", how="inner")

assert len(socio) == len(socio_gdf)

duplicates = [c for c in socio_gdf.columns if c.endswith("_x") or c.endswith("_y")]
assert len(duplicates) == 0

socio_gdf.replace(np.nan, 0, inplace=True)


# %%
