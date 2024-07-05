import matplotlib as mpl
from matplotlib import cm, colors
import seaborn as sns

sns.set_theme(style="white")

import matplotlib_inline.backend_inline


# Plot parameters
mpl.rcParams["savefig.bbox"] = "tight"
mpl.rcParams["xtick.minor.visible"] = False
mpl.rcParams["xtick.major.size"] = 0
mpl.rcParams["xtick.labelbottom"] = True
mpl.rcParams["ytick.major.size"] = 3
mpl.rcParams["font.size"] = 10
mpl.rcParams["figure.titlesize"] = 10
mpl.rcParams["legend.title_fontsize"] = 10
mpl.rcParams["legend.fontsize"] = 9
# mpl.rcParams["figure.labelsize"] = 10 # use if figure.titlesize does not work?
mpl.rcParams["axes.labelsize"] = 10
mpl.rcParams["xtick.labelsize"] = 9
mpl.rcParams["ytick.labelsize"] = 9
mpl.rcParams["hatch.linewidth"] = 0.5

# Classification scheme for visualizations of results
scheme = "fisherjenks"
# number of classes in classification scheme
k = 5

labels = ["LTS 1", "LTS 2", "LTS 3", "LTS 4", "Total car"]
labels_all = ["LTS 1", "LTS 2", "LTS 3", "LTS 4", "Total car", "Total network"]

labels_step = [
    "LTS 1",
    "LTS 1-2",
    "LTS 1-3",
    "LTS 1-4",
    "Total car",
]
labels_step_all = [
    "LTS 1",
    "LTS 1-2",
    "LTS 1-3",
    "LTS 1-4",
    "Total car",
    "Total network",
]


labels_pct = [
    "LTS 1 (%)",
    "LTS 2 (%)",
    "LTS 3 (%)",
    "LTS 4 (%)",
    "Total car (%)",
]
labels_pct_step = [
    "LTS 1 (%)",
    "LTS 1-2 (%)",
    "LTS 1-3 (%)",
    "LTS 1-4 (%)",
    "Total car (%)",
]

network_levels = ["lts1", "lts2", "lts3", "lts4", "car"]
network_levels_step = ["lts1", "lts1_2", "lts1_3", "lts1_4", "car"]


id_columns = ["municipality", "id", "hex_id"]
aggregation_levels = ["administrative", "socio", "hexgrid"]

lts_color_dict = {
    "1": "#0B7512",
    "2": "#7ABA78",
    "3": "#FFC100",
    "4": "#F97300",
    "car": "#5c5c5c",
    "total": "#151515",
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
    "households_income_under_100k_share": "Income under 100k (share)",
    "households_income_100_150k_share": "Income 100-150k (share)",
    "households_income_150_200k_share": "Income 150-200k (share)",
    "households_income_200_300k_share": "Income 200-300k (share)",
    "households_income_300_400k_share": "Income 300-400k (share)",
    "households_income_400_500k_share": "Income 400-500k (share)",
    "households_income_500_750k_share": "Income 500-750k (share)",
    "households_income_750k_share": "Income 750k (share)",
    "households_with_car_share": "Households w car (share)",
    "households_1car_share": "Households 1 car (share)",
    "households_2cars_share": "Households 2 cars (share)",
    "households_nocar_share": "Households no car (share)",
}


socio_corr_variables = [
    "Income under 100k (share)",
    "Income 100-150k (share)",
    "Income 150-200k (share)",
    "Income 200-300k (share)",
    "Income 300-400k (share)",
    "Income 400-500k (share)",
    "Income 500-750k (share)",
    "Income 750k (share)",
    "Households w car (share)",
    "Households 1 car (share)",
    "Households 2 cars (share)",
    "Households no car (share)",
    "population_density",
    "urban_pct",
]

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

pdict = {
    # grid; polygon; base barplots
    "base": "black",
    "base2": "grey",
    "compare_base": "black",  # "dimgray",
    # colormaps for grid cell plots
    "pos": "PuRd",  # "Blues",  # Positive values
    "neg": "YlOrdRd",  # "Reds",  # Negative/Missing/Unmatched values
    "diff": "RdBu",  # for osm-ref difference plots (alternatives: "PiYG", "PRGn", "PuOr")
    "seq": "YlGnBu",  # for sequential plots where low should not be white (usually percentages)
    # alpha (transparency) values (alternatives: PuRd, RdPu, PbBuGn)
    "alpha_back": 0.5,  # for unicolor plots with relevant background
    "alpha_bar": 0.7,  # for partially overlapping stats barplots
    "alpha_grid": 0.9,  # for multicolor/divcolor gridplots
    "alpha_nodata": 0.3,  # for no data patches
    # linewidths (base, emphasis, emphasis2)
    # "line_base": 1,
    # "line_emp": 3,
    # "line_emp2": 5,
    "line_nodata": 0.3,
    # widths for bar plots; single: for 1 value, double: for 2 values comparison
    "bar_single": 0.4,
    "bar_double": 0.75,
    # marker sizes (base, emphasis)
    # "mark_base": 2,
    # "mark_emp": 6,
    # Colors of no-data grid cell patches
    "nodata": "lightgrey",
    # "nodata_face": "none",
    # "nodata_edge": "grey",
    # "nodata_hatch": "//",
    # GLOBAL SETTINGS FOR PLOTS
    "dpi": 300,  # resolution
    "plot_res": "low",  # "high" for exporting to svg, "low" for png
    # matplotlib figure size for map plots of study area
    "fsmap": (13, 7.3125),
    # size for bar plots
    "fsbar": (8, 8),
    "fsbar_small": (4, 3.5),
    "fsbar_short": (6, 3),
    "fsbar_sub": (4, 3),  # size per subplot
    "map_attr": "OSM Contributors, GeoDanmark",
    "background_color": "#e0ecf4",
}

