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
from pysal.explore import inequality
from inequality.gini import Gini_Spatial
from shapely.geometry import mapping, Polygon
import h3

# Clustering functions based on https://geographicdata.science/book/notebooks/10_clustering_and_regionalization.html#

# Gini functions from  https://geographicdata.science/book/notebooks/09_spatial_inequality.html


def corrected_concentration_index(data, opportunity, population, income):
    """
    Calculate the Corrected Concentration Index (CCI) (based on equations in Karner et al. 2024)

    Parameters:
    - data (pd.DataFrame): The dataset.
    - opportunity (str): Column name representing the opportunity measure (e.g., access to low-stress infrastructure).
    - population (str): Column name representing the population.
    - income (str): Column name representing the socioeconomic variable (e.g., income).

    Returns:
    - float: The Corrected Concentration Index (CCI).
    """
    assert isinstance(opportunity, str), "'opportunity' must be a string."
    assert isinstance(population, str), "'population' must be a string."
    assert isinstance(income, str), "'income' must be a string."

    # Sort the data by the income column
    data = data.sort_values(by=income).reset_index(drop=True)

    # Number of individuals (n)
    n = len(data)

    # Assign ranks (r_i)
    data["rank"] = range(1, n + 1)  # r_i

    # Calculate weights (w_i)
    data["weight"] = data["rank"] - (n + 1) / 2

    # Calculate the upper (m_x) and lower (n_x) bounds of the opportunity measure
    m_x = data[opportunity].max()
    n_x = data[opportunity].min()
    if m_x == n_x:
        raise ValueError(
            "Upper and lower bounds of the opportunity measure are equal. CCI cannot be calculated."
        )

    # Apply the CCI formula
    data["weighted_opportunity"] = data[opportunity] * data["weight"]
    cci = (8 / (n**2 * (m_x - n_x))) * data["weighted_opportunity"].sum()

    return cci


# def corrected_concentration_index(
#     data,
#     opportunity,
#     population,
#     income,
# ):
#     # Based on https://github.com/ipeaGIT/accessibility/blob/main/R/concentration_index.R

#     """
#     Calculate the concentration index.

#     Parameters:
#     - data (pd.DataFrame): The dataset.
#     - opportunity (str): Column name representing the opportunity measure (e.g. access to low stress infrastructure).
#     - population (str): Column name representing the population.
#     - socioeconomic (str): Column name representing socioeconic variable (e.g. income).

#     Returns:
#     - pd.DataFrame: Results with concentration index calculations by group.
#     """

#     assert isinstance(opportunity, str), "'opportunity' must be a string."
#     assert isinstance(population, str), "'population' must be a string."
#     assert isinstance(income, str), "'income' must be a string."

#     # Sort data by income and group_by columns
#     sort_cols = [income]
#     data = data.sort_values(by=sort_cols)

#     # Fractional rank calculation (based on Equation 4 of the referenced paper)
#     def calculate_fractional_rank(df):
#         df["pop_share"] = df[population] / df[population].sum()
#         df["fractional_rank"] = (
#             df["pop_share"].cumsum().shift(fill_value=0) + df["pop_share"] / 2
#         )
#         return df

#     data = calculate_fractional_rank(data)

#     # Calculate average accessibility
#     def calculate_avg_access(df):
#         avg_access = np.average(df[opportunity], weights=df[population])
#         df["avg_access"] = avg_access
#         df["diff_from_avg"] = df[opportunity] - avg_access
#         return df

#     data = calculate_avg_access(data)

#     # Contribution to total calculation
#     data["cont_to_total"] = (
#         (data["fractional_rank"] - 0.5)
#         * data["diff_from_avg"]
#         * data["pop_share"]
#         / data["avg_access"]
#     )

#     # If no rows and no grouping, return empty result
#     if data.empty:
#         return pd.DataFrame(columns=["concentration_index"])

#     # Calculate the concentration index

#     # Handle corrected type
#     def add_correction_factor(df):
#         upper = df[opportunity].max()
#         lower = df[opportunity].min()
#         avg_access = df["avg_access"].iloc[0]  # Same within group
#         correction_factor = 4 * avg_access / (upper - lower) if upper != lower else 0
#         df["correction_factor"] = correction_factor
#         return df

#     data = add_correction_factor(data)

#     data["cont_to_total_corrected"] = data["cont_to_total"] * data["correction_factor"]

#     concentration_index_value = 2 * data["cont_to_total_corrected"].sum()
#     # result = pd.DataFrame({"concentration_index": [concentration_index_value]})

#     return concentration_index_value


# def concentr(opportunity, income, population):
#     """
#     Calculate the Concentration Index (CI) for given opportunity, income, and population data.
#     From https://github.com/aakarner/transit-equity-methods/blob/f30ab26a03f411d99c78d79e454dc182f9491356/00-inequality-measures.R

