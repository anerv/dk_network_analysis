# %%
import numpy as np

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())

# Read socio pop
exec(open("../helper_scripts/read_socio_pop.py").read())

socio_socio_gdf = socio
socio_socio_gdf.replace(np.nan, 0, inplace=True)

# Define cluster variables
socio_socio_cluster_variables = [c for c in socio_corr_variables if "w car" not in c]

socio_socio_cluster_variables.remove("0-17 years (share)")
# socio_socio_cluster_variables.remove("Urban area (%)")

# socio_socio_cluster_variables.remove("Population density")
# %%
