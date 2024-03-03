from geo_map import GeoMap
from pdf_file import PDFFile
from trip_data import TripData


class PhotoBook(PDFFile):
    def __init__(self, data: TripData, path: str, dev: bool = False):
        super().__init__(
            font_path="polarsteps_book/fonts/FreeSerif.otf",
            title=data.title,
            unit="mm",
            format=(297, 297),
            bleed=3,
            dev=dev,
        )
        self.data = data
        self.path = path

    def add_geo_map(self):
        geo_map = GeoMap(self.data.locations)
        buf = geo_map.create_buf()
        self.image_page(buf)

    def add_steps(self):
        for step in self.data.steps:
            self.text_page(body=step["description"], title=step["display_name"])
            for f in step["photo_paths"]:
                self.image_page(f)

    def output_book(self, output_path):
        self.create_output(path=output_path)
