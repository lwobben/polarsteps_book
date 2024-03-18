from geo_map import GeoMap
from pdf_file import PDFFile
from trip_data import TripData


class PhotoBook(PDFFile):
    def __init__(
        self,
        data: TripData,
        path: str,
        margin=25,
        bleed: int = 3,
        mark_bleed_line: bool = False,
    ):
        super().__init__(
            font_path="polarsteps_book/fonts/FreeSerif.otf",
            title=data.title,
            unit="mm",
            margin=margin,
            format=(297, 297),
            bleed=bleed,
            mark_bleed_line=mark_bleed_line,
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
            for i in range(0, len(step["photo_paths"]), 2):
                if i + 1 == len(step["photo_paths"]):
                    self.image_page(step["photo_paths"][i])
                    break
                else:
                    self.two_images_page(
                        step["photo_paths"][i], step["photo_paths"][i + 1]
                    )

    def output_book(self, output_path):
        self.create_output(path=output_path)
