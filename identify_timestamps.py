#!/usr/bin/python3

import pyocr
import pyocr.builders

from PIL import Image

#def image_pixels(filepath):
#    img = Image.open(filepath)
#    pixels = im.load()
#
#    return pixels
#
#def image_rows(filepath):

filepath = '/opt/metadata/time_0.png'

img = Image.open(filepath)
rows = []


tools = pyocr.get_available_tools()[0]

builder = pyocr.builders.WordBoxBuilder

darkness_threshold = (img.width * 19) * .6
lightness_threshold = (img.width * 19) * .001

text_rows = []
empty_rows = []
bar_rows = []
too_low_rows = []

builder = pyocr.builders.LineBoxBuilder()

img = Image.open(filepath)
ocr_lines = tools.image_to_string(img, builder=builder, lang = 'eng')


crop_points = []
for line in ocr_lines:
    positions = line.position
    print(line.content)
