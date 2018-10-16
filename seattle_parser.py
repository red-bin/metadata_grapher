#!/usr/bin/python3


import csv
import magic
import xlrd

import re

from multiprocessing import Pool
from os import listdir

email_re = re.compile('([^>]*)<([^>]*)>')

def parse_rawaddr(raw_addr):
    matched = re.match(email_re, raw_addr)
    if matched:
        addr, alias = map(str.rstrip, matched.groups())

    else:
        alias = None
        addr = None

    return alias, addr

def parse_addrs(addr_str):
    if not addr_str:
        return []

    raw_addrs = addr_str.split(';')

    ret = []
    ret = ( parse_rawaddr(a) for a in raw_addrs )

    return(ret)

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

    return ['/opt/data/foia/seattle_emails/PPN-SAO.xlsx']

    #return ret

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

    return w

#def graphiphy(rows):
    #for row in rows:
        #ccs = row['Recipients in Cc line']
        #bccs = row['Recipients in Bcc line']
        #tos = row['Recipients in To line']
        #sender = row['Sender or Created by']
        #sent_time = row['Sent']
#
        #sql_row = [sender, 

files = excel_files()

pool = Pool(processes=31)

print("Cacheing excel data")

parsed = pool.map(parse_book, files)

print("Writing CSV")

header = ['Sender or Created by', 'Recipients in To line', 
          'Recipients in Cc line', 'Recipients in Bcc line', 'Sent']

filepath = '/opt/data/seattle_ppnsao.csv'
fh = open(filepath, 'w')
writer = csv.DictWriter(fh, fieldnames=header)

[ writer.writerows(p) for p in parsed ]

count=1
for rows in parsed:
    print("(%s/%s): %s" % (count, len(files), files[count-1]))
    if rows:
        graph_rows = graphiphy(rows)
        writer.writerows(rows)

    count+=1

fh.close()

