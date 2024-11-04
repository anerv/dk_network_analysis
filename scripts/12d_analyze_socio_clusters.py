# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd
from IPython.display import display
import seaborn as sns
import matplotlib.patches as mpatches

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/df_styler.py").read())
exec(open("../settings/filepaths.py").read())

plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

# %%
preprocess = True

if preprocess:

    q = "sql/12d_process_socio_clusters.sql"

    result = dbf.run_query_pg(q, connection)
    if result == "error":
        print("Please fix error before rerunning and reconnect to the database")

# %%
socio_hex_cluster = gpd.read_postgis(
    "SELECT * FROM clustering.socio_socio_clusters", engine, geom_col="geometry"
)
socio_hex_cluster.fillna(0, inplace=True)

# %%

area_columns = [c for c in socio_hex_cluster.columns if "area" in c]
area_columns.append("socio_label")
grouped_socio_clusters = socio_hex_cluster[area_columns].groupby("socio_label").sum()

# %%
# Normalize the data to get proportions
hex_type_proportions = grouped_socio_clusters.div(
    grouped_socio_clusters.sum(axis=1), axis=0
)

colors = list(bikeability_cluster_color_dict.values())
cmap = plot_func.color_list_to_cmap(colors)

# Plot the stacked bar chart
ax = hex_type_proportions.plot(
    kind="bar", stacked=True, figsize=pdict["fsbar"], cmap=cmap
)

# Add labels and title
ax.set_xlabel("")
ax.set_ylabel("Proportion")

ax.set_yticks([0, 1])

ax.set_xticklabels(
    ax.get_xticklabels(),
    rotation=30,
    ha="right",
    fontdict={"fontsize": pdict["fontsize"]},
)
sns.despine(left=True)

# turn off legend
ax.get_legend().remove()

# handles, labels = ax.get_legend_handles_labels()
# labels = list(bikeability_cluster_color_dict_labels.keys())
# plt.legend(handles, labels, bbox_to_anchor=(1.05, 1), loc="upper left", frameon=False)

# Show plot
plt.tight_layout()
plt.savefig(fp_cluster_plots_base + "socio_clusters_proportions.png", dpi=pdict["dpi"])
plt.show()
# %%
