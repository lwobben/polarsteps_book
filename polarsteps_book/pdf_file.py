import io
import re
from copy import deepcopy
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
            )  # make actual error instead of print


class PDFFile(FPDF):
    def __init__(
        self,
        font_path: str,
        title: str,
        unit: str,
        text_margin: int,
        image_margin: int,
        format: Tuple[int, int],  # width, height
        bleed: Optional[int] = None,
        mark_bleed_line: bool = False,
        vertically_center_text_pages: bool = False,
        page_numbering: bool = True,
    ):
        self.format = format
        self.bleed = bleed
        self.mark_bleed_line = mark_bleed_line
        self.text_margin = text_margin
        self.image_margin = image_margin
        self.page_numbering = page_numbering
        self.vertically_center_text_pages = vertically_center_text_pages
        self.full_format = (
            (format[0] + 2 * bleed, format[1] + 2 * bleed) if bleed else format
        )
        super().__init__(unit=unit, format=self.full_format)

        font_name = "".join(filter(str.isalpha, font_path))
        self.add_font(font_name, "", font_path)
        self.add_font(font_name, "B", font_path)  # change!!
        self.set_font(font_name, size=24)
        self.set_margin(self.text_margin)
        self.text_page(title=title)

    def base_page(self):
        self.add_page()
        if self.mark_bleed_line and self.bleed:
            self.set_draw_color(r=255, g=0, b=0)
            self.rect(x=self.bleed, y=self.bleed, w=self.format[0], h=self.format[0])
            self.set_draw_color(r=0, g=0, b=0)

    def _split_string(
        self,
        str_in: str,
        n_parts: int,
        split_pattern: str = r"\.",
        # To do: maybe change default split pattern so that it splits on newlines
        # (inbetween paragraphs) and not on dots (inbetween sentences)
    ) -> list[str]:
        """
        Splits a string (`str_in`) on `split_pattern` into `n_parts`.
        The sizes of the parts will be as equal to each other as possible.
        """
        pattern_matches = [m.end() for m in re.finditer(split_pattern, str_in)]
        split_near = [i * len(str_in) / n_parts for i in range(1, n_parts)]
        split_on = [min(pattern_matches, key=lambda x: abs(x - i)) for i in split_near]
        split_on.insert(0, 0)
        parts = [str_in[i:j].strip() for i, j in zip(split_on, split_on[1:] + [None])]
        return parts

    def text_page(
        self,
        title: str = None,
        body: str = None,
        align: Literal["J", "L", "R", "C"] = "C",
    ):
        if self.vertically_center_text_pages:
            test_pdf = deepcopy(self)
            page_no_before = test_pdf.page_no()
            y_after_title, y_before_body, y_after_body = test_pdf._insert_text_page(
                title, body, align
            )
            if (page_amount := test_pdf.page_no() - page_no_before) > 1:  # multi-page
                for idx, p in enumerate(self._split_string(body, page_amount)):
                    title = title if idx == 0 else None
                    self.text_page(title, p)
            else:
                if body:
                    body_size = y_after_body - y_before_body
                    space_left = self.full_format[1] - body_size - 2 * self.text_margin
                    y_start = self.text_margin + space_left / 2
                    if title:
                        # Body & title provided?:
                        # -> vertically center body itself, title comes above
                        full_title_size = y_before_body - self.text_margin
                        y_start = y_start - full_title_size
                else:  # title only
                    title_size = y_after_title - self.text_margin
                    space_left = self.full_format[1] - title_size - 2 * self.text_margin
                    y_start = self.text_margin + space_left / 2
                self._insert_text_page(title, body, align, y_start)
        else:
            self._insert_text_page(title, body, align)

    def _insert_text_page(
        self,
        title: str = None,
        body: str = None,
        align: Literal["J", "L", "R", "C"] = "C",
        y_start: Optional[float] = None,
    ):
        self.base_page()
        if y_start is not None:
            self.set_y(y_start)

        if title:
            self.set_font(size=52)
            self.multi_cell(w=0, text=title, new_y="Next", align=align)
            y_after_title = self.y
            self.ln()
            self.set_font(size=24)
        else:
            y_after_title = None

        if body:
            y_before_body = self.y
            self.multi_cell(w=0, text=body, align=align)
            y_after_body = self.y
        else:
            y_before_body = None
            y_after_body = None

        return y_after_title, y_before_body, y_after_body

    def image_page(self, image: Union[str, io.BytesIO]):
        img = ImageFile(image)
        self.base_page()

        if img.w_h_ratio > 1:  # landscape
            img.set_target_size(
                target_width=self.full_format[0] - 2 * self.image_margin
            )
            y_start = self.full_format[1] / 2 - img.target_h / 2
            self.image(
                image,
                x=self.image_margin,
                y=y_start,
                h=img.target_h,
                keep_aspect_ratio=True,
            )

        if img.w_h_ratio <= 1:  # portrait/square
            img.set_target_size(
                target_height=self.full_format[1] - 2 * self.image_margin
            )
            x_start = self.full_format[0] / 2 - img.target_w / 2
            self.image(
                image,
                x=x_start,
                y=self.image_margin,
                h=img.target_h,
                keep_aspect_ratio=True,
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
            y_image_space = self.full_format[1] - 2 * self.image_margin - sep
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
                y=self.image_margin,
                h=img1.target_h,
                keep_aspect_ratio=True,
            )
            self.image(
                img2.image,
                x=x_start,
                y=self.image_margin + img1.target_h + sep,
                h=img2.target_h,
                keep_aspect_ratio=True,
            )

        else:  # stack horizontally
            equalizer = img2.h / img1.h
            x_image_space = self.full_format[0] - 2 * self.image_margin - sep
            total_width_original = img1.w * equalizer + img2.w
            img1.set_target_size(
                target_width=(img1.w * equalizer * x_image_space) / total_width_original
            )
            img2.set_target_size(target_width=x_image_space - img1.target_w)
            y_start = self.full_format[1] / 2 - img1.target_h / 2
            self.image(
                img1.image,
                x=self.image_margin,
                y=y_start,
                h=img1.target_h,
                keep_aspect_ratio=True,
            )
            self.image(
                img2.image,
                x=self.image_margin + img1.target_w + sep,
                y=y_start,
                h=img2.target_h,
                keep_aspect_ratio=True,
            )

    def footer(self):
        # Gets called automatically by parent class
        if self.page_numbering and self.page_no() != 1:
            min_margin = min(self.text_margin, self.image_margin)
            self.set_y(self.full_format[1] - (min_margin / 3) * 2)
            self.set_font(size=20)
            self.cell(w=0, text=str(self.page_no() - 1), align="C")
            self.set_font(size=24)

    def create_output(self, path: str = None) -> Optional[bytearray]:
        if path:
            self.output(path)
        else:
            return self.output()  # still need to test!
