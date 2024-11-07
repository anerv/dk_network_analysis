# %%
from src import db_functions as dbf
from src import plotting_functions as plot_func
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import contextily as cx
from mpl_toolkits.axes_grid1 import make_axes_locatable
import geopandas as gpd
from matplotlib_scalebar.scalebar import ScaleBar
import random
import seaborn as sns
import matplotlib.patches as mpatches
import matplotlib as mpl


exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())
exec(open("../settings/filepaths.py").read())
plot_func.set_renderer("png")

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

# - maps of socio vars
# - map of population at socio level
# - map of urban pct at socio level
# - make bivariate maps of income and car ownership
# %%
