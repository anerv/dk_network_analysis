import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from pysal.explore import esda
from pysal.lib import weights
from splot.esda import lisa_cluster
from sklearn import metrics
from scipy.spatial.distance import cdist
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import robust_scale
from IPython.display import display
from src import plotting_functions as plot_func

# Clustering functions based on https://geographicdata.science/book/notebooks/10_clustering_and_regionalization.html#


def spatial_weights_combined(gdf, id_column, k=3):

    w_queen = compute_spatial_weights(gdf, id_column, "queen")
    w_knn = compute_spatial_weights(gdf, id_column, w_type="knn", k=3)
    w = weights.set_operations.w_union(w_queen, w_knn)

    assert len(w.islands) == 0

    return w


def examine_cluster_results(
    gdf, cluster_col, cluster_variables, fp_map, fp_size, fp_kde
):

    plot_func.plot_clustering(gdf, cluster_col, fp_map)

    cluster_sizes = evaluate_cluster_sizes(gdf, cluster_col)
    cluster_areas = evaluate_cluster_areas(gdf, cluster_col)

    plot_func.plot_cluster_sizes(cluster_sizes, cluster_areas, fp_size)

    cluster_means = get_mean_cluster_variables(gdf, cluster_col, cluster_variables)

    plot_func.plot_cluster_variable_distributions(
        gdf, cluster_col, cluster_variables, fp_kde
    )

    return cluster_means


def compare_clustering(
    gdf,
    cluster_columns,
    cluster_variables,
    plot_titles,
    df_styler,
    fp_geo,
    fp_feature,
    fp_similarity,
    fp_map,
):

    geo = evaluate_geographical_coherence(gdf, cluster_columns)

    geo.to_csv(fp_geo, index=True)

    print("Geographical coherence:")
    display(geo.style.pipe(df_styler))

    feature = evaluate_feature_coherence(gdf, cluster_columns, cluster_variables)
    feature.to_csv(fp_feature, index=True)

    print("Feature coherence (goodness of fit):")
    display(feature.style.pipe(df_styler))

    print("Solution similarity:")
    similiarity = evaluate_solution_similarity(gdf, cluster_columns)
    similiarity.to_csv(fp_similarity, index=True)
    display(similiarity.style.pipe(df_styler))

    plot_func.map_all_cluster_results(gdf, cluster_columns, plot_titles, fp_map)


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


def evaluate_cluster_sizes(gdf, cluster_col):

    cluster_sizes = gdf.groupby(cluster_col).size()

    return cluster_sizes


def evaluate_cluster_areas(gdf, cluster_col):

    gdf["area_sqkm"] = gdf.area / 10**6
    cluster_areas = gdf.dissolve(by=cluster_col, aggfunc="sum")["area_sqkm"]

    return cluster_areas


def get_mean_cluster_variables(gdf, cluster_col, cluster_variables):

    cluster_means = gdf.groupby(cluster_col)[cluster_variables].mean()

    cluster_means = cluster_means.T.round(3)

    display(cluster_means)

    return cluster_means


def evaluate_geographical_coherence(gdf, cluster_columns):

    results = []

    for cluster_type in cluster_columns:

        regions = gdf[[cluster_type, "geometry"]].dissolve(by=cluster_type)
        ipqs = regions.area * 4 * np.pi / (regions.boundary.length**2)
        result = ipqs.to_frame(cluster_type)
        results.append(result)

    return pd.concat(results, axis=1)


def evaluate_feature_coherence(gdf, cluster_columns, cluster_variables):

    ch_scores = []

    for cluster_type in cluster_columns:

        ch_score = metrics.calinski_harabasz_score(
            robust_scale(gdf[cluster_variables]), gdf[cluster_type]
        )

        ch_scores.append((cluster_type, ch_score))

    return pd.DataFrame(ch_scores, columns=["cluster type", "CH score"]).set_index(
        "cluster type"
    )


def evaluate_solution_similarity(gdf, cluster_columns):

    scores = []
    for i_cluster_type in cluster_columns:
        for j_cluster_type in cluster_columns:
            score = metrics.adjusted_mutual_info_score(
                gdf[i_cluster_type], gdf[j_cluster_type]
            )
            scores.append((i_cluster_type, j_cluster_type, score))
    results = pd.DataFrame(scores, columns=["source", "target", "similarity"])
    return results.pivot(index="source", columns="target", values="similarity")


def find_k_elbow_method(input_data, min_k=1, max_k=10):
    # Based on https://www.geeksforgeeks.org/elbow-method-for-optimal-value-of-k-in-kmeans/
    distortions = []
    inertias = []
    mapping1 = {}
    mapping2 = {}
    K = range(min_k, max_k)

    for k in K:
        # Building and fitting the model
        kmeanModel = KMeans(n_clusters=k).fit(input_data)

        distortions.append(
            sum(
                np.min(
                    cdist(input_data, kmeanModel.cluster_centers_, "euclidean"),
                    axis=1,
                )
            )
            / input_data.shape[0]
        )
        inertias.append(kmeanModel.inertia_)

        mapping1[k] = (
            sum(
                np.min(
                    cdist(input_data, kmeanModel.cluster_centers_, "euclidean"),
                    axis=1,
                )
            )
            / input_data.shape[0]
        )
        mapping2[k] = kmeanModel.inertia_

    plt.plot(K, distortions, "bx-")
    plt.xlabel("K")
    plt.ylabel("Distortion")
    plt.title("Elbow Method: Find best K")
    plt.show()

    return mapping1, mapping2


