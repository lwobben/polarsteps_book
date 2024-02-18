from pdf_file import PDFFile
from trip_data import TripData
from geo_map import GeoMap
from typing import Optional

class PhotoBook(PDFFile):
    def __init__(self, data: TripData, path: str):
        super().__init__(title=data.title) # doesn't work yet
        self.data = data
        print("***", self.data.title, type(self.data.title))
        self.text_page(title = self.data.title)
        self.path = path
    
    def add_geo_map(self): # should be somewhere else maybe
        geo_map = GeoMap(self.path)
        buf = geo_map.create_buf()
        self.image_page(buf)

    def add_steps(self):
        for step in self.data.steps:
            self.text_page(body=step["description"], title=step["display_name"])
            for f in step["photo_paths"]:
                self.image_page(f)
    
    def output_book(self, output_path):
        self.create_output(path=output_path)
