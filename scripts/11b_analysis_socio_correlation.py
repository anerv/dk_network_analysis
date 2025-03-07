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
# Just income

socio_vars = socio_corr_variables[7:17]
plot_func.plot_correlation(
    socio,
    socio_vars,
    # pair_plot_x_log=True,
    # pair_plot_y_log=True,
    # heatmap_fp=fp_socio_vars_heatmap,
    # pairplot_fp=fp_socio_vars_pairplot,
)
display(socio[socio_vars].corr().style.background_gradient(cmap="coolwarm"))
display(socio[socio_vars].describe())
# %%
# Just income and cars

sns.set(font_scale=1.3, style="white")

socio_vars = (
    socio_corr_variables[8:15] + socio_corr_variables[17:-2]
)  # socio_corr_variables[7:17]
plot_func.plot_correlation(
    socio,
    socio_vars,
    # pair_plot_x_log=True,
    # pair_plot_y_log=True,
    # heatmap_fp=fp_socio_vars_heatmap,
    pairplot_fp=fp_socio_pairplot_income_cars,
)
display(socio[socio_vars].corr().style.background_gradient(cmap="coolwarm"))
display(socio[socio_vars].describe())


# %%
# Just income, urban, pop

socio_vars = socio_corr_variables[7:17] + socio_corr_variables[-2:]
plot_func.plot_correlation(
    socio,
    socio_vars,
    pair_plot_x_log=True,
    pair_plot_y_log=True,
    # heatmap_fp=fp_socio_vars_heatmap,
    # pairplot_fp=fp_socio_vars_pairplot,
)
display(socio[socio_vars].corr().style.background_gradient(cmap="coolwarm"))
display(socio[socio_vars].describe())

# %%
# Car, urban, pop
socio_vars = socio_corr_variables[17:]
plot_func.plot_correlation(
    socio,
    socio_vars,
    pair_plot_x_log=True,
    pair_plot_y_log=True,
    # heatmap_fp=fp_socio_vars_heatmap,
    # pairplot_fp=fp_socio_vars_pairplot,
)
display(socio[socio_vars].corr().style.background_gradient(cmap="coolwarm"))
display(socio[socio_vars].describe())

# %%
