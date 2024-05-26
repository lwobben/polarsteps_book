import random

from photo_book import PhotoBook
from trip_data import PolarStepsData

path = random.choice(["data/zuid-india/", "data/colombia-panama/"])
data = PolarStepsData(path)  # title can be specified here
photo_book = PhotoBook(data, path, bleed=0)
if path == "data/zuid-india/":
    photo_book.add_geo_map(countries_filter=["India"])  # SSL error? to do: look into
elif path == "data/colombia-panama/":
    photo_book.add_geo_map(countries_filter=["Panama", "Colombia"])
photo_book.add_steps()
photo_book.output_book(output_path="data/book-out.pdf")
