import matplotlib as mpl
from matplotlib import cm, colors
import seaborn as sns

sns.set_theme(style="white")

import matplotlib_inline.backend_inline

pdict = {
    # colormaps for grid cell plots
    "dens": "viridis",
    "reach": "YlGnBu",
    "dens_rel": "PuRd",
    "frag": "viridis",
    "largest_comp": "viridis_r",
    "cat": "Set2",  # for categorical plots
    # alpha (transparency) values (alternatives: PuRd, RdPu, PbBuGn)
    "alpha": 0.8,
    "alpha_nodata": 0.7,  # for no data patches
    # Colors of no-data
    "nodata": "darkgrey",  # "xkcd:putty",  # "xkcd:taupe",  # "tan",  # "silver",
    # GLOBAL SETTINGS FOR PLOTS
    "dpi": 300,  # resolution
    # matplotlib figure size for map plots of entire study area
    "fsmap": (13, 7.3125),
    # size for bar plots
    "fsbar": (8, 8),
    "fsbar_sub": (16, 8),
    "map_attr": "OSM Contributors, GeoDanmark",
    "background_color": None,  # "#e0ecf4",
    "legend_fs": 10,
    "title_fs": 12,
    "legend_title_fs": 12,
    "fontsize": 10,
    "ax_fs": 12,
    "fsmap_subs": (10, 15),
    "map_title_fs": 14,
    "map_fs": 10,
    "map_legend_fs": 12,
    "fs_subplot": 11,
}

# Plot parameters
mpl.rcParams["savefig.bbox"] = "tight"
mpl.rcParams["xtick.minor.visible"] = False
mpl.rcParams["xtick.major.size"] = 0
mpl.rcParams["xtick.labelbottom"] = True
mpl.rcParams["ytick.major.size"] = 3
mpl.rcParams["ytick.minor.visible"] = False
mpl.rcParams["font.size"] = pdict["fontsize"]
mpl.rcParams["figure.titlesize"] = pdict["title_fs"]
mpl.rcParams["legend.title_fontsize"] = pdict["legend_title_fs"]
mpl.rcParams["legend.fontsize"] = pdict["legend_fs"]
# mpl.rcParams["figure.labelsize"] = 10 # use if figure.titlesize does not work?
mpl.rcParams["axes.labelsize"] = pdict["ax_fs"]
mpl.rcParams["xtick.labelsize"] = 9
mpl.rcParams["ytick.labelsize"] = 9
mpl.rcParams["hatch.linewidth"] = 0.5
mpl.style.use("tableau-colorblind10")

import contextily as cx

labels = ["LTS 1", "LTS 2", "LTS 3", "LTS 4", "Car"]
labels_all = ["LTS 1", "LTS 2", "LTS 3", "LTS 4", "Car", "Total network"]

labels_step = [
    "LTS 1",
    "LTS ≤ 2",
    "LTS ≤ 3",
    "LTS ≤ 4",
    "Car",
]
labels_step_all = [
    "LTS 1",
    "LTS ≤ 2",
    "LTS ≤ 3",
    "LTS ≤ 4",
    "Car",
    "Total network",
]

labels_pct = [
    "LTS 1 (%)",
    "LTS 2 (%)",
    "LTS 3 (%)",
    "LTS 4 (%)",
    "Car (%)",
]
labels_pct_step = [
    "LTS 1 (%)",
    "LTS ≤ 2 (%)",
    "LTS ≤ 3 (%)",
    "LTS ≤ 4 (%)",
    "Car (%)",
]

network_levels = ["lts1", "lts2", "lts3", "lts4", "car"]
network_levels_step = ["lts_1", "lts_1_2", "lts_1_3", "lts_1_4", "car"]


id_columns = ["municipality", "id", "hex_id"]
aggregation_levels = ["municipal", "socio", "hexgrid"]

