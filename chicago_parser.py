#!/usr/bin/python3

import csv
import cv2
import numpy
import pyocr
import pyocr.builders

from wand.image import Image
from wand.image import Color

from pprint import pprint

from PyPDF2 import PdfFileReader, PdfFileWriter
from PIL import Image as PilImage
from io import BytesIO

from multiprocessing import Pool

def page_to_png(page, page_no):
    dst_pdf = PdfFileWriter()
    dst_pdf.addPage(page)

    pdf_bytes = BytesIO()
    dst_pdf.write(pdf_bytes)
    pdf_bytes.seek(0)

    img = Image(file=pdf_bytes, resolution=300, background=Color("white"))
    png = img.convert("png")
    png.save(filename='/opt/data/%s.png' % page_no)

    image = PilImage.open('/opt/data/%s.png' % page_no)

    return image

filepath = '/opt/data/foia/DOIT -- domain name log.pdf'
pdf_reader = PdfFileReader(filepath)

tools = pyocr.get_available_tools()[0]
builder = pyocr.builders.LineBoxBuilder()

fh = open('/tmp/testwriter.csv','w')
output_writer = csv.DictWriter(fh, fieldnames=['to','from','cc','bcc','date','time'])
output_writer.writeheader()

def text_from_cell(png, left, bot, right, top):
    axes = (left, bot, right, top)
    txt_list = tools.image_to_string(png.crop(axes), builder=builder)
       
    txt = '\0'.join([t.content for t in txt_list if t])
    txt = txt.strip('\0')

    return txt

def parse_page(page_no):
    print('parsing page: %s' % page_no)
    field_poses = (0.0636363, 0.2780818, 0.587272727, 0.721818182, 0.8055, .8628, .917)
    pdf_page = pdf_reader.getPage(page_no)

    png = page_to_png(pdf_page, page_no)
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

    time_column = png.crop((time_start, 0, time_end, page_height))
    ocr_lines = tools.image_to_string(time_column, builder=builder)

    row_ends = [(l.position[-1][-1],l.content) for l in ocr_lines if l.content.strip() and l.content != 'TimeSent']
    row_ends.sort(key=lambda x: x[0])

    top,ts = row_ends.pop()
    row_data = []

    while row_ends:
        bot, bot_ts = row_ends[-1]

        from_txt = text_from_cell(png, from_start, bot, from_end, top+10)
        to_txt = text_from_cell(png, to_start, bot, to_end, top+10)
        cc_txt = text_from_cell(png, cc_start, bot, cc_end, top+10)
        bcc_txt = text_from_cell(png, bcc_start, bot, bcc_end, top+10)
        date_txt = text_from_cell(png, date_start, bot, date_end, top+10)
        time_txt = ts

        cell_data = {'to':to_txt, 'from': from_txt,
                     'cc':cc_txt, 'bcc': bcc_txt,
                     'date':date_txt, 'time':time_txt}

        row_data.append(cell_data)
        top, ts = row_ends.pop()

    return reversed(row_data)

pool = Pool(processes=4)
rows = pool.map(parse_page, list(range(len(pdf_reader.pages))))
