from photo_book import PhotoBook
from trip_data import PolarStepsData

path = "data/zuid-india/"
data = PolarStepsData(path)  # title can be specified here
photo_book = PhotoBook(data, path, True)
photo_book.add_geo_map()
photo_book.add_steps()
photo_book.output_book(output_path="data/book-out.pdf")
