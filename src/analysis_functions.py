import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from pysal.explore import esda
from pysal.lib import weights
from splot.esda import lisa_cluster


def compute_spatial_weights(gdf, na_cols, w_type, dist=1000, k=6):
    """
    Wrapper function for computing the spatial weights for the analysis/results grids.
    ...

    Arguments:
        gdf (geodataframe): geodataframe with polygons
        na_cols (list): list of columns used to drop NA rows. If no rows should be dropped, just use e.g. 'grid_index'
        w_type (str): type of spatial weight to compute. Only supports KNN, distance band or queens.
        dist (numeric): distance to use if distance band
        k (int): number of nearest neighbors if using KNN

    Returns:
        w (pysal spatial weight object): the spatial weight object
    """
    gdf.dropna(subset=na_cols, inplace=True)

    # convert to centroids
    cents = gdf.centroid

    # Extract coordinates into an array
    pts = pd.DataFrame({"X": cents.x, "Y": cents.y}).values

    if w_type == "dist":
        w = weights.distance.DistanceBand.from_array(pts, dist, binary=False)

    elif w_type == "knn":
        w = weights.distance.KNN.from_array(pts, k=k)

    elif w_type == "queen":
        w = weights.contiguity.Queen.from_dataframe(gdf)

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
