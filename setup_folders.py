# Run this file while in the main folder
import os

parent_folders = ["data", "results"]

for f in parent_folders:
    if not os.path.exists(f):
        os.mkdir(f)

        print("Successfully created folder: " + f)

# make subfolders for data
data_subfolders = ["input", "processed"]
for f in data_subfolders:
    if not os.path.exists("data/" + f):
        os.mkdir("data/" + f)

# Make input data subfolders
data_subsubfolders = [
    "municipalities",
    "population",
    "socioeconomic",
    "urban",
]

for f in data_subsubfolders:
    if not os.path.exists("data/input/" + f):
        os.mkdir("data/input/" + f)

        print("Successfully created folder: data/input/" + f)

# make subfolders for results

results_subfolders = [
    "density_maps",
    "density_plots",
    "component_maps",
    "component_plots",
    "correlation",
    "reach_maps",
    "reach_plots",
    "summary_stats",
    "spatial_autocorrelation",
    "clustering",
]

for f in results_subfolders:
    if not os.path.exists("results/" + f):
        os.mkdir("results/" + f)

        print("Successfully created folder: results/" + f)

area_folders = ["municipal", "socio", "hexgrid"]

for f in results_subfolders[:5]:

    for a in area_folders:
        if not os.path.exists("results/" + f + "/" + a):
            os.mkdir("results/" + f + "/" + a)

            print("Successfully created folder: results/" + f + "/" + a)

# make subfolders for clustering results
clustering_subfolders = ["plots", "maps", "data"]

for f in clustering_subfolders:
    if not os.path.exists("results/clustering/" + f):
        os.mkdir("results/clustering/" + f)

        print("Successfully created folder: results/clustering/" + f)


result_type_subfolders = ["density", "fragmentation", "reach"]

f = "spatial_autocorrelation"
for r in result_type_subfolders:
    if not os.path.exists("results/" + f + "/" + r):
        os.mkdir("results/" + f + "/" + r)

        print("Successfully created folder: results/" + f + "/" + r)

        if r in ("fragmentation", "density"):  # no muni or socio folders in reach
            for a in area_folders:
                if not os.path.exists("results/" + f + "/" + r + "/" + a):
                    os.mkdir("results/" + f + "/" + r + "/" + a)
                    print(
                        "Successfully created folder: results/" + f + "/" + r + "/" + a
                    )
        elif r == "reach":
            if not os.path.exists("results/" + f + "/" + r + "/" + "hexgrid"):
                os.mkdir("results/" + f + "/" + r + "/" + "hexgrid")
                print(
                    "Successfully created folder: results/"
                    + f
                    + "/"
                    + r
                    + "/"
                    + "hexgrid"
                )

fp = "results/spatial_autocorrelation/sensitivity_test"
if not os.path.exists(fp):
    os.mkdir(fp)

    print("Successfully created folder: " + fp)


fp = "results/spatial_autocorrelation/socio_pop"
if not os.path.exists(fp):
    os.mkdir(fp)

    print("Successfully created folder: " + fp)


# # make illustration folder
# if not os.path.exists("illustrations"):
#     os.mkdir("illustrations")

#     print("Successfully created folder: illustrations")
