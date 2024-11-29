# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd
from IPython.display import display
import seaborn as sns

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/df_styler.py").read())
exec(open("../settings/filepaths.py").read())

plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

# %%

socio_hex_cluster = gpd.read_postgis(
    "SELECT * FROM clustering.socio_socio_clusters", engine, geom_col="geometry"
)
socio_hex_cluster.fillna(0, inplace=True)

exec(open("../helper_scripts/read_socio_pop.py").read())

# %%
socio_socio = socio.merge(socio_hex_cluster, on="id")

socio_socio = socio_socio.drop(columns=["geometry_x", "geometry_y"])

assert len(socio_socio) == len(socio) == len(socio_hex_cluster)
# %%

socio_bikeability_cols = [c for c in socio_socio.columns if "share_hex_cluster" in c]

corr_columns = socio_corr_variables[7:-2] + socio_bikeability_cols

plot_func.plot_correlation(
    socio_socio,
    corr_columns,
    heatmap_fp=fp_socio_bikeability_heatmap,
    pairplot_fp=fp_socio_bikeability_pairplot,
    pair_plot_x_log=True,
    pair_plot_y_log=True,
)

display(socio_socio[corr_columns].corr().style.background_gradient(cmap="coolwarm"))
display(socio_socio[corr_columns])

# %%

preprocess = True

if preprocess:

    q = "sql/12f_process_hexcluster_socio.sql"

    result = dbf.run_query_pg(q, connection)
    if result == "error":
        print("Please fix error before rerunning and reconnect to the database")


# %%
# Get hex bikeability clusters with socio data
pop_keys = list(population_rename_dict.keys())
pop_keys = pop_keys[7:23]
pop_keys.remove("households_income_under_150k_pct")

population_keys_string = ", ".join(pop_keys)

hex_bike_socio = pd.read_sql(
    f"""SELECT cluster_label, {population_keys_string} FROM clustering.hex_bikeability_socio""",
    engine,
)

hex_bike_socio["households_income_under_150k_pct"] = (
    hex_bike_socio.households_income_under_100k_pct
    + hex_bike_socio.households_income_100_150k_pct
)

hex_bike_socio.rename(columns=population_rename_dict, inplace=True)

# %%

bikeability_values = sorted(list(hex_bike_socio.cluster_label.unique()))

for s in socio_corr_variables[7:-2]:

    fig, ax = plt.subplots(figsize=pdict["fsbar"])
    sns.boxplot(
        x="cluster_label",
        y=s,
        data=hex_bike_socio,
        palette=bikeability_cluster_color_dict_labels.values(),
        hue="cluster_label",
        order=bikeability_values,
    )

    plt.yrange = [0, 100]
    plt.xlabel("")
    plt.ylabel(s)
    plt.yticks([0, 100])
    # plt.yticks([min(hex_bike_socio[s]), max(hex_bike_socio[s])])

    plt.xticks(rotation=90)

    sns.despine(left=True)

    s_fp = s.replace(" ", "_")
    plt.savefig(
        fp_cluster_plots_base + f"{s_fp}_hex_bikeability_boxplot.png", dpi=pdict["dpi"]
    )

    plt.show()

# %%
