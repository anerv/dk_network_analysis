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
# Label each socio row based on dominant bikeability cluster

socio_bikeability_cols = [c for c in socio_socio.columns if "share_hex_cluster" in c]

corr_columns = socio_corr_variables[7:-2] + socio_bikeability_cols

plot_func.plot_correlation(
    socio_socio,
    corr_columns,
    heatmap_fp=fp_socio_bikeability_heatmap,
    pairplot_fp=fp_socio_bikeability_pairplot,
)

display(socio_socio[corr_columns].corr().style.background_gradient(cmap="coolwarm"))
display(socio_socio[corr_columns])

# %%
