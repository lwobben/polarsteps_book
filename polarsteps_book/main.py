import json
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
# import pyogrio
import contextily as ctx
import shapely

# Load data and create gdf's
data = json.load(open("data/zuid-india/locations.json"))
df = pd.json_normalize(data, record_path="locations")
df['geometry'] = gpd.points_from_xy(df.lon, df.lat)
gdf_points = gpd.GeoDataFrame(df.drop(['lon', 'lat'], axis=1))
line_string = shapely.LineString(gdf_points.geometry.tolist())
gdf_line = gpd.GeoDataFrame(pd.DataFrame({"geometry": [line_string]}))

# Use world border map
# world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
# map_gdf = gpd.read_file('data/ne_110m_admin_0_countries.zip', engine="pyogrio")

# Set projections
gdf_points.crs = {'init': 'epsg:4326'}
gdf_points = gdf_points.to_crs(epsg=3857)
gdf_line.crs = {'init': 'epsg:4326'}
gdf_line = gdf_line.to_crs(epsg=3857)

# Plot
f, ax = plt.subplots()
# map_gdf.plot(ax=ax)
gdf_points.plot(ax=ax,figsize=(10, 5))
gdf_line.plot(ax=ax,figsize=(10, 5), color='red')
ctx.add_basemap(ax=ax)
plt.show(block=True)