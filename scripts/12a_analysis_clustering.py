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

# CREATE DATA SET:

# SOCIO-ECONOMIC VARIABLES

# absolute and relative densities (steps)

# component count for different steps
# component per km for different steps

# largest comp size (ave, median, ??)

# reach (socio average?)
# %%
# Use robust_scale to norm cluster variables


# Explore sizes of the clusters - number of observations in each cluster, geo size, --> plot

# Group variables by cluster to explore profiles (using scaled or unscaled variables?)

# plot distribution of cluster variables (KDES)

# Experiment with K-means, DBSCAN and agglomorative clustering (spatially constrained)

# Look into elbow method - find appropriate number of clusters


# Evaluate geographical and feature coherence of clusters

# Compare scores for different clustering options?
