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


# make subfolders for results
results_subfolders = [
    "component_density_correlation",
    "component_size_distribution",
    "component_count_maps",
    "density_maps",
    "density_distributions",
    "summary_stats",
    "reach_maps",
    "reach_distributions",
    "reach_density_correlation",
]
for f in results_subfolders:
    if not os.path.exists("results/" + f):
        os.mkdir("results/" + f)

        print("Successfully created folder: results/" + f)


area_folders = ["administrative", "socio", "hexgrid"]

for f in results_subfolders[:5]:

    for a in area_folders:
        if not os.path.exists("results/" + f + "/" + a):
            os.mkdir("results/" + f + "/" + a)

            print("Successfully created folder: results/" + f + "/" + a)

analysis_results_subfolders = ["spatial_autocorrelation", "clustering"]

result_type_subfolders = ["density", "fragmentation", "reach"]

for f in analysis_results_subfolders:
    if not os.path.exists("results/" + f):
        os.mkdir("results/" + f)

        print("Successfully created folder: results/" + f)

        for r in result_type_subfolders:
            if not os.path.exists("results/" + f + "/" + r):
                os.mkdir("results/" + f + "/" + r)

                print("Successfully created folder: results/" + f + "/" + r)

                if r == "fragmentation" or r == "density ":  # no area folders in reach
                    for a in area_folders:
                        if not os.path.exists("results/" + f + "/" + r + "/" + a):
                            os.mkdir("results/" + f + "/" + r + "/" + a)
                            print(
                                "Successfully created folder: results/"
                                + f
                                + "/"
                                + r
                                + "/"
                                + a
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
