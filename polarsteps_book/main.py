from trip_data import PolarStepsData
from pdf_file import PDFFile
from geo_map import GeoMap
from photo_book import PhotoBook

path = "data/zuid-india/"
data = PolarStepsData(path) # title can be specified here
photo_book = PhotoBook(data, path)
photo_book.add_geo_map()
photo_book.add_steps()
photo_book.output_book(output_path="data/book-out.pdf")
