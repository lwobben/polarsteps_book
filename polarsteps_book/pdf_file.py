import io
from typing import Literal, Optional, Tuple, Union

from fpdf import FPDF
from PIL import Image


class PDFFile(FPDF):
    def __init__(
        self,
        font_path: str,
        title: str,
        unit: str,
        format: Tuple[int, int],
        bleed: Optional[int] = None,
        dev: bool = False,
    ):
        self.format = format
        self.bleed = bleed
        self.dev = dev

        full_format = (
            (format[0] + 2 * bleed, format[1] + 2 * bleed) if bleed else format
        )
        super().__init__(unit=unit, format=full_format)

        font_name = "".join(filter(str.isalpha, font_path))
        self.add_font(font_name, "", font_path)

        self.set_font(font_name, size=12)
        self.text_page(title=title)

    def base_page(self):
        self.add_page()
        if self.dev and self.bleed:
            self.set_draw_color(r=255, g=0, b=0)
            self.rect(x=self.bleed, y=self.bleed, w=self.format[0], h=self.format[0])
            self.set_draw_color(r=0, g=0, b=0)

    def text_page(
        self,
        title: str = None,
        body: str = None,
        align: Literal["J", "L", "R", "C"] = "C",
    ):
        self.base_page()
        if title:
            self.set_font(size=16)
            self.multi_cell(w=0, text=title, new_y="Next", align=align)
            self.ln()
            self.set_font(size=12)
        if body:
            self.multi_cell(w=0, text=body, align=align)

    def image_page(self, image: Union[str, io.BytesIO], page_add=True):
        if page_add:
            self.base_page()
        with Image.open(image) as im:
            w, h = im.size
            if w > 1.15 * h:
                print("Treat as landscape")
            elif h > 1.15 * w:
                print("Treat as portrait")
            else:
                print("Treat as square")
        self.image(image, x=20, y=60, h=self.eph / 2, keep_aspect_ratio=True)

    def create_output(self, path: str = None) -> Optional[bytearray]:
        if path:
            self.output(path)
        else:
            return self.output()  # still need to test!