import contextily as cx

cx_tile_1 = cx.providers.CartoDB.Voyager
cx_tile_2 = cx.providers.CartoDB.PositronNoLabels  # CartoDB.DarkMatterNoLabels

rename_index_dict_density = {
    "lts_1_dens": "LTS 1 density",
    "lts_2_dens": "LTS 2 density",
    "lts_3_dens": "LTS 3 density",
    "lts_4_dens": "LTS 4 density",
    "total_car_dens": "Car density",
    "total_network_dens": "Total density",
    "lts_1_2_dens": "LTS 1-2 density",
    "lts_1_3_dens": "LTS 1-3 density",
    "lts_1_4_dens": "LTS 1-4 density",
    "lts_1_pct": "LTS 1 %",
    "lts_2_pct": "LTS 2 %",
    "lts_3_pct": "LTS 3 %",
    "lts_4_pct": "LTS 4 %",
    "total_car_pct": "Car %",
    "lts_1_2_pct": "LTS 1-2 %",
    "lts_1_3_pct": "LTS 1-3 %",
    "lts_1_4_pct": "LTS 1-4 %",
}

rename_index_dict_fragmentation = {
    "component_1_count": "Component count LTS 1",
    "component_1_2_count": "Component count LTS 1-2",
    "component_1_3_count": "Component count LTS 1-3",
    "component_1_4_count": "Component count LTS 1-4",
    "component_car_count": "Component count car",
    "component_all_count": "Component count full",
    "component_per_length_1": "Components per km LTS 1",
    "component_per_length_1_2": "Components per km LTS 1-2",
    "component_per_length_1_3": "Components per km LTS 1-3",
    "component_per_length_1_4": "Components per km LTS 1-4",
    "component_per_length_car": "Components per km car",
    "component_per_length_all": "Components per km full",
    "component_per_dens_1": "Components per km/sqkm LTS 1",
    "component_per_dens_1_2": "Components per km/sqkm LTS 1-2",
    "component_per_dens_1_3": "Components per km/sqkm LTS 1-3",
    "component_per_dens_1_4": "Components per km/sqkm LTS 1-4",
    "component_per_dens_car": "Components per km/sqkm car",
    "component_per_dens_all": "Components per km/sqkm all",
}

rename_index_dict_reach = {
    "lts_1_reach": "LTS 1 reach",
    "lts_1_2_reach": "LTS 1-2 reach",
    "lts_1_3_reach": "LTS 1-3 reach",
    "lts_1_4_reach": "LTS 1-4 reach",
    "car_reach": "Car reach",
    "car_lts_1_diff": "Difference car-LTS 1 reach",
    "car_lts_1_2_diff": "Difference car-LTS 1-2 reach",
    "car_lts_1_3_diff": "Difference car-LTS 1-3 reach",
    "car_lts_1_4_diff": "Difference car-LTS 1-4 reach",
    "car_lts_1_diff_pct": "Difference car-LTS 1 reach %",
    "car_lts_1_2_diff_pct": "Difference car-LTS 1-2 reach %",
    "car_lts_1_3_diff_pct": "Difference car-LTS 1-3 reach %",
    "car_lts_1_4_diff_pct": "Difference car-LTS 1-4 reach %",
}

rename_index_dict_largest_comp = {
    "component_length_1": "LTS 1 largest component length",
    "component_length_1_2": "LTS 1-2 largest component length",
    "component_length_1_3": "LTS 1-3 largest component length",
    "component_length_1_4": "LTS 1-4 largest component length",
    "component_length_car": "Car largest component length",
    # "component_coverage_1": "LTS 1 largest component coverage",
    # "component_coverage_1_2": "LTS 2 largest component coverage",
    # "component_coverage_1_3": "LTS 3 largest component coverage",
    # "component_coverage_1_4": "LTS 4 largest component coverage",
    # "component_coverage_car": "Car largest component coverage",
}
