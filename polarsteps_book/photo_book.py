from geo_map import GeoMap
from pdf_file import PDFFile
from trip_data import TripData


class PhotoBook(PDFFile):
    def __init__(
        self,
        data: TripData,
        path: str,
        text_margin: int = 40,
        image_margin: int = 25,
        bleed: int = 3,
        mark_bleed_line: bool = False,
        vertically_center_text_pages: bool = True,
        page_numbering: bool = True,
    ):
        super().__init__(
            # font_path="polarsteps_book/fonts/FreeSerif.otf",
            # font_path="polarsteps_book/fonts/ARIAL.TTF",
            # font_path="polarsteps_book/fonts/avenir_roman_12.otf",
            # font_path="polarsteps_book/fonts/calibri-regular.ttf",
            font_path="polarsteps_book/fonts/calibril.ttf",
            title=data.title,
            unit="mm",
            text_margin=text_margin,
            image_margin=image_margin,
            format=(297, 297),
            bleed=bleed,
            mark_bleed_line=mark_bleed_line,
            vertically_center_text_pages=vertically_center_text_pages,
            page_numbering=page_numbering,
        )
        self.data = data
        self.path = path

    def add_geo_map(
        self, countries_filter: list[str] = None, continents_filter: list[str] = None
    ):
        geo_map = GeoMap(
            self.data.locations,
            countries_filter=countries_filter,
            continents_filter=continents_filter,
        )
        buf = geo_map.create_buf()
        self.image_page(buf)

    def add_steps(self):
        for step in self.data.steps:
            self.text_page(body=step["description"], title=step["display_name"])
            if step["photo_paths"] is not None:
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
