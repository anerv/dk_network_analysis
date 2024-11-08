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
###### SOCIO-ECO VARIABLES #####
################################

exec(open("../helper_scripts/read_socio_pop.py").read())
# %%
plot_func.plot_correlation(
    socio,
    socio_corr_variables,
    heatmap_fp=fp_socio_vars_heatmap,
    pairplot_fp=fp_socio_vars_pairplot,
)

display(socio[socio_corr_variables].corr().style.background_gradient(cmap="coolwarm"))
display(socio[socio_corr_variables].describe())

# %%
# Just income and car ownership
plot_func.plot_correlation(
    socio,
    socio_corr_variables[7:20],
    # pair_plot_x_log=True,
    # pair_plot_y_log=True,
    # heatmap_fp=fp_socio_vars_heatmap,
    # pairplot_fp=fp_socio_vars_pairplot,
)
display(socio[socio_corr_variables].corr().style.background_gradient(cmap="coolwarm"))
display(socio[socio_corr_variables].describe())

# %%
# Just income
plot_func.plot_correlation(
    socio,
    socio_corr_variables[7:15],
    # pair_plot_x_log=True,
    # pair_plot_y_log=True,
    # heatmap_fp=fp_socio_vars_heatmap,
    # pairplot_fp=fp_socio_vars_pairplot,
)
display(socio[socio_corr_variables].corr().style.background_gradient(cmap="coolwarm"))
display(socio[socio_corr_variables].describe())
# %%
# Just income, urban, pop

socio_vars = socio_corr_variables[7:15] + socio_corr_variables[-2:]
plot_func.plot_correlation(
    socio,
    socio_vars,
    pair_plot_x_log=True,
    pair_plot_y_log=True,
    # heatmap_fp=fp_socio_vars_heatmap,
    # pairplot_fp=fp_socio_vars_pairplot,
)
display(socio[socio_corr_variables].corr().style.background_gradient(cmap="coolwarm"))
display(socio[socio_corr_variables].describe())

# %%
# Car, urban, pop
plot_func.plot_correlation(
    socio,
    socio_corr_variables[16:],
    pair_plot_x_log=True,
    pair_plot_y_log=True,
    # heatmap_fp=fp_socio_vars_heatmap,
    # pairplot_fp=fp_socio_vars_pairplot,
)
display(socio[socio_corr_variables].corr().style.background_gradient(cmap="coolwarm"))
display(socio[socio_corr_variables].describe())

# %%