#     Parameters:
#     opportunity (pd.Series): The opportunity variable (e.g., access to infrastructure).
#     income (pd.Series): The income variable used for ranking.
#     population (pd.Series): The population variable used for weighting.

#     Returns:
#     float: The Concentration Index (CI).
#     """

#     # Ensure opportunity, income, and population are numpy arrays
#     opportunity = np.array(opportunity)
#     income = np.array(income)
#     population = np.array(population)

#     # Complete cases: valid values for opportunity, income, and population
#     complete = (
#         (np.isfinite(opportunity) & np.isfinite(income) & np.isfinite(population))
#         & (opportunity >= 0)
#         & (income >= 0)
#     )
#     x_c = opportunity[complete]
#     y_c = income[complete]
#     w_c = population[complete]

#     # Order by income values
#     o = np.argsort(y_c)
#     x_o = x_c[o]
#     y_o = y_c[o]
#     w_o = w_c[o]

#     # Cumulative sums for opportunity and weights
#     x_cum = np.concatenate(([0], np.cumsum((x_o * w_o) / np.sum(x_o * w_o))))
#     w_cum = np.concatenate(([0], np.cumsum(w_o / np.sum(w_o))))

#     b = x_cum[:-1]
#     B = x_cum[1:]
#     h = np.diff(w_cum)

#     # Calculate area under the concentration curve
#     area_under_concentrationCurve = np.sum(((B + b) * h) / 2)

#     return 1 - 2 * area_under_concentrationCurve


def classify_urban_rural(x):

    if x == 100:
        return "completely urban"

    elif x >= 75:
        return "very urban"

    elif x >= 50:
        return "mostly urban"

    elif x >= 25:
        return "slightly urban"

    else:
        return "rural"


def lorenz(y):
    y = np.asarray(y)
    sorted_y = np.sort(y)
    y_shares = (sorted_y / sorted_y.sum()).cumsum()
    N = y.shape[0]

    pop_shares = np.arange(1, N + 1) / N
    return pop_shares, y_shares


def compute_cumulative_shares(values):

    shares = values.sort_values() / values.sum()
    return shares.cumsum()


def gini_by_col(column):
    return inequality.gini.Gini(column.values).g


def compute_theil(column):
    return inequality.theil.Theil(column.values).T


def gini_spatial_by_column(values, weights):

    gs = Gini_Spatial(values, weights)
    denom = 2 * values.mean() * weights.n**2
    near_diffs = gs.wg / denom
    far_diffs = gs.wcg / denom
    out = pd.Series(
        {
            "gini": gs.g,
            "near_diffs": near_diffs,
            "far_diffs": far_diffs,
            "p_sim": gs.p_sim,
        }
    )
    return out


def spatial_weights_combined(gdf, id_column, k=3, silence_warnings=True):

    w_queen = compute_spatial_weights(
        gdf, id_column, "queen", silence_warnings=silence_warnings
    )
    w_knn = compute_spatial_weights(
        gdf, id_column, w_type="knn", k=3, silence_warnings=silence_warnings
    )
    w = weights.set_operations.w_union(
        w_queen, w_knn, silence_warnings=silence_warnings
    )

    assert len(w.islands) == 0

    return w


