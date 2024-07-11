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

exec(open("../settings/read_socio_results.py").read())

socio_density = socio_density[socio_density.total_network_length > 0]

# Merge all
socio_cluster_gdf = socio.merge(socio_density, on="id", how="inner")
socio_cluster_gdf = socio_cluster_gdf.merge(socio_components, on="id", how="inner")
socio_cluster_gdf = socio_cluster_gdf.merge(
    socio_largest_components, on="id", how="inner"
)
socio_cluster_gdf = socio_cluster_gdf.merge(socio_reach, on="id", how="inner")
socio_cluster_gdf = socio_cluster_gdf.merge(
    socio_reach_comparison, on="id", how="inner"
)

assert len(socio_density) == len(socio_cluster_gdf)

duplicates = [
    c for c in socio_cluster_gdf.columns if c.endswith("_x") or c.endswith("_y")
]
assert len(duplicates) == 0

socio_cluster_gdf.replace(np.nan, 0, inplace=True)


# %%