lts_color_dict = {
    "1": "#117733",  # "#0B7512",
    "2": "#44AA99",  # "#7ABA78",
    "3": "#DDCC77",  # "#FFC100",
    "4": "#CC6677",  # "#F97300",
    "car": "#882255",  # "#5c5c5c",
    "total": "#151515",
}

bikeability_cluster_color_dict_labels = {
    "1: High stress": lts_color_dict["car"],
    "2: Local low stress connectivity": lts_color_dict["4"],
    "3: Regional low stress connectivity": lts_color_dict["3"],
    "4: High bikeability": lts_color_dict["2"],
    "5: Highest bikeability and high density": lts_color_dict["1"],
}

bikeability_cluster_color_dict = {
    "1": bikeability_cluster_color_dict_labels["1: High stress"],
    "2": bikeability_cluster_color_dict_labels["2: Local low stress connectivity"],
    "3": bikeability_cluster_color_dict_labels["3: Regional low stress connectivity"],
    "4": bikeability_cluster_color_dict_labels["4: High bikeability"],
    "5": bikeability_cluster_color_dict_labels[
        "5: Highest bikeability and high density"
    ],
}

socio_cluster_colors_dict = {
    "1: High income - 2 cars": "#EE8866",  # orange
    "2: Very high income - 2 cars": "#FFAABB",  # pink
    "3: Medium income - high car": "#BBCC33",  # pear
    "4: Medium/high income - medium car": "#AAAA00",  # olive
    "5: Medium/low income - 1 car": "#44BB99",  # mint
    "6: Very low income - low car": "#99DDFF",  # light cyan
    "7: Medium income - very low car": "#77AADD",  # light blue
}


# socio_cluster_colors_dict = {
#     "1: High income - 2 cars": "#77AADD",  # light blue
#     "2: Very high income - 2 cars": "#99DDFF",  # light cyan
#     "3: Medium income - high car": "#44BB99",  # mint
#     "4: Medium/high income - medium car": "#AAAA00",  # olive
#     "5: Medium/low income - 1 car": "#BBCC33",  # pear
#     "6: Very low income - low car": "#FFAABB",  # pink
#     "7: Medium income - very low car": "#EE8866",  # orange
# }

distance_color_dict = {
    "1": "#DDCC77",  # "#94CBEC",
    "2": "#999933",  # 44AA99",
    "5": "#88CCEE",  # "#DDCC77",
    "10": "#44AA99",  # "#CC6677",
    "15": "#117733",  # "#882255",
}

component_columns = [
    "component_all",
    "component_1",
    "component_1_2",
    "component_1_3",
    "component_1_4",
    "component_car",
]

length_columns = [
    "lts_1_length",
    "lts_2_length",
    "lts_3_length",
    "lts_4_length",
    "total_car_length",
    "total_network_length",
]

length_steps_columns = [
    "lts_1_length",
    "lts_1_2_length",
    "lts_1_3_length",
    "lts_1_4_length",
    "total_car_length",
    "total_network_length",
]

length_relative_steps_columns = [
    "lts_1_pct",
    "lts_1_2_pct",
    "lts_1_3_pct",
    "lts_1_4_pct",
    "total_car_pct",
]

length_relative_columns = [
    "lts_1_pct",
    "lts_2_pct",
    "lts_3_pct",
    "lts_4_pct",
    "total_car_pct",
]

density_columns = [
    "lts_1_dens",
    "lts_2_dens",
    "lts_3_dens",
    "lts_4_dens",
    "total_car_dens",
    "total_network_dens",
]

density_steps_columns = [
    "lts_1_dens",
    "lts_1_2_dens",
    "lts_1_3_dens",
    "lts_1_4_dens",
    "total_car_dens",
    "total_network_dens",
]

component_count_columns = [
    "component_1_count",
    "component_1_2_count",
    "component_1_3_count",
    "component_1_4_count",
    "component_car_count",
    "component_all_count",
]

