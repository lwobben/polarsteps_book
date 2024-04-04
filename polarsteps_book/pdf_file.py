import io
from typing import Literal, Optional, Tuple, Union

from fpdf import FPDF
from fpdf.enums import VAlign
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
            )  # make actual error instead of print


class PDFFile(FPDF):
    def __init__(
        self,
        font_path: str,
        title: str,
        unit: str,
        margin: int,
        format: Tuple[int, int],  # width, height
        bleed: Optional[int] = None,
        mark_bleed_line: bool = False,
    ):
        self.format = format
        self.bleed = bleed
        self.mark_bleed_line = mark_bleed_line
        self.margin = margin
        self.full_format = (
            (format[0] + 2 * bleed, format[1] + 2 * bleed) if bleed else format
        )
        super().__init__(unit=unit, format=self.full_format)

        font_name = "".join(filter(str.isalpha, font_path))
        self.add_font(font_name, "", font_path)
        self.add_font(font_name, "B", font_path)  # change!!
        self.set_font(font_name, size=12)
        self.text_page(title=title)
        self.set_margin(self.margin)

    def base_page(self):
        self.add_page()
        if self.mark_bleed_line and self.bleed:
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
            self.set_font(size=28)
            self.multi_cell(w=0, text=title, new_y="Next", align=align)
            self.ln()
            self.set_font(size=20)
        if body:
            self.multi_cell(w=0, text=body, align=align)
        self.base_page()
        # TABLE_DATA = (
        #     ("First name", "Last name", "Age", "City"),
        #     ("Jules", "Smith", "34", "San Juan"),
        #     ("Mary", "Ramos", "45", "Orlando"),
        #     ("Carlson", "Banks", "19", "Los Angeles"),
        #     ("Lucas", "Cimon", "31", "Saint-Mathurin-sur-Loire"),
        # )
        TABLE_DATA = [["test"]]
        with self.table(
            v_align=VAlign.M,
            line_height=self.full_format[1] - 2 * self.margin,
            borders_layout="NONE",
        ) as table:
            for data_row in TABLE_DATA:
                row = table.row()
                for datum in data_row:
                    row.cell(datum)

    def image_page(self, image: Union[str, io.BytesIO]):
        img = ImageFile(image)
        self.base_page()

        if img.w_h_ratio > 1:  # landscape
            img.set_target_size(target_width=self.full_format[0] - 2 * self.margin)
            y_start = self.full_format[1] / 2 - img.target_h / 2
            self.image(
                image, x=self.margin, y=y_start, h=img.target_h, keep_aspect_ratio=True
            )

        if img.w_h_ratio <= 1:  # portrait/square
            img.set_target_size(target_height=self.full_format[1] - 2 * self.margin)
            x_start = self.full_format[0] / 2 - img.target_w / 2
            self.image(
                image, x=x_start, y=self.margin, h=img.target_h, keep_aspect_ratio=True
            )

    def two_images_page(
        self,
        image1: Union[str, io.BytesIO],
        image2: Union[str, io.BytesIO],
        sep=3,
    ):
        img1 = ImageFile(image1)
        img2 = ImageFile(image2)
        self.base_page()

        if all(im.w_h_ratio > 1 for im in [img1, img2]):  # stack vertically
            equalizer = img2.w / img1.w
            y_image_space = self.full_format[1] - 2 * self.margin - sep
            total_height_original = img1.h * equalizer + img2.h
            img1.set_target_size(
                target_height=(img1.h * equalizer * y_image_space)
                / total_height_original
            )
            img2.set_target_size(target_height=y_image_space - img1.target_h)
            x_start = self.full_format[0] / 2 - img1.target_w / 2
            self.image(
                img1.image,
                x=x_start,
                y=self.margin,
                h=img1.target_h,
                keep_aspect_ratio=True,
            )
            self.image(
                img2.image,
                x=x_start,
                y=self.margin + img1.target_h + sep,
                h=img2.target_h,
                keep_aspect_ratio=True,
            )

        else:  # stack horizontally
            equalizer = img2.h / img1.h
            x_image_space = self.full_format[0] - 2 * self.margin - sep
            total_width_original = img1.w * equalizer + img2.w
            img1.set_target_size(
                target_width=(img1.w * equalizer * x_image_space) / total_width_original
            )
            img2.set_target_size(target_width=x_image_space - img1.target_w)
            y_start = self.full_format[1] / 2 - img1.target_h / 2
            self.image(
                img1.image,
                x=self.margin,
                y=y_start,
                h=img1.target_h,
                keep_aspect_ratio=True,
            )
            self.image(
                img2.image,
                x=self.margin + img1.target_w + sep,
                y=y_start,
                h=img2.target_h,
                keep_aspect_ratio=True,
            )

    def create_output(self, path: str = None) -> Optional[bytearray]:
        if path:
            self.output(path)
        else:
            return self.output()  # still need to test!
