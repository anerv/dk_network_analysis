# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
from src import analysis_functions as analysis_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly_express as px
import pandas as pd
from sklearn.preprocessing import robust_scale

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
keep_columns = (
    ["id"]
    + density_steps_columns
    + length_steps_columns
    + length_relative_steps_columns
)
socio_density = socio_density[keep_columns]

socio_density = socio_density[socio_density.total_network_length > 0]
org_len_socio = len(socio_density)
# %%
# Read socio comp count
socio_components = gpd.read_postgis(
    "SELECT * FROM fragmentation.component_length_socio;", engine, geom_col="geometry"
)
keep_columns = (
    component_count_columns + component_per_km_columns + ["id", "area_name", "geometry"]
)
socio_components = socio_components[keep_columns]

# Read socio largest comp size
socio_largest_components = gpd.read_postgis(
    "SELECT * FROM fragmentation.socio_largest_component;", engine, geom_col="geometry"
)
keep_columns = ["id"] + socio_largest_component_columns_median
socio_largest_components = socio_largest_components[keep_columns]

# Read socio reach
socio_reach = gpd.read_postgis(
    f"SELECT * FROM reach.socio_reach_{reach_dist}", engine, geom_col="geometry"
)
keep_columns = ["id"] + socio_reach_median_columns
socio_reach = socio_reach[keep_columns]

# %%
# Merge all
socio = socio.merge(socio_density, on="id", how="inner")
socio = socio.merge(socio_components, on="id", how="inner")
socio = socio.merge(socio_largest_components, on="id", how="inner")
socio = socio.merge(socio_reach, on="id", how="inner")

assert len(socio) == org_len_socio

socio.replace(np.nan, 0, inplace=True)
# %%
# Define cluster variables
cluster_vars = socio.columns.to_list()
cluster_vars.remove("id")
cluster_vars.remove("geometry")
cluster_vars.remove("area_name")

# Use robust_scale to norm cluster variables
socio_scaled = robust_scale(socio[cluster_vars])

# %%
# Find appropriate number of clusters
m1, m2 = analysis_func.find_k_elbow_method(socio_scaled, min_k=1, max_k=20)

for key, val in m1.items():
    print(f"{key} : {val}")

# %%
##### K-Means #######

k = 5
kmeans = KMeans(n_clusters=k)

np.random.seed(1234)
k_class = kmeans.fit(socio_scaled)

socio[f"k{k}cls"] = k_class.labels_

f, ax = plt.subplots(1, figsize=(10, 10))
socio.plot(column=f"k{k}cls", categorical=True, legend=True, linewidth=0, ax=ax)
ax.set_axis_off()

# %%
##### DBSCAN #######


##### Hiearchical clustering #######


##### Regionalization #######


# %%


# Explore sizes of the clusters - number of observations in each cluster, geo size, --> plot

# Group variables by cluster to explore profiles (using scaled or unscaled variables?)

# plot distribution of cluster variables (KDES)

# Evaluate geographical and feature coherence of clusters

# *****


# Compare scores for different clustering options?

# Make step that compares the fit etc based on clustering method and variables used


# %%