component_per_km_columns = [
    "component_per_length_1",
    "component_per_length_1_2",
    "component_per_length_1_3",
    "component_per_length_1_4",
    "component_per_length_car",
    "component_per_length_all",
]

component_per_km_sqkm_columns = [
    "component_per_dens_1",
    "component_per_dens_1_2",
    "component_per_dens_1_3",
    "component_per_dens_1_4",
    "component_per_dens_car",
    "component_per_dens_all",
]

largest_local_component_len_columns = [
    "component_length_1",
    "component_length_1_2",
    "component_length_1_3",
    "component_length_1_4",
    "component_length_car",
]

largest_local_component_area_columns = [
    "component_coverage_1",
    "component_coverage_1_2",
    "component_coverage_1_3",
    "component_coverage_1_4",
    "component_coverage_car",
]

socio_largest_component_columns_ave = [
    "lts_1_largest_component_average",
    "lts_1_2_largest_component_average",
    "lts_1_3_largest_component_average",
    "lts_1_4_largest_component_average",
    "car_largest_component_average",
]

socio_largest_component_columns_max = [
    "lts_1_largest_component_max",
    "lts_1_2_largest_component_max",
    "lts_1_3_largest_component_max",
    "lts_1_4_largest_component_max",
    "car_largest_component_max",
]

socio_largest_component_columns_median = [
    "lts_1_largest_component_median",
    "lts_1_2_largest_component_median",
    "lts_1_3_largest_component_median",
    "lts_1_4_largest_component_median",
    "car_largest_component_median",
]

socio_largest_component_columns_min = [
    "lts_1_largest_component_min",
    "lts_1_2_largest_component_min",
    "lts_1_3_largest_component_min",
    "lts_1_4_largest_component_min",
    "car_largest_component_min",
]

reach_columns = [
    "lts_1_reach",
    "lts_1_2_reach",
    "lts_1_3_reach",
    "lts_1_4_reach",
    "car_reach",
]

reach_diff_columns = [
    "car_lts_1_diff",
    "car_lts_1_2_diff",
    "car_lts_1_3_diff",
    "car_lts_1_4_diff",
]
reach_diff_pct_columns = [
    "car_lts_1_diff_pct",
    "car_lts_1_2_diff_pct",
    "car_lts_1_3_diff_pct",
    "car_lts_1_4_diff_pct",
]

socio_reach_average_columns = [
    "lts_1_reach_average",
    "lts_1_2_reach_average",
    "lts_1_3_reach_average",
    "lts_1_4_reach_average",
    "car_reach_average",
]

socio_reach_median_columns = [
    "lts_1_reach_median",
    "lts_1_2_reach_median",
    "lts_1_3_reach_median",
    "lts_1_4_reach_median",
    "car_reach_median",
]

socio_reach_max_columns = [
    "lts_1_reach_max",
    "lts_1_2_reach_max",
    "lts_1_3_reach_max",
    "lts_1_4_reach_max",
    "car_reach_max",
]

population_rename_dict = {
    "-17_pct": "0-17 years (%)",
    "18-29_pct": "18-29 years (%)",
    "30-39_pct": "30-39 years (%)",
    "40-49_pct": "40-49 years (%)",
    "50-59_pct": "50-59 years (%)",
    "60-69_pct": "60-69 years (%)",
    "70-_pct": "70+ years (%)",
    "student_pct": "Students (%)",
    "households_income_under_150k_pct": "Income under 150k (%)",
    "households_income_under_100k_pct": "Income under 100k (%)",
    "households_income_100_150k_pct": "Income 100-150k (%)",
    "households_income_150_200k_pct": "Income 150-200k (%)",
    "households_income_200_300k_pct": "Income 200-300k (%)",
    "households_income_300_400k_pct": "Income 300-400k (%)",
    "households_income_400_500k_pct": "Income 400-500k (%)",
    "households_income_500_750k_pct": "Income 500-750k (%)",
    "households_income_750k_pct": "Income 750k+ (%)",
    "households_with_car_pct": "Households w car (%)",
    "households_1car_pct": "Households 1 car (%)",
    "households_2cars_pct": "Households 2 cars (%)",
    "households_nocar_pct": "Households no car (%)",
    "households_income_50_percentile": "Household income 50th percentile",
    "households_income_80_percentile": "Household income 80th percentile",
    "population_density": "Population density",
    "urban_pct": "Urban area (%)",
}

