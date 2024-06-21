import io

# import pyogrio
# import contextily as ctx
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

# import pycountry
import shapely

# from geopy.geocoders import Nominatim

# from mpl_toolkits.basemap import Basemap


class GeoMap:
    GLOBE_COORDINATE_SYSTEM_ID: int = 4326
    MAP_COORDINATE_SYSTEM_ID: int = 3857
    COLOR_LIGHT: str = "#78586F"
    COLOR_DARK: str = "#30011E"

    def __init__(self, locations, countries_filter, continents_filter):
        self.locations = locations
        self.countries_filter = countries_filter
        self.continents_filter = continents_filter

    def create_buf(self) -> io.BytesIO:
        frame = {"geometry": gpd.points_from_xy(self.locations.lon, self.locations.lat)}
        gdf_points = gpd.GeoDataFrame(pd.DataFrame(frame), crs="EPSG:4326")
        line_string = shapely.LineString(gdf_points.geometry.tolist())
        gdf_line = gpd.GeoDataFrame(
            pd.DataFrame({"geometry": [line_string]}), crs="EPSG:4326"
        )

        world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
        # if self.countries_filter is not None:
        #     world = world[world["name"].isin(self.countries_filter)]
        # if self.continents_filter is not None:
        #     world = world[world["continent"].isin(self.continents_filter)]

        ax = world.plot(color="white", edgecolor="black")
        gdf_points.plot(ax=ax, color=self.COLOR_LIGHT)
        gdf_line.plot(ax=ax, color=self.COLOR_DARK)

        ax.set_xticks([])
        ax.set_yticks([])
        for spine_location in ["bottom", "top", "right", "left"]:
            ax.spines[spine_location].set_color(self.COLOR_LIGHT)

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)

        return buf


"""
source_url = ("https://www.naturalearthdata.com/"\
              "http//www.naturalearthdata.com/download/"\
              "10m/cultural/ne_10m_admin_0_countries.zip"
             )
source_url
'https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip'
ctys = geopandas.read_file(source_url)
ctys.plot()
"""


# https://github.com/geopandas/geopandas/issues/2838
