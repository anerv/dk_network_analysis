# %%
import rioxarray as rxr
from rasterio.merge import merge
from rasterio.mask import mask
import rasterio
import h3
import json
from shapely.geometry import Polygon
import geopandas as gpd
from src import db_functions as dbf
from src import h3_functions as h3f

exec(open("../settings/yaml_variables.py").read())

connection = dbf.connect_pg(db_name, db_user, db_password, db_port=db_port)

engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

# Load high res pop

# LOAD DATA
pop_src_1 = rasterio.open(pop_fp_1)
pop_src_2 = rasterio.open(pop_fp_2)

# MERGE RASTERS
mosaic, out_trans = merge([pop_src_1, pop_src_2])

out_meta = pop_src_1.meta.copy()

out_meta.update(
    {
        "driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": out_trans,
        "crs": pop_src_1.crs,
    }
)
merged_fp = "../data/processed/merged_pop_raster.tif"
with rasterio.open(merged_fp, "w", **out_meta) as dest:
    dest.write(mosaic)

merged = rasterio.open(merged_fp)


# Load DK boundaries
engine = dbf.connect_alc(db_name, db_user, db_password, db_port=db_port)

get_muni = "SELECT navn, geometry FROM adm_boundaries;"

muni = gpd.GeoDataFrame.from_postgis(get_muni, engine, geom_col="geometry")

# Clip raster to DK extent
dissolved = muni.dissolve()
dissolved_buffer = dissolved.buffer(500)

dissolved_proj = dissolved_buffer.to_crs(merged.crs)
convex = dissolved_proj.convex_hull

geo = gpd.GeoDataFrame({"geometry": convex[0]}, index=[0], crs=merged.crs)

coords = [json.loads(geo.to_json())["features"][0]["geometry"]]

clipped, out_transform = mask(merged, shapes=coords, crop=True)

out_meta = merged.meta.copy()

out_meta.update(
    {
        "driver": "GTiff",
        "height": clipped.shape[1],
        "width": clipped.shape[2],
        "transform": out_transform,
        "crs": merged.crs,
    }
)
clipped_fp = "../data/processed/clipped_pop_raster.tif"
with rasterio.open(clipped_fp, "w", **out_meta) as dest:
    dest.write(clipped)

clipped = rasterio.open(clipped_fp)

assert clipped.crs.to_string() == "EPSG:4326"

# vectorize and join to h3 hexes
pop_df = (
    rxr.open_rasterio(clipped_fp)
    .sel(band=1)
    .to_pandas()
    .stack()
    .reset_index()
    .rename(columns={"x": "lng", "y": "lat", 0: "population"})
)

pop_df = pop_df[pop_df.population > -200]

pop_gdf = gpd.GeoDataFrame(pop_df, geometry=gpd.points_from_xy(pop_df.lng, pop_df.lat))

pop_gdf.set_crs("EPSG:4326", inplace=True)

dk_gdf = gpd.GeoDataFrame({"geometry": dissolved_proj}, crs=dissolved_proj.crs)
dk_gdf.to_crs("EPSG:4326", inplace=True)

pop_gdf = gpd.sjoin(pop_gdf, dk_gdf, predicate="within", how="inner")

hex_id_col = f"hex_id"
pop_gdf[hex_id_col] = pop_gdf.apply(
    lambda row: h3.geo_to_h3(lat=row["lat"], lng=row["lng"], resolution=h3_resolution),
    axis=1,
)

h3_groups = (
    pop_gdf.groupby(hex_id_col)["population"].sum().to_frame("population").reset_index()
)
# Get the coordinate of the centroid of the hexagons
h3_groups["lat"] = h3_groups[hex_id_col].apply(lambda x: h3.h3_to_geo(x)[0])
h3_groups["lng"] = h3_groups[hex_id_col].apply(lambda x: h3.h3_to_geo(x)[1])

# use h3.h3_to_geo_boundary to obtain the geometries of these hexagons
h3_groups["hex_geometry"] = h3_groups[hex_id_col].apply(
    lambda x: {
        "type": "Polygon",
        "coordinates": [h3.h3_to_geo_boundary(h=x, geo_json=True)],
    }
)

h3_groups["geometry"] = h3_groups["hex_geometry"].apply(
    lambda x: Polygon(list(x["coordinates"][0]))
)

h3_gdf = gpd.GeoDataFrame(h3_groups, geometry="geometry", crs="EPSG:4326")