socio_corr_variables = [
    "0-17 years (%)",
    "18-29 years (%)",
    "30-39 years (%)",
    "40-49 years (%)",
    "50-59 years (%)",
    "60-69 years (%)",
    "70+ years (%)",
    "Students (%)",
    "Income under 150k (%)",
    # "Income under 100k (%)",
    # "Income 100-150k (%)",
    "Income 150-200k (%)",
    "Income 200-300k (%)",
    "Income 300-400k (%)",
    "Income 400-500k (%)",
    "Income 500-750k (%)",
    "Income 750k+ (%)",
    "Household income 50th percentile",
    "Household income 80th percentile",
    "Households w car (%)",
    "Households 1 car (%)",
    "Households 2 cars (%)",
    "Households no car (%)",
    "Population density",
    "Urban area (%)",
]

socio_age_vars = socio_corr_variables[:7]
socio_income_vars = socio_corr_variables[7:17]
socio_car_vars = socio_corr_variables[17:21]
socio_urban_pop_vars = socio_corr_variables[21:]
socio_car_pop = socio_corr_variables[17:]

plotly_labels = {
    "lts_1_dens": "LTS 1 density (km/sqkm)",
    "lts_2_dens": "LTS 2 density (km/sqkm)",
    "lts_3_dens": "LTS 3 density (km/sqkm)",
    "lts_4_dens": "LTS 4 density (km/sqkm)",
    "lts_1_2_dens": "LTS 1-2 density (km/sqkm)",
    "lts_1_3_dens": "LTS 1-3 density (km/sqkm)",
    "lts_1_4_dens": "LTS 1-4 density (km/sqkm)",
    "total_car_dens": "Total car density (km/sqkm)",
    "total_network_dens": "Total network density (km/sqkm)",
    "lts_1_length": "LTS 1 length (km)",
    "lts_1_2_length": "LTS 1-2 length (km)",
    "lts_1_3_length": "LTS 1-3 length (km)",
    "lts_1_4_length": "LTS 1-4 length (km)",
    "lts_1_length": "LTS 1 length (km)",
    "lts_2_length": "LTS 2 length (km)",
    "lts_3_length": "LTS 3 length (km)",
    "lts_4_length": "LTS 4 length (km)",
    "total_car_length": "Total car length (km)",
    "total_network_length": "Total network length (km)",
    "component_1_count": "LTS 1 component count",
    "component_1_2_count": "LTS 1-2 component count",
    "component_1_3_count": "LTS 1-3 component count",
    "component_1_4_count": "LTS 1-4 component count",
    "component_car_count": "Total car component count",
    "component_all_count": "Total network component count",
    "density": "Density (km/sqkm)",
    "length": "Length (km)",
    "lts": "LTS",
    "component_count": "Component count",
    "all": "All",
    "car": "Car",
    "municipality": "Municipality",
    "lts_1_reach": "Network reach (km) - LTS 1",
    "lts_1_2_reach": "Network reach (km) - LTS 2",
    "lts_1_3_reach": "Network reach (km) - LTS 3",
    "lts_1_4_reach": "Network reach (km) - LTS 4",
    "car_reach": "Network reach (km) - car",
    "car_lts_1_diff": "Difference in network reach (km)",
    "car_lts_1_2_diff": "Difference in network reach (km)",
    "car_lts_1_3_diff": "Difference in network reach (km)",
    "car_lts_1_4_diff": "Difference in network reach (km)",
    "car_lts_1_diff_pct": "Difference in network reach (%)",
    "car_lts_1_2_diff_pct": "Difference in network reach (%)",
    "car_lts_1_3_diff_pct": "Difference in network reach (%)",
    "car_lts_1_4_diff_pct": "Difference in network reach (%)",
}

