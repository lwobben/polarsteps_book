import json
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
# import pyogrio
import contextily as ctx
import shapely
from fpdf import FPDF
import io
from typing import Optional, Union


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

# Plot & save as file-like fig
f, ax = plt.subplots()
# map_gdf.plot(ax=ax)
gdf_points.plot(ax=ax,figsize=(10, 5))
gdf_line.plot(ax=ax,figsize=(10, 5), color='red')
ctx.add_basemap(ax=ax)
# plt.show(block=True)
buf = io.BytesIO()
plt.savefig(buf, format='png')
buf.seek(0)

# Define Photobook class
class PhotoBook(FPDF):
    def __init__(self, font: str = "helvetica", title: str = "My photobook"):
        FPDF.__init__(self)
        self.page_add()
        self.set_font('helvetica', size=12)
        self.title_add(title)

    def page_add(self):
        self.add_page()

    def title_add(self, title: str):
        self.cell(text=title)

    def image_add(self, image: Union[str, io.BytesIO]):
        self.image(image, x=20, y=60, h=self.eph/2, keep_aspect_ratio=True)

    def create_output(self, path: str=None) -> Optional[bytes]:
        if path:
            self.output(path)
        else:
            return self.output() #still need to test!

# Create and save photobook pdf
photo_book = PhotoBook()
photo_book.image_add(buf)
photo_book.page_add()
photo_book.image_add("data/zuid-india/alappuzha_88326961/photos/7BC50DA2-BCFB-41C7-AFC3-720A56923B2D_229F9E6B-64C4-47C4-979F-3F08E2D5B86C.jpg.jpg")
photo_book.create_output(path="data/photo-book.pdf")
