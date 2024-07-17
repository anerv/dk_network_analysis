# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/df_styler.py").read())
exec(open("../settings/filepaths.py").read())
plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)
# %%
exec(open("../helper_scripts/read_hex_results.py").read())

# %%
all_density_columns = [
    # length_columns,
    # length_steps_columns,
    density_columns,
    density_steps_columns,
    length_relative_columns,
    length_relative_steps_columns,
]

all_labels = [labels_all, labels_step_all, labels_pct, labels_pct_step]

axis_labels = ["km/sqkm", "km/sqkm", "%", "%"]

for i, columns in enumerate(all_density_columns[:-2]):

    for e, c in enumerate(columns):

        plt.figure(figsize=(8, 6))
        fig = sns.scatterplot(
            data=hex_gdf,
            x="pop_density",
            y=c,
            hue="urban_pct",
            alpha=0.5,
        )
        fig.get_legend().set_title("Pct urban")
        plt.xscale("log")
        # plt.yscale("log")
        plt.xlabel("People per sqkm")
        plt.ylabel(all_labels[i][e] + " " + axis_labels[i])
        # plt.title()
        # plt.savefig(fp_hex_pop_corr + f"{c}.png")
        plt.show()

# %%
