import pandas as pd
import geopandas as gpd
# import pyogrio
import contextily as ctx
import shapely
import matplotlib.pyplot as plt
import io
import json


class GeoMap:
    def __init__(self, path):
        self.path = path

    def create_buf(self) -> io.BytesIO:
        print("* Loading data and creating gdf's")
        data = json.load(open(f"{self.path}locations.json"))
        df = pd.json_normalize(data, record_path="locations")
        df['geometry'] = gpd.points_from_xy(df.lon, df.lat)
        gdf_points = gpd.GeoDataFrame(df.drop(['lon', 'lat'], axis=1))
        line_string = shapely.LineString(gdf_points.geometry.tolist())
        gdf_line = gpd.GeoDataFrame(pd.DataFrame({"geometry": [line_string]}))

        # Use world border map
        # world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
        # map_gdf = gpd.read_file('data/ne_110m_admin_0_countries.zip', engine="pyogrio")

        print("* Setting projections")
        gdf_points.crs = {'init': 'epsg:4326'}
        gdf_points = gdf_points.to_crs(epsg=3857)
        gdf_line.crs = {'init': 'epsg:4326'}
        gdf_line = gdf_line.to_crs(epsg=3857)

        print("* Plotting & saving as file-like fig")
        f, ax = plt.subplots()
        # map_gdf.plot(ax=ax)
        gdf_points.plot(ax=ax,figsize=(10, 5))
        gdf_line.plot(ax=ax,figsize=(10, 5), color='red')
        ctx.add_basemap(ax=ax)
        # plt.show(block=True)
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        return buf
