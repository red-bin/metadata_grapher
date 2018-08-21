#!/usr/bin/python3

import psycopg2
from PyPDF2 import PdfFileReader, PdfFileWriter
from io import BytesIO

from PIL import Image as PilImage

import pyocr
import pyocr.builders

from wand.image import Image
from wand.image import Color

tools = pyocr.get_available_tools()[0]
builder = pyocr.builders.LineBoxBuilder()

def pg_conn():
    connstr = "port=5432 dbname=houston_metadata host=%s user=houston_metadata password=houston_metadata" % "localhost"
    conn = psycopg2.connect(connstr)

    return conn



def page_to_png(page, path='/opt/data/cache/pdf_pages'):
    dst_pdf = PdfFileWriter()
    dst_pdf.addPage(page)

    pdf_bytes = BytesIO()
    dst_pdf.write(pdf_bytes)
    pdf_bytes.seek(0)

    img = Image(file=pdf_bytes, resolution=300, background=Color("white"))
    png = img.convert("png")

    #get hash of image to avoid collisions
    filepath = "%s/%s.png" % (path, img.signature)
    png.save(filename=filepath)

    image = PilImage.open(filepath)

    return image, filepath

def ocr_pdf_page(page):
    png, _ = page_to_png(page)
    built_strings = tools.image_to_string(png, builder=builder)

    return built_strings

def pdf_to_pngs(path, count=2):
    r = PdfFileReader(path)

    c = 0
    for page in r.pages:
        image, fp = page_to_png(page)
        return (image, fp)
