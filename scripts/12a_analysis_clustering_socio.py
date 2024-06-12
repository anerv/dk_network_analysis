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
from sklearn import metrics
from scipy.spatial.distance import cdist
from sklearn.cluster import KMeans

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

# TODO:
# add reach comparison

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
k5sizes = db.groupby("k5cls").size()
k5sizes

areas = db.dissolve(by="k5cls", aggfunc="sum")["area_sqm"]
areas

# Bind cluster figures in a single table
area_tracts = pandas.DataFrame({"No. Tracts": k5sizes, "Area": areas})
# Convert raw values into percentages
area_tracts = area_tracts * 100 / area_tracts.sum()
# Bar plot
ax = area_tracts.plot.bar()
# Rename axes
ax.set_xlabel("Cluster labels")
ax.set_ylabel("Percentage by cluster")


# Group table by cluster label, keep the variables used
# for clustering, and obtain their mean
k5means = db.groupby("k5cls")[cluster_variables].mean()
# Transpose the table and print it rounding each value
# to three decimals
k5means.T.round(3)

# Index db on cluster ID
tidy_db = db.set_index("k5cls")
# Keep only variables used for clustering
tidy_db = tidy_db[cluster_variables]
# Stack column names into a column, obtaining
# a "long" version of the dataset
tidy_db = tidy_db.stack()
# Take indices into proper columns
tidy_db = tidy_db.reset_index()
# Rename column names
tidy_db = tidy_db.rename(columns={"level_1": "Attribute", 0: "Values"})
# Check out result
tidy_db.head()

# Scale fonts to make them more readable
seaborn.set(font_scale=1.5)
# Setup the facets
facets = seaborn.FacetGrid(
    data=tidy_db,
    col="Attribute",
    hue="k5cls",
    sharey=False,
    sharex=False,
    aspect=2,
    col_wrap=3,
)
# Build the plot from `sns.kdeplot`
_ = facets.map(seaborn.kdeplot, "Values", shade=True).add_legend()
# %%
##### Hiearchical clustering #######


##### Regionalization #######


# %%


# Explore sizes of the clusters - number of observations in each cluster, geo size, --> plot

# Group variables by cluster to explore profiles (using scaled or unscaled variables?)

# plot distribution of cluster variables (KDES)

# Evaluate geographical and feature coherence of clusters

# *****


# Make step that compares the fit etc based on clustering method and variables used


# Geographical coherence
results = []
for cluster_type in ("k5cls", "ward5", "ward5wq", "ward5wknn"):
    # compute the region polygons using a dissolve
    regions = db[[cluster_type, "geometry"]].dissolve(by=cluster_type)
    # compute the actual isoperimetric quotient for these regions
    ipqs = regions.area * 4 * numpy.pi / (regions.boundary.length**2)
    # cast to a dataframe
    result = ipqs.to_frame(cluster_type)
    results.append(result)
# stack the series together along columns
pandas.concat(results, axis=1)

# Feature coherence (goodness of fit)
ch_scores = []
for cluster_type in ("k5cls", "ward5", "ward5wq", "ward5wknn"):
    # compute the CH score
    ch_score = metrics.calinski_harabasz_score(
        # using scaled variables
        robust_scale(db[cluster_variables]),
        # using these labels
        db[cluster_type],
    )
    # and append the cluster type with the CH score
    ch_scores.append((cluster_type, ch_score))

# re-arrange the scores into a dataframe for display
pandas.DataFrame(ch_scores, columns=["cluster type", "CH score"]).set_index(
    "cluster type"
)

# solution similarity
ami_scores = []
# for each cluster solution
for i_cluster_type in ("k5cls", "ward5", "ward5wq", "ward5wknn"):
    # for every other clustering
    for j_cluster_type in ("k5cls", "ward5", "ward5wq", "ward5wknn"):
        # compute the adjusted mutual info between the two
        ami_score = metrics.adjusted_mutual_info_score(
            db[i_cluster_type], db[j_cluster_type]
        )
        # and save the pair of cluster types with the score
        ami_scores.append((i_cluster_type, j_cluster_type, ami_score))
# arrange the results into a dataframe
results = pandas.DataFrame(ami_scores, columns=["source", "target", "similarity"])
# and spread the dataframe out into a square
results.pivot("source", "target", "similarity")


# %%
