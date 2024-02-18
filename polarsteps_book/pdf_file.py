from fpdf import FPDF
import io
from typing import Optional, Union


class PDFFile(FPDF):
    def __init__(self, font_path: str = "polarsteps_book/fonts/FreeSerif.otf", title: str = "My photobook"):
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
