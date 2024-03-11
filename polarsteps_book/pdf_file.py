import io
from typing import Literal, Optional, Tuple, Union

from fpdf import FPDF
from PIL import Image


class ImageFile:
    def __init__(self, input: Union[str, io.BytesIO]):
        self.image = Image.open(input)
        self.w, self.h = self.image.size
        self.w_h_ratio = self.w / self.h

    def set_target_size(
        self,
        target_width: Optional[float] = None,
        target_height: Optional[float] = None,
    ):
        if target_width:
            self.target_w = target_width
            if target_height:
                self.target_h = target_height
            else:
                self.target_h = target_width / self.w_h_ratio
        elif target_height:
            self.target_h = target_height
            self.target_w = target_height * self.w_h_ratio
        else:
            print(
                "Error! at least one of target_width & target_height should be given!!!"
            )


class PDFFile(FPDF):
    def __init__(
        self,
        font_path: str,
        title: str,
        unit: str,
        format: Tuple[int, int],  # width, height
        bleed: Optional[int] = None,
        dev: bool = False,
    ):
        self.format = format
        self.bleed = bleed
        self.dev = dev

        self.full_format = (
            (format[0] + 2 * bleed, format[1] + 2 * bleed) if bleed else format
        )
        super().__init__(unit=unit, format=self.full_format)

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

    def two_images_page(
        self,
        image1: Union[str, io.BytesIO],
        image2: Union[str, io.BytesIO],
        margin=25,
        sep=3,
    ):
        img1 = ImageFile(image1)
        img2 = ImageFile(image2)
        self.base_page()

        if all(im.w_h_ratio > 1 for im in [img1, img2]):  # stack vertically
            y_image_space = self.full_format[1] - 2 * margin - sep
            total_height_original = img1.h + img2.h
            img1.set_target_size(
                target_height=(img1.h * y_image_space) / total_height_original
            )
            img2.set_target_size(target_height=y_image_space - img1.target_h)
            x_start = self.full_format[0] / 2 - img1.target_w / 2
            self.image(
                img1.image, x=x_start, y=margin, h=img1.target_h, keep_aspect_ratio=True
            )
            self.image(
                img2.image,
                x=x_start,
                y=margin + img1.target_h + sep,
                h=img2.target_h,
                keep_aspect_ratio=True,
            )

        else:  # stack horizontally - improve!!
            self.image(img1.image, x=margin, y=80, w=125, keep_aspect_ratio=True)
            self.image(img2.image, x=150, y=80, w=125, keep_aspect_ratio=True)

    def create_output(self, path: str = None) -> Optional[bytearray]:
        if path:
            self.output(path)
        else:
            return self.output()  # still need to test!
