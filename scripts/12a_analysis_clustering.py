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

# Read socio pop
exec(open("../settings/read_socio_pop.py").read())

socio.dropna(subset=["population_density"], inplace=True)
# %%
# Read socio density
socio_density = gpd.read_postgis(
    "SELECT * FROM density.density_socio", engine, geom_col="geometry"
)
socio_density.drop(columns=["geometry", "area_name"], inplace=True)
keep_columns = (
    ["id"]
    + density_steps_columns
    + length_steps_columns
    + length_relative_steps_columns
)
socio_density = socio_density[keep_columns]

# Read socio comp count
socio_components = gpd.read_postgis(
    "SELECT * FROM fragmentation.component_length_socio;", engine, geom_col="geometry"
)
socio_components.drop(columns=["geometry"], inplace=True)
keep_columns = component_count_columns + component_per_km_columns + ["id"]
socio_components = socio_components[keep_columns]

# Read socio largest comp size
socio_largest_components = gpd.read_postgis(
    "SELECT * FROM fragmentation.socio_largest_component;", engine, geom_col="geometry"
)
keep_columns = (
    ["id"]
    + socio_largest_components_columns_min
    + socio_largest_component_columns_median
    + socio_largest_component_columns_max
)

# Read socio reach
socio_reach = gpd.read_postgis(
    f"SELECT * FROM reach.socio_reach_{reach_dist}", engine, geom_col="geometry"
)
socio_reach.drop(columns=["geometry"], inplace=True)

# %%
# Merge all
socio = socio.merge(socio_density, on="id", how="inner")
socio = socio.merge(socio_components, on="id", how="inner")
socio = socio.merge(socio_largest_components, on="id", how="inner")
socio = socio.merge(socio_reach, on="id", how="inner")

# assert correct length


# %%
# Define cluster variables

# Use robust_scale to norm cluster variables

# Explore sizes of the clusters - number of observations in each cluster, geo size, --> plot

# Group variables by cluster to explore profiles (using scaled or unscaled variables?)

# plot distribution of cluster variables (KDES)

# Evaluate geographical and feature coherence of clusters

# *****

# Experiment with K-means, DBSCAN and agglomorative clustering (spatially constrained)

# Look into elbow method - find appropriate number of clusters

# Compare scores for different clustering options?

# Make step that compares the fit etc based on clustering method and variables used
