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
