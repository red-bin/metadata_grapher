#!/usr/bin/python3

from time import sleep

from multiprocessing import Pool
from selenium import webdriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from PyPDF2 import PdfFileReader, PdfFileWriter

from os import listdir

import json
import re
import psutil

def div_xy(div):
    raw_style = div.get_attribute("style")
    raw_style = raw_style.split(';')
    
    left_pos, top_pos = None, None
    for style in raw_style:
        style = style.strip()

        if style.startswith('left:'):
            left_pos = float(style.split(':')[1].strip()[:-2])
            
        elif style.startswith('top:') :
            top_pos = int(float(style.split(':')[1].strip()[:-2]))

    return left_pos, top_pos

def parse_div(div):
    bottom_buffer = None
    x, y = div_xy(div)
    width = div.size['width']
    text = div.text

    ret = {'x':x, 'y':y, 'width':width, 'text':text} 

    return  ret

def get_header():
    d = new_driver()

    d.get("file:///opt/data/foia/DOIT -- domain name log.pdf")
    sleep(2)
    text_layer = d.find_element_by_class_name("textLayer")
    divs = text_layer.find_elements_by_tag_name("div")[:6]

    header_data = [parse_div(d) for d in divs]

    if not header_data:
        print("No header found")
        exit()

    d.close()

    print("Headers: " % header_data)
    return header_data

def new_driver():
    tries = 0
    while tries < 10:
        try:
            driver = webdriver.Firefox() 
            return driver
        except:
            print("Could not create FF instance. Waiting 3s..")
            tries += 1
            sleep(5)

def page_lines(cache_fp):
    print("%s: launching firefox" % cache_fp)

    d = new_driver()
    try:
        d.get("file://%s" % cache_fp)
        sleep(5)
    except:
        d.close()
        return page_lines(cache_fp)

    d.find_element_by_class_name("textLayer")

    line_elems = []
    text_buffer = []

    text_layer = d.find_element_by_class_name("textLayer")
    divs = text_layer.find_elements_by_tag_name("div")

    if divs[0].text == 'From':
        divs = divs[6:] #ignore header

    print("parsing divs: %s" % cache_fp)
    for div in divs:
        parsed_div = parse_div(div)
        text_buffer.append(parsed_div)

        if re.match('[0-9]{1,2}:[0-9][0-9]:[0-9][0-9]', parsed_div['text']):
            line_elems.append(text_buffer)
            text_buffer = []

    print("Finished with divs, closing driver for %s" % cache_fp)
    d.close()
    sleep(1)

    print(line_elems)

    return line_elems

def save_page(page_no):
    print("saving page no %s" % page_no)
    dst_fp = '/opt/data/cache/pdf_pages/%s.pdf' % page_no
    pdf_reader = PdfFileReader('/opt/data/foia/DOIT -- domain name log.pdf')

    page = pdf_reader.getPage(page_no)
    dst_fh = open(dst_fp, 'wb')
    dst_pdf = PdfFileWriter()

    dst_pdf.addPage(page)
    dst_pdf.write(dst_fh)

    return dst_fp

def pdf_to_caches():
    print("Testing with pool # of %s" % 31)
    pool = Pool(processes=int(31))
    fps_ret = pool.map(save_page, list(range(1,1751)))

    return fps_ret
   

cache_dir = '/opt/data/cache/pdf_pages'
cache_fps = pdf_to_caches()

cache_fps = sorted(['%s/%s' % (cache_dir, f) for f in listdir(cache_dir)])

pool = Pool(processes=5)
results = pool.map(page_lines, cache_fps)

fh = open('/opt/data/pdf_poses.json','w')
json.dump(results, fh)

fh.close()

header_dets = get_header()

###########copy and paste from notebook########

import csv
import operator

import matplotlib
import numpy as np

import json

pages = json.load(open('/opt/data/pdf_poses.json','r'))

rows = []
_ = [ [rows.append(r) for r in p] for p in pages]