rename_index_dict_density = {
    "lts_1_dens": "Density - LTS 1",
    "lts_2_dens": "Density - LTS 2",
    "lts_3_dens": "Density - LTS 3",
    "lts_4_dens": "Density - LTS 4",
    "total_car_dens": "Density - car ",
    "total_network_dens": "Density - total network",
    "lts_1_2_dens": "Density - LTS 1-2",
    "lts_1_3_dens": "Density - LTS 1-3",
    "lts_1_4_dens": "Density - LTS 1-4",
    "lts_1_pct": "Share of network - LTS 1 (%)",
    "lts_2_pct": "Share of network - LTS 2 (%)",
    "lts_3_pct": "Share of network - LTS 3 (%)",
    "lts_4_pct": "Share of network - LTS 4 (%)",
    "total_car_pct": "Share of network - car (%)",
    "lts_1_2_pct": "Share of network - LTS 1-2 (%)",
    "lts_1_3_pct": "Share of network - LTS 1-3 (%)",
    "lts_1_4_pct": "Share of network - LTS 1-4 (%)",
}

rename_index_dict_fragmentation = {
    "component_1_count": "Component count  - LTS 1",
    "component_1_2_count": "Component count - LTS ≤ 2",
    "component_1_3_count": "Component count - LTS ≤m3",
    "component_1_4_count": "Component count - LTS ≤ 4",
    "component_car_count": "Component count - car",
    "component_all_count": "Component count - total network",
    "component_per_length_1": "Components per km LTS 1",
    "component_per_length_1_2": "Components per km - LTS ≤ 2",
    "component_per_length_1_3": "Components per km - LTS ≤ 3",
    "component_per_length_1_4": "Components per km - LTS ≤ 4",
    "component_per_length_car": "Components per km - car",
    "component_per_length_all": "Components per km - total network",
    "component_per_dens_1": "Components per km/sqkm - LTS 1",
    "component_per_dens_1_2": "Components per km/sqkm - LTS ≤ 2",
    "component_per_dens_1_3": "Components per km/sqkm - LTS ≤ 3",
    "component_per_dens_1_4": "Components per km/sqkm - LTS ≤ 4",
    "component_per_dens_car": "Components per km/sqkm - car",
    "component_per_dens_all": "Components per km/sqkm - all",
}

rename_index_dict_reach = {
    "lts_1_reach": "Reach - LTS 1",
    "lts_1_2_reach": "Reach - LTS ≤ 2",
    "lts_1_3_reach": "Reach - LTS ≤ 3",
    "lts_1_4_reach": "Reach - LTS ≤ 4",
    "car_reach": "Reach - car",
    "car_lts_1_diff": "Reach diff. car - LTS 1",
    "car_lts_1_2_diff": "Reach diff. car - LTS ≤ 2",
    "car_lts_1_3_diff": "Reach diff. car - LTS ≤ 3",
    "car_lts_1_4_diff": "Reach diff. car - LTS ≤ 4",
    "car_lts_1_diff_pct": "Reach diff. car - LTS 1 (%)",
    "car_lts_1_2_diff_pct": "Reach diff. car - LTS ≤ 2 (%)",
    "car_lts_1_3_diff_pct": "Reach diff. car - LTS ≤ 3 (%)",
    "car_lts_1_4_diff_pct": "Reach diff. car - LTS ≤ 4 (%)",
}

