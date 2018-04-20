#!/usr/bin/python3


import csv
import magic
import xlrd

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
    for c in range(1, ws.nrows):
        row_dict = dict(zip(headers, ws.row_values(c)))
        row_dict['Sent'] = convert_excel_time(row_dict['Sent'])

        yield row_dict

def parse_book(book):
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

books = ( xlrd.open_workbook(f) for f in files )
parsed = ( parse_book(b) for b in books )

count=1
for rows in parsed:
    print("(%s/%s): %s" % (count, len(files), files[count-1]))
    if rows:
        writer.writerows(rows)

    count+=1

fh.close()