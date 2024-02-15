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
import os




print("* Loading data and creating gdf's")
data = json.load(open("data/zuid-india/locations.json"))
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

# Define Photobook class
class PhotoBook(FPDF):
    def __init__(self, font_path: str = "FreeSerif.otf", title: str = "My photobook"):
        super().__init__()
        font_name = ''.join(filter(str.isalpha, font_path))
        self.add_font(font_name, '', font_path)
        self.set_font(font_name, size=12)
        self.text_page(title=title)

    def text_page(self, title: str=None, body: str=None):
        self.add_page()
        if title:
            self.set_font(size=16)
            self.multi_cell(w=0, text=title, new_y="Next")
            self.ln()
            self.set_font(size=12)
        if body:
            self.multi_cell(w=0, text=body)

    def image_page(self, image: Union[str, io.BytesIO], page_add=True):
        if page_add:
            self.add_page()
        self.image(image, x=20, y=60, h=self.eph/2, keep_aspect_ratio=True)

    def create_output(self, path: str=None) -> Optional[bytearray]:
        if path:
            self.output(path)
        else:
            return self.output() #still need to test!

print("* Creating and saving photobook pdf")
photo_book = PhotoBook()
photo_book.image_page(buf)
path = "data/zuid-india/"
regions = [r for r in os.listdir(path) if os.path.isdir(path+r)]
regions.sort(key=lambda x: x.split("_")[1])
steps = json.load(open("data/zuid-india/trip.json"))["all_steps"]

for cnt, r in enumerate(regions):
    path = f"data/zuid-india/{r}/photos/"
    if os.path.isdir(path):
        step=steps[cnt]
        photo_book.text_page(body=step["description"], title=step["display_name"])
        photo_files = os.listdir(path)
        for f in photo_files:
            photo_book.image_page(path+f)
photo_book.create_output(path="data/photo-book.pdf")


class TripData():
    def __init__():
        path: str = "data"