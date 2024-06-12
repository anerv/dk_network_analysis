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
# TODO: READ DATA
exec(open("../settings/prepare_socio_cluster_data.py").read())
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
from sklearn import metrics
from scipy.spatial.distance import cdist
from sklearn.cluster import KMeans
import seaborn as sns
from sklearn.cluster import AgglomerativeClustering


def run_kmeans(k, scaled_data):

    np.random.seed(13)

    kmeans = KMeans(n_clusters=k)
    k_class = kmeans.fit(scaled_data)

    return k_class.labels_


def run_regionalization(scaled_data, weights, n_clusters):

    np.random.seed(18)
    # Specify cluster model with spatial constraint
    model = AgglomerativeClustering(
        linkage="ward", connectivity=weights.sparse, n_clusters=n_clusters
    )
    # Fit algorithm to the data
    model.fit(scaled_data)

    return model.labels_


def run_agg_clustering(scaled_data, linkage, n_clusters):

    np.random.seed(17)

    model = AgglomerativeClustering(linkage=linkage, n_clusters=n_clusters)
    model.fit(scaled_data)

    return model.labels_


def plot_clustering(gdf, cluster_col):

    _, ax = plt.subplots(1, figsize=(10, 5))

    gdf.plot(column=cluster_col, categorical=True, legend=True, linewidth=0, ax=ax)
    ax.set_axis_off()


def evaluate_cluster_sizes(gdf, cluster_col):

    cluster_sizes = gdf.groupby(cluster_col).size()

    return cluster_sizes


def evaluate_cluster_areas(gdf, cluster_col):

    gdf["area_sqkm"] = gdf.area / 10**6
    cluster_areas = gdf.dissolve(by=cluster_col, aggfunc="sum")["area_sqkm"]

    return cluster_areas


def plot_cluster_sizes(cluster_sizes, cluster_areas):

    _, ax = plt.subplots(1, figsize=(10, 5))
    area_tracts = pd.DataFrame({"No. Tracts": cluster_sizes, "Area": cluster_areas})
    area_tracts = area_tracts * 100 / area_tracts.sum()
    ax = area_tracts.plot.bar()
    ax.set_xlabel("Cluster labels")
    ax.set_ylabel("Percentage by cluster")


def get_mean_cluster_variables(gdf, cluster_col, cluster_variables):

    cluster_means = gdf.groupby(cluster_col)[cluster_variables].mean()

    cluster_means = cluster_means.T.round(3)

    display(cluster_means)


def plot_cluster_variable_distributions(gdf, cluster_col, cluster_variables):
    tidy_df = gdf.set_index(cluster_col)
    tidy_df = tidy_df[cluster_variables]
    tidy_df = tidy_df.stack()
    tidy_df = tidy_df.reset_index()
    tidy_df = tidy_df.rename(columns={"level_1": "Attribute", 0: "Values"})
    sns.set(font_scale=1.5)
    facets = sns.FacetGrid(
        data=tidy_df,
        col="Attribute",
        hue=cluster_col,
        sharey=False,
        sharex=False,
        aspect=2,
        col_wrap=3,
    )
    _ = facets.map(sns.kdeplot, "Values", shade=True).add_legend()


def map_clusters(gdf, cluster_cols, titles):

    _, axs = plt.subplots(1, len(cluster_cols), figsize=(12, 6))

    for i, cluster_col in enumerate(cluster_cols):

        gdf.plot(
            column=cluster_col,
            categorical=True,
            cmap="Set2",
            legend=True,
            linewidth=0,
            ax=axs[i],
        )

        axs[i].set_axis_off()
        axs[i].set_title(titles[i])

    plt.show()


def evaluate_geographical_coherence(gdf, clustering_results):

    results = []

    for cluster_type in clustering_results:

        regions = gdf[[cluster_type, "geometry"]].dissolve(by=cluster_type)
        ipqs = regions.area * 4 * np.pi / (regions.boundary.length**2)
        result = ipqs.to_frame(cluster_type)
        results.append(result)

    return pd.concat(results, axis=1)


def evaluate_feature_coherence(gdf, clustering_results, cluster_variables):

    ch_scores = []

    for cluster_type in clustering_results:

        ch_score = metrics.calinski_harabasz_score(
            robust_scale(gdf[cluster_variables]), gdf[cluster_type]
        )

        ch_scores.append((cluster_type, ch_score))

    return pd.DataFrame(ch_scores, columns=["cluster type", "CH score"]).set_index(
        "cluster type"
    )


def evaluate_solution_similarity(gdf):

    scores = []
    for i_cluster_type in gdf.columns:
        for j_cluster_type in gdf.columns:
            score = metrics.adjusted_mutual_info_score(
                gdf[i_cluster_type], gdf[j_cluster_type]
            )
            scores.append((i_cluster_type, j_cluster_type, score))
    results = pd.DataFrame(scores, columns=["source", "target", "similarity"])
    return results.pivot("source", "target", "similarity")


# %%

##### K-Means #######


# %%
##### Hiearchical clustering #######


##### Regionalization #######


# %%


# TODO Make step that compares the fit etc based on clustering method and variables used


# %%
