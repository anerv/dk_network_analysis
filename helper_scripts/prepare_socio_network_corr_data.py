from src import db_functions as dbf
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly_express as px
import pandas as pd

exec(open("../settings/yaml_variables.py").read())
exec(open("../settings/plotting.py").read())

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

socio = gpd.read_postgis(
    "SELECT id, urban_pct, geometry FROM socio;", engine, geom_col="geometry"
)

exec(open("../helper_scripts/read_socio_results.py").read())

socio_gdf = socio.merge(socio_density, on="id", how="left")
socio_gdf = socio_gdf.merge(socio_components, on="id", how="left")
socio_gdf = socio_gdf.merge(socio_largest_components, on="id", how="left")
socio_gdf = socio_gdf.merge(socio_reach, on="id", how="left")
socio_gdf = socio_gdf.merge(socio_reach_comparison, on="id", how="left")

assert socio.shape[0] == socio_gdf.shape[0]

duplicates = [c for c in socio_gdf.columns if c.endswith("_x") or c.endswith("_y")]
assert len(duplicates) == 0