rename_index_dict_largest_comp = {
    "component_length_1": "Largest component length - LTS 1",
    "component_length_1_2": "Largest component length - LTS ≤ 2",
    "component_length_1_3": "Largest component length - LTS ≤ 3",
    "component_length_1_4": "Largest component length - LTS ≤ 4",
    "component_length_car": "Largest component length - car",
    # "component_coverage_1": "LTS 1 largest component coverage",
    # "component_coverage_1_2": "LTS 2 largest component coverage",
    # "component_coverage_1_3": "LTS 3 largest component coverage",
    # "component_coverage_1_4": "LTS 4 largest component coverage",
    # "component_coverage_car": "Car largest component coverage",
}

rename_hex_reach_dict = {
    "lts_1_pct_diff_1_5": "Diff. 1-5 km reach - LTS 1 (%)",
    "lts_1_pct_diff_5_10": "Diff. 5-10 km reach - LTS 1 (%)",
    "lts_1_2_pct_diff_1_5": "Diff. 1-5 km reach - LTS ≤ 2 (%)",
    "lts_1_2_pct_diff_5_10": "Diff. 5-10 km reach - LTS ≤ 2 (%)",
    "lts_1_3_pct_diff_1_5": "Diff. 1-5 km reach - LTS ≤ 3 (%)",
    "lts_1_3_pct_diff_5_10": "Diff. 5-10 km reach - LTS ≤ 3 (%)",
    "lts_1_4_pct_diff_1_5": "Diff. 1-5 km reach - LTS ≤ 4 (%)",
    "lts_1_4_pct_diff_5_10": "Diff. 5-10 km reach - LTS ≤ 4 (%)",
    "car_pct_diff_1_5": "Diff. 1-5 km reach - car (%)",
    "car_pct_diff_5_10": "Diff. 5-10 km reach - car (%)",
}

rename_socio_reach_dict = {
    "lts_1_pct_diff_1_5_median": "Diff. 1-5 km reach - LTS 1 (%) (median)",
    "lts_1_pct_diff_5_10_median": "Diff. 5-10 km reach - LTS 1 (%) (median)",
    "lts_1_2_pct_diff_1_5_median": "Diff. 1-5 km reach - LTS ≤ 2 (%) (median)",
    "lts_1_2_pct_diff_5_10_median": "Diff. 5-10 km reach - LTS ≤ 2 (%) (median)",
    "lts_1_3_pct_diff_1_5_median": "Diff. 1-5 km reach - LTS ≤ 3 (%) (median)",
    "lts_1_3_pct_diff_5_10_median": "Diff. 5-10 km reach - LTS ≤ 3 (%) (median)",
    "lts_1_4_pct_diff_1_5_median": "Diff. 1-5 km reach - LTS ≤ 4 (%) (median)",
    "lts_1_4_pct_diff_5_10_median": "Diff. 5-10 km reach - LTS ≤ 4 (%) (median)",
    "car_pct_diff_1_5_median": "Diff. 1-5 km reach - car (%) (median)",
    "car_pct_diff_5_10_median": "Diff. 5-10 km reach - car (%) (median)",
    "urban_pct": "Urban area (%)",
    "lts_1_largest_component_median": "Largest component LTS 1 (median)",
    "lts_1_2_largest_component_median": "Largest component - LTS ≤ 2 (median)",
    "lts_1_3_largest_component_median": "Largest component - LTS ≤ 3 (median)",
    "lts_1_4_largest_component_median": "Largest component - LTS ≤ 4 (median)",
    "car_largest_component_median": "Largest component - car (median)",
    "lts_1_reach_median": "Reach - LTS 1 (median)",
    "lts_1_2_reach_median": "Reach - LTS ≤ 2 (median)",
    "lts_1_3_reach_median": "Reach - LTS ≤ 3 (median)",
    "lts_1_4_reach_median": "Reach - LTS ≤ 4 (median)",
    "car_reach_median": "Reach - car (median)",
}


reach_comparisons = [
    "1_5",
    "5_10",
]  # "10_15"
