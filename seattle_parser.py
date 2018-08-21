#!/usr/bin/python3


import csv
import magic
import xlrd

from multiprocessing import Pool
from os import listdir

def file_prechecks(filepath):
    filetype = magic.from_file(filepath)

    if not filetype.startswith('Microsoft Excel'):
        return False

    return True

def excel_files(datadir='/opt/data/foia/seattle_emails'):
    files = listdir(datadir)
    ret = []

    for f in files:
        filepath = "%s/%s" % (datadir, f)
        if file_prechecks(filepath):
            ret.append(filepath)

    return ret

def ws_headers(ws):
    headers = ws.row_values(0)
    return headers

def convert_excel_time(timeval, datetype=0):
    if timeval:
        return xlrd.xldate_as_datetime(timeval, 0)
    else:
        return

def ws_rows(ws):
    headers = ws_headers(ws)
    ret = []
    for c in range(1, ws.nrows):
        row_dict = dict(zip(headers, ws.row_values(c)))
        row_dict['Sent'] = convert_excel_time(row_dict['Sent'])

        ret.append(row_dict)

    return ret

def parse_book(fp):
    book = xlrd.open_workbook(fp)
    first_worksheet = book.sheets()[0]
    rows = ws_rows(first_worksheet)

    return rows

def csv_writer(filepath='/opt/seattle_emails.csv', header=None):
    if not header:
        header = ['Sender or Created by', 'Recipients in To line', 
                  'Recipients in Cc line', 'Recipients in Bcc line', 'Sent']

    fh = open(filepath, 'w') 
    w = csv.DictWriter(fh, fieldnames=header)
    w.writeheader()

    return w

writer = csv_writer()
files = excel_files()

pool = Pool(processes=32)

print("hi")
parsed = pool.map(parse_book, files)
print("hey")

count=1
for rows in parsed:
    print("(%s/%s): %s" % (count, len(files), files[count-1]))
    if rows:
        writer.writerows(rows)

    count+=1

writer.close()