def within_header(x, width):
    for header_col in header_dets:
        header_x = header_col['x']
        header_width = header_col['width']
        if x >= header_x and x <= (header_width + header_x):
            return header_col
        elif header_x >= x and header_x <= (width + x):
            return header_col


farthest_left = 9999

col_divs = {key: [] for key in [d['text'] for d in header_dets]}

bad_divs = []
div_count = 0
for row in rows:
    for div in row:
        div_count+=1
        col_div = within_header(div['x'], div['width'])
        if col_div:
            col_divs[col_div['text']].append(div)
        else: #this is where the problem is at
            bad_divs.append(div)
print("count of divs: %s" % div_count)
print("count of bad divs: %s" % len(bad_divs))
            
col_bounds = {}
for header_key, divs in col_divs.items():
    largest_width = 0
    min_x, max_x = 9999, 0
    
    header_det = [h for h in header_dets if h['text'] == header_key][0]
    
    for div in divs:
        if div['width'] > largest_width:
            largest_width = div['width']
        if div['x'] < farthest_left:
            farthest_left = div['x']
        if div['x'] <= min_x:
            min_x = div['x']
         
        div_x2 = div['x'] + div['width']
        if div_x2 > max_x:
            max_x = div_x2
            
    column_end = ((header_det['x'] + (header_det['width']/2) - min_x) * 2)
    
    if max_x > column_end:
        column_end = max_x
    
    if min_x > header_det['x']:
        header_center = header_det['x'] + (header_det['width']/2)
        column_width = max_x -((max_x - header_center)*2)
    
    start, end = min_x, column_end
    col_bounds[header_key] = [start, end]

print([h for h in header_dets if h['text'] == 'To'][0])

header_names = ['From', 'To', 'CC', 'BCC', 'DateSent', 'TimeSent']

prev = 'From'
for h in header_names[1:]:
    if col_bounds[h][0] <= col_bounds[prev][1]:
        col_bounds[prev][1] = col_bounds[h][0]
    prev = h
print(col_bounds)

def within_bounds(x, width):
    x = x-1
    possibles = {}
    
    ret = []
    
    for k,v in sorted(col_bounds.items(), key=operator.itemgetter(0)):
        bound_start, bound_end = v

        if x > bound_start and x < bound_end:
            ret.append(k)
        
        elif bound_start > x and bound_start < (width + x):
            ret.append(k)

    
    fields = ['From', 'To', 'CC', 'BCC', 'TimeSent', 'DateSent']
    for f in reversed(fields):
        for r in ret:
            if r == f:
                return f
        
col_bounds

def cells_to_dict(row_keypairs):
    row_results = {}
    for header, cell_divs in row_keypairs.items():
        cell_results = []
        ys = {}
        for div in cell_divs:
            if 'mark.mejia@chicago' in div['text']:
                print(div)
            div_y = div['y']
            if div_y not in ys.keys():
                ys[div_y] = []
            ys[div_y].append(div)
        
        for y, divs in sorted(ys.items(), key=operator.itemgetter(0)):
            y_texts = ' '.join([d['text'] for d in divs])
            cell_results.append(y_texts)
            
        row_results[header] = ' '.join(cell_results)
        
    return row_results

row_results = []
wrong_divs = []
right_divs = []
rows = []
_ = [ [rows.append(r) for r in p] for p in pages]
for row in rows:
    row_keypairs = {key: [] for key in [d['text'] for d in header_dets]}
    for div in row:
        div_header = within_bounds(div['x'], div['width'])
        if div_header:
            row_keypairs[div_header].append(div)
            right_divs.append(div)            
        else:
            wrong_divs.append(div)
    recombined = cells_to_dict(row_keypairs)

    for h in ['From','To','CC','BCC']:
        recombined[h] = recombined[h].replace('\n','')
        
    row_results.append(cells_to_dict(row_keypairs))    

print(len(wrong_divs), row_results[5380]['DateSent'])

fh = open('/opt/data/foia/chicago_metadata.csv','w')
w = csv.DictWriter(fh, fieldnames=['From','To','CC','BCC','TimeSent','DateSent'])
w.writeheader()
w.writerows(row_results)
fh.close()