def compare_spatial_weights_sensitivity(
    gdf,
    id_column,
    aggregation_level,
    k_values,
    all_columns,
    fp,
):

    print("Starting sensitivity analysis for aggregation level:", aggregation_level)

    # Compute spatial weights
    w1 = compute_spatial_weights(
        gdf, id_column, "knn", k=k_values[0]
    )  # using filler col for subset
    w2 = compute_spatial_weights(
        gdf, id_column, "knn", k=k_values[1]
    )  # using filler col for subset
    w3 = compute_spatial_weights(
        gdf, id_column, "knn", k=k_values[2]
    )  # using filler col for subset

    all_weigths = {
        "w1": w1,
        "w2": w2,
        "w3": w3,
    }

    for columns in all_columns:

        for c in columns:

            # dictionaries for results
            all_morans = {}
            all_lisas = {}
            hotspot_count = {}
            coldspot_count = {}

            col_names = [c]
            variable_names = [c]

            for name, w in all_weigths.items():

                morans_density = compute_spatial_autocorrelation(
                    col_names,
                    variable_names,
                    gdf,
                    w,
                    [fp + f"moransi_{aggregation_level}_{c}"],
                    show_plot=False,
                )

                all_morans[name] = morans_density[c].I

                filepaths = [fp + f"lisa_{c}_{name}_{aggregation_level}.png"]

                lisas_density = compute_lisa(
                    col_names, variable_names, gdf, w, filepaths, show_plot=False
                )

                all_lisas[name] = lisas_density[c]

                # Export
                q_columns = [v + "_q" for v in variable_names]
                q_columns.append("id")
                gdf.rename({id_column: "id"}, axis=1)[q_columns].to_csv(
                    fp + f"spatial_autocorrelation_{name}_{c}_{aggregation_level}.csv",
                    index=True,
                )

                for v in variable_names:
                    hotspot = len(gdf[gdf[f"{v}_q"] == "HH"])
                    coldspot = len(gdf[gdf[f"{v}_q"] == "LL"])

                    print(
                        f"Using spatial weights {name}, for '{v}', {hotspot} out of {len(gdf)} units ({hotspot/len(gdf)*100:.2f}%) are part of a hotspot."
                    )
                    print(
                        f"Using spatial weights {name}, for '{v}', {coldspot} out of {len(gdf)} units ({coldspot/len(gdf)*100:.2f}%) are part of a coldspot."
                    )
                    print("\n")

                    hotspot_count[name] = hotspot
                    coldspot_count[name] = coldspot

            _ = plt.figure(figsize=(10, 5))

            # creating the bar plot
            plt.bar(all_morans.keys(), all_morans.values(), color="#AA336A", width=0.4)

            plt.xlabel("Spatial weights")
            plt.ylabel("Moran's I")
            plt.title(
                f"Comparison of global spatial autocorrelation for {c} at aggregation {aggregation_level}"
            )
            plt.show()

            _ = plt.figure(figsize=(10, 5))

            # creating the bar plot
            plt.bar(
                hotspot_count.keys(),
                hotspot_count.values(),
                color="#916E99",
                width=0.4,
            )

            plt.xlabel("Spatial weights")
            plt.ylabel("Number of units in hot spot")
            plt.title(
                f"Comparison of areas in hot spot for {c} at aggregation {aggregation_level}"
            )
            plt.show()

            _ = plt.figure(figsize=(10, 5))

            # creating the bar plot
            plt.bar(
                coldspot_count.keys(),
                coldspot_count.values(),
                color="#658CBB",
                width=0.4,
            )

            plt.xlabel("Spatial weights")
            plt.ylabel("Number of grid cells in cold spot")
            plt.title(
                f"Comparison of areas in cold spot for {c} at aggregation {aggregation_level}"
            )
            plt.show()


def compute_spatial_weights(gdf, na_columns, w_type, dist=1000, k=6):
    """
    Wrapper function for computing the spatial weights for the analysis/results grids.
    ...

    Arguments:
        gdf (geodataframe): geodataframe with polygons
        na_columns (list): list of columns used to drop NA rows. If no rows should be dropped, just use e.g. 'grid_index'
        w_type (str): type of spatial weight to compute. Only supports KNN, distance band or queens.
        dist (numeric): distance to use if distance band
        k (int): number of nearest neighbors if using KNN

    Returns:
        w (pysal spatial weight object): the spatial weight object
    """
    gdf.dropna(subset=na_columns, inplace=True)

    # convert to centroids
    cents = gdf.centroid

    # Extract coordinates into an array
    pts = pd.DataFrame({"X": cents.x, "Y": cents.y}).values

    if w_type == "dist":
        w = weights.distance.DistanceBand.from_array(pts, dist, binary=False)

    elif w_type == "knn":
        w = weights.distance.KNN.from_array(pts, k=k)

    elif w_type == "queen":
        w = weights.contiguity.Queen.from_dataframe(gdf, use_index=False)

    else:
        print("no valid type defined")

        pass

    # row standardize
    w.transform = "R"

    return w


