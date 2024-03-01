import io

# import pyogrio
import contextily as ctx
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import shapely


class GeoMap:
    def __init__(self, locations):
        self.locations = locations

    def create_buf(self) -> io.BytesIO:
        frame = {"geometry": gpd.points_from_xy(self.locations.lon, self.locations.lat)}
        gdf_points = gpd.GeoDataFrame(pd.DataFrame(frame))
        line_string = shapely.LineString(gdf_points.geometry.tolist())
        gdf_line = gpd.GeoDataFrame(pd.DataFrame({"geometry": [line_string]}))

        # Use world border map
        # world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
        # map_gdf = gpd.read_file('data/countries.zip', engine="pyogrio")

        gdf_points.crs = {"init": "epsg:4326"}
        gdf_points = gdf_points.to_crs(epsg=3857)
        gdf_line.crs = {"init": "epsg:4326"}
        gdf_line = gdf_line.to_crs(epsg=3857)

        f, ax = plt.subplots()
        # map_gdf.plot(ax=ax)
        gdf_points.plot(ax=ax, figsize=(10, 5))
        gdf_line.plot(ax=ax, figsize=(10, 5), color="red")
        ctx.add_basemap(ax=ax)
        # plt.show(block=True)
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)

        return buf
