#!/usr/bin/python3

import cv2
import numpy
import pyocr
import pyocr.builders

from wand.image import Image
from wand.image import Color

from PyPDF2 import PdfFileReader, PdfFileWriter
from PIL import Image as PilImage
from io import BytesIO


def page_to_png(page):
    dst_pdf = PdfFileWriter()
    dst_pdf.addPage(page)

    pdf_bytes = BytesIO()
    dst_pdf.write(pdf_bytes)
    pdf_bytes.seek(0)

    img = Image(file=pdf_bytes, resolution=700, background=Color("white"))
    png = img.convert("png")
    png.save(filename='/opt/data/tmp.png')

    image = PilImage.open('/opt/data/tmp.png')

    return image

filepath = '/opt/data/foia/DOIT -- domain name log.pdf'
pdf_reader = PdfFileReader(filepath)

for page_no in range(len(pdf_reader.pages)):
    field_poses = (0.0636363, 0.2780818, 0.587272727, 0.721818182, 0.8055, .8628, .917)

    pdf_page = pdf_reader.getPage(page_no)
    break

    png = page_to_png(pdf_page)
    png = png.convert('L')

    page_width = png.width
    page_height = png.height

    from_end = int(page_width * field_poses[1])
    to_end = int(page_width * field_poses[2])
    cc_end = int(page_width * field_poses[3])
    bcc_end = int(page_width * field_poses[4])
    date_end = int(page_width * field_poses[5])
    time_end = int(page_width * field_poses[6])

    from_start = int(page_width * field_poses[0])
    to_start = from_end
    cc_start = to_end
    bcc_start = cc_end
    date_start = bcc_end
    time_start = date_end

    from_column = png.crop((from_start, 0, from_end, page_height))
    to_column = png.crop((to_start, 0, to_end, page_height))
    cc_column = png.crop((cc_start, 0, cc_end, page_height))
    bcc_column = png.crop((bcc_start, 0, bcc_end, page_height))
    date_column = png.crop((date_start, 0, date_end, page_height))
    time_column = png.crop((time_start, 0, time_end, page_height))

    tools = pyocr.get_available_tools()[0]
    builder = pyocr.builders.LineBoxBuilder()
    ocr_lines = tools.image_to_string(time_column, builder=builder)

    row_ends = [ l.position[-1][-1] for l in ocr_lines if l.content.strip() ]

    cells = []
    top = row_ends.pop()
    while row_ends:
        bot = row_ends.pop()
        cells.append(png.crop((to_start, bot, to_end, top+10)))
        top = bot

    cell_strings = []
    for c in cells:
        #c.save('/tmp/test123.png')
        cell_strings.append(tools.image_to_string(c, builder=builder))

    print([ [i.content for i in c ] for c in cell_strings ])
    break
