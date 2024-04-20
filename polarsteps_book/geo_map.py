import io

# import pyogrio
import contextily as ctx
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import shapely

# from mpl_toolkits.basemap import Basemap


class GeoMap:
    GLOBE_COORDINATE_SYSTEM_ID: int = 4326
    MAP_COORDINATE_SYSTEM_ID: int = 3857
    COLOR_LIGHT: str = "#78586F"
    COLOR_DARK: str = "#30011E"

    def __init__(self, locations):
        self.locations = locations

    def create_buf(self) -> io.BytesIO:
        frame = {"geometry": gpd.points_from_xy(self.locations.lon, self.locations.lat)}
        gdf_points = gpd.GeoDataFrame(pd.DataFrame(frame))
        line_string = shapely.LineString(gdf_points.geometry.tolist())
        gdf_line = gpd.GeoDataFrame(pd.DataFrame({"geometry": [line_string]}))

        # # Use world border map
        # world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
        # map_gdf = gpd.read_file('data/countries.zip', engine="pyogrio")

        gdf_points.crs = {"init": f"epsg:{self.GLOBE_COORDINATE_SYSTEM_ID}"}
        gdf_points = gdf_points.to_crs(epsg=self.MAP_COORDINATE_SYSTEM_ID)
        gdf_line.crs = {"init": f"epsg:{self.GLOBE_COORDINATE_SYSTEM_ID}"}
        gdf_line = gdf_line.to_crs(epsg=self.MAP_COORDINATE_SYSTEM_ID)

        ax = plt.axes()

        for spine_location in ["bottom", "top", "right", "left"]:
            ax.spines[spine_location].set_color(self.COLOR_LIGHT)

        ax.set_xticks([])
        ax.set_yticks([])

        gdf_points.plot(ax=ax, color=self.COLOR_LIGHT)
        gdf_line.plot(ax=ax, color=self.COLOR_DARK)

        # # Use mpl_toolkits basemap
        # m=Basemap(epsg=self.MAP_COORDINATE_SYSTEM_ID)
        # x, y = m(gdf_points['Longitude'].values, gdf_points['Latitude'].values)
        # m.scatter(x, y, color='red', marker='o', label='Points')

        # # Add Contextily basemap
        # https://contextily.readthedocs.io/en/latest/providers_deepdive.html
        # ctx.add_basemap(ax=ax, source=ctx.providers.CartoDB.PositronNoLabels)
        # ctx.add_basemap(ax=ax, source=ctx.providers.CartoDB.Positron)
        ctx.add_basemap(ax=ax, source=ctx.providers.OpenStreetMap.HOT)

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)

        return buf
