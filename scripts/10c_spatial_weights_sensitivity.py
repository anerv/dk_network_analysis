# Compute spatial weights
w_k6 = eval_func.compute_spatial_weights(
    ex_grid_subset, "hex_id_osm", "knn", k=6
)  # using filler col for subset
w_k12 = eval_func.compute_spatial_weights(
    ex_grid_subset, "hex_id_osm", "knn", k=12
)  # using filler col for subset
w_k18 = eval_func.compute_spatial_weights(
    ex_grid_subset, "hex_id_osm", "knn", k=18
)  # using filler col for subset
dist_1000 = eval_func.compute_spatial_weights(
    ex_grid_subset, "hex_id_osm", "dist", dist=1000
)  # using filler col for subset
dist_2000 = eval_func.compute_spatial_weights(
    ex_grid_subset, "hex_id_osm", "dist", dist=2000
)  # using filler col for subset


all_weigths = {
    "k6": w_k6,
    "k12": w_k12,
    "k18": w_k18,
    "dist1000": dist_1000,
    "dist2000": dist_2000,
}


# dictionaries for results
all_morans = {}
all_lisas = {}
hotspot_count = {}
coldspot_count = {}

for name, w in all_weigths.items():
    morans_density = eval_func.compute_spatial_autocorrelation(
        col_names, variable_names, ex_grid_subset, w, filepaths
    )

    all_morans[name] = morans_density["edge_density"].I

    col_names = ["edge_density_diff"]
    variable_names = ["edge_density"]
    filepaths = [compare_analysis_plots_fp + f"lisa_edge_dens_{name}.png"]

    lisas_density = eval_func.compute_lisa(
        col_names, variable_names, ex_grid_subset, w, filepaths
    )

    all_lisas[name] = lisas_density["edge_density"]

    # Export
    q_cols = [v + "_q" for v in variable_names]
    q_cols.append("hex_id")
    ex_grid_subset.rename({"hex_id_osm": "hex_id"}, axis=1)[q_cols].to_csv(
        compare_analysis_data_fp + f"density_spatial_autocorrelation_{name}.csv",
        index=True,
    )

    for v in variable_names:
        hotspot = len(ex_grid_subset[ex_grid_subset[f"{v}_q"] == "HH"])
        coldspot = len(ex_grid_subset[ex_grid_subset[f"{v}_q"] == "LL"])

        print(
            f"Using spatial weights {name}, for '{v}', {hotspot} out of {len(ex_grid_subset)} grid cells ({hotspot/len(ex_grid_subset)*100:.2f}%) are part of a hotspot."
        )
        print(
            f"Using spatial weights {name}, for '{v}', {coldspot} out of {len(ex_grid_subset)} grid cells ({coldspot/len(ex_grid_subset)*100:.2f}%) are part of a coldspot."
        )
        print("\n")

        hotspot_count[name] = hotspot
        coldspot_count[name] = coldspot


fig = plt.figure(figsize=(10, 5))

# creating the bar plot
plt.bar(all_morans.keys(), all_morans.values(), color="#AA336A", width=0.4)

plt.xlabel("Spatial weights")
plt.ylabel("Moran's I")
plt.title("Comparison of global spatial autocorrelation from different spatial weights")
plt.show()


fig = plt.figure(figsize=(10, 5))

# creating the bar plot
plt.bar(hotspot_count.keys(), hotspot_count.values(), color="#916E99", width=0.4)

plt.xlabel("Spatial weights")
plt.ylabel("Number of grid cells in hot spot")
plt.title("Comparison of edges in hot spot from different spatial weights")
plt.show()

fig = plt.figure(figsize=(10, 5))

# creating the bar plot
plt.bar(coldspot_count.keys(), coldspot_count.values(), color="#658CBB", width=0.4)

plt.xlabel("Spatial weights")
plt.ylabel("Number of grid cells in cold spot")
plt.title("Comparison of edges in cold spots from different spatial weights")
plt.show()