def examine_cluster_results(
    gdf, cluster_col, cluster_variables, fp_map, fp_size, fp_kde, cmap, palette
):

    plot_func.plot_clustering(gdf, cluster_col, fp_map, cmap=cmap)

    cluster_sizes = evaluate_cluster_sizes(gdf, cluster_col)
    cluster_areas = evaluate_cluster_areas(gdf, cluster_col)

    plot_func.plot_cluster_sizes(cluster_sizes, cluster_areas, fp_size)

    cluster_means = get_mean_cluster_variables(gdf, cluster_col, cluster_variables)

    plot_func.plot_cluster_variable_distributions(
        gdf, cluster_col, cluster_variables, fp_kde, palette=palette
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
    """
    Compare clustering results based on geographical coherence, feature coherence, and solution similarity.

    Parameters:
    - gdf (GeoDataFrame): The input GeoDataFrame containing the data.
    - cluster_columns (list): The list of column names representing the clustering results.
    - cluster_variables (list): The list of column names representing the variables used for clustering.
    - plot_titles (list): The list of titles for the cluster result plots.
    - df_styler (Styler): The Styler object used to style the output DataFrame.
    - fp_geo (str): The file path to save the geographical coherence results.
    - fp_feature (str): The file path to save the feature coherence results.
    - fp_similarity (str): The file path to save the solution similarity results.
    - fp_map (str): The file path to save the cluster result plots.

    Returns:
    None
    """

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

    # display(cluster_means)

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
    silence_warnings=False,
):
    """
    Compare the sensitivity of spatial weights in a sensitivity analysis.

    Parameters:
    gdf (GeoDataFrame): The input GeoDataFrame containing the spatial data.
    id_column (str): The name of the column in the GeoDataFrame that contains the unique identifiers.
    aggregation_level (str): The level of aggregation for the analysis.
    k_values (list): A list of three integers representing the k values for computing spatial weights.
    all_columns (list): A list of lists, where each inner list contains the column names to analyze.
    fp (str): The file path for saving the output files.
    silence_warnings (bool, optional): Whether to silence the warnings during spatial weights computation. Defaults to False.

    Returns:
    None
    """

    print("Starting sensitivity analysis for aggregation level:", aggregation_level)

    # Compute spatial weights
    w1 = compute_spatial_weights(
        gdf, id_column, "knn", k=k_values[0], silence_warnings=silence_warnings
    )  # using filler col for subset
    w2 = compute_spatial_weights(
        gdf, id_column, "knn", k=k_values[1], silence_warnings=silence_warnings
    )  # using filler col for subset
    w3 = compute_spatial_weights(
        gdf, id_column, "knn", k=k_values[2], silence_warnings=silence_warnings
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


def compute_spatial_weights(
    gdf, na_columns, w_type, dist=1000, k=6, silence_warnings=False
):
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
        w = weights.distance.DistanceBand.from_array(
            pts, dist, binary=False, silence_warnings=silence_warnings
        )

    elif w_type == "knn":
        w = weights.distance.KNN.from_array(pts, k=k, silence_warnings=silence_warnings)

    elif w_type == "queen":
        w = weights.contiguity.Queen.from_dataframe(
            gdf, use_index=False, silence_warnings=silence_warnings
        )

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


def normalize_data(df, columns):
    for c in columns:
        df[c + "_norm"] = (df[c] - df[c].min()) / (df[c].max() - df[c].min())
    return df


def create_hex_grid(polygon_gdf, hex_resolution, crs, buffer_dist):

    # Inspired by https://stackoverflow.com/questions/51159241/how-to-generate-shapefiles-for-h3-hexagons-in-a-particular-area

    print(f"Creating hexagons at resolution {hex_resolution}...")

    union_poly = (
        polygon_gdf.buffer(buffer_dist).to_crs("EPSG:4326").geometry.unary_union
    )

    # Find the hexagons within the shape boundary using PolyFill
    hex_list = []
    for n, g in enumerate(union_poly.geoms):
        temp = mapping(g)
        temp["coordinates"] = [[[j[1], j[0]] for j in i] for i in temp["coordinates"]]
        hex_list.extend(h3.polyfill(temp, res=hex_resolution))

    # Create hexagon data frame
    hex_pd = pd.DataFrame(hex_list, columns=["hex_id"])

    # Create hexagon geometry and GeoDataFrame
    hex_pd["geometry"] = [
        Polygon(h3.h3_to_geo_boundary(x, geo_json=True)) for x in hex_pd["hex_id"]
    ]

    grid = gpd.GeoDataFrame(hex_pd)

    grid.set_crs("4326", inplace=True).to_crs(crs, inplace=True)

    grid["grid_id"] = grid.hex_id

    return grid


def clean_labels(s):

    s = s.replace(" ", "_")
    s = s.replace(":", "_")
    s = s.replace("/", "_")
    s = s.replace("-", "_")
    s = s.replace("__", "_")

    return s


def label_above_below_mean(gdf, socio_column, bikeability_column):

    socio_cluster_values = gdf[socio_column].unique()
    socio_cluster_values.sort()

    gdf["above_mean"] = False
    gdf["below_mean"] = False

    for socio_label in socio_cluster_values:

        mean = gdf.loc[gdf[socio_column] == socio_label][bikeability_column].mean()
        std_dev = gdf.loc[gdf[socio_column] == socio_label][bikeability_column].std()

        gdf.loc[
            (gdf[socio_column] == socio_label)
            & (gdf[bikeability_column] > mean + std_dev),
            "above_mean",
        ] = True

        gdf.loc[
            (gdf[socio_column] == socio_label)
            & (gdf[bikeability_column] < mean - std_dev),
            "below_mean",
        ] = True

    return gdf


def export_outliers(
    gdf,
    socio_label,
    fp_above,
    fp_below,
    socio_column="socio_label",
    bikeability_column="average_bikeability_rank",
):

    mean = gdf.loc[gdf[socio_column] == socio_label][bikeability_column].mean()
    std_dev = gdf.loc[gdf[socio_column] == socio_label][bikeability_column].std()

    below_mean = gdf[gdf[socio_column] == socio_label].loc[
        gdf[bikeability_column] < mean - std_dev
    ]

    above_mean = gdf[gdf[socio_column] == socio_label].loc[
        gdf[bikeability_column] > mean + std_dev
    ]
    if len(below_mean) > 0:
        below_mean.to_file(fp_below)

    if len(above_mean) > 0:
        above_mean.to_file(fp_above)