def compute_lisa(
    col_names, variable_names, gdf, spatial_weights, filepaths, p=0.05, show_plot=True
):
    # based on https://geographicdata.science/book/notebooks/07_local_autocorrelation.html

    """
    Wrapper function for computing and plotting local spatial autocorrelation.
    ...

    Arguments:
        col_names (list of str): names of cols for which local spatial autocorrelation should be computed
        variable_names (list of str): name of variables (only to avoid using potentially long or confusing column names for print statements etc.)
        gdf (geodataframe): geodataframe with polygon data set
        spatial_weights (pysal spatial weight object): the spatial weight object used in the computation
        filepaths (list or str): list of filepaths for storing the plots
        p (float): the desired pseudo p-value


    Returns:
        lisas (dict): dictionary with pysal lisas objects for all columns/variables
    """

    lisas = {}

    significance_labels = {}

    for i, c in enumerate(col_names):
        v = variable_names[i]

        lisa = esda.moran.Moran_Local(gdf[c], spatial_weights)

        lisas[v] = lisa

        sig = 1 * (lisa.p_sim < p)

        spots = lisa.q * sig

        # Mapping from value to name (as a dict)
        spots_labels = {
            0: "Non-Significant",
            1: "HH",
            2: "LH",
            3: "LL",
            4: "HL",
        }
        gdf[f"{v}_q"] = pd.Series(spots, index=gdf.index).map(spots_labels)

        f, axs = plt.subplots(nrows=2, ncols=2, figsize=(15, 15))
        axs = axs.flatten()

        ax = axs[0]

        gdf.assign(Is=lisa.Is).plot(
            column="Is",
            cmap="plasma",
            scheme="quantiles",
            k=2,
            edgecolor="white",
            linewidth=0.1,
            alpha=0.75,
            legend=True,
            ax=ax,
        )

        ax = axs[1]

        lisa_cluster(lisa, gdf, p=1, ax=ax)

        ax = axs[2]
        labels = pd.Series(1 * (lisa.p_sim < p), index=gdf.index).map(
            {1: "Significant", 0: "Non-Significant"}
        )
        gdf.assign(cl=labels).plot(
            column="cl",
            categorical=True,
            k=2,
            cmap="Paired",
            linewidth=0.1,
            edgecolor="white",
            legend=True,
            ax=ax,
        )

        significance_labels[v] = labels

        ax = axs[3]
        lisa_cluster(lisa, gdf, p=p, ax=ax)

        for z, ax in enumerate(axs.flatten()):
            ax.set_axis_off()
            ax.set_title(
                [
                    "Local Statistics",
                    "Scatterplot Quadrant",
                    "Statistical Significance",
                    "Moran Cluster Map",
                ][z],
                y=0,
            )

        f.suptitle(
            f"Local Spatial Autocorrelation for differences in: {v}", fontsize=16
        )

        f.tight_layout()

        f.savefig(filepaths[i])

        if show_plot:
            plt.show()

        plt.close()

    return lisas


def compute_spatial_autocorrelation(
    col_names,
    variable_names,
    df,
    spatial_weights,
    filepaths,
    show_plot=True,
    print_results=True,
):
    """
    Wrapper function for computing and plotting global spatial autocorrelation (Moran's I)
    ...

    Arguments:
        col_names (list of str): names of cols for which local spatial autocorrelation should be computed
        variable_names (list of str): name of variables (only to avoid using potentially long or confusing column names for print statements etc.)
        df (dataframe/geodataframe): dataframe or geodataframe with data
        spatial_weights (pysal spatial weight object): the spatial weight object used in the computation
        filepaths (list or str): list of filepaths for storing the plots


    Returns:
        morans (dict): dictionary with pysal morans objects for all columns/variables
    """
    morans = {}

    for i, c in enumerate(col_names):
        v = variable_names[i]

        # compute spatial lag
        df[f"{v}_lag"] = weights.spatial_lag.lag_spatial(spatial_weights, df[c])

        fig, ax = plt.subplots(1, figsize=(5, 5))

        sns.regplot(
            x=c,
            y=f"{v}_lag",
            ci=None,
            data=df,
            line_kws={"color": "r"},
            scatter_kws={"alpha": 0.4},
            color="black",
        )

        ax.axvline(0, c="k", alpha=0.5)
        ax.axhline(0, c="k", alpha=0.5)
        ax.set_title(f"Moran Plot - {v}")

        if show_plot:
            plt.show()

        moran = esda.moran.Moran(df[c], spatial_weights)

        if print_results:
            print(
                f"With significance {moran.p_sim}, the Moran's I value for {v} is {moran.I:.2f}"
            )

        morans[v] = moran

        fig.savefig(filepaths[i])

        plt.close()

    return morans
