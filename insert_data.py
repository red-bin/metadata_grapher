#!/usr/bin/python3

import csv
import re
import psycopg2

from os import environ

connstr = "port=5432 dbname=metadata host=%s user=metadata password=metadata" % "localhost"
conn = psycopg2.connect(connstr)
c = conn.cursor()

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

def insert_email(source):
    sql = "INSERT INTO emails (source) values ('houston') RETURNING id"

    c.execute(sql)
    ret_id = c.fetchone()[0]
    return ret_id

filepath = environ['HOUSTON_METADATA_PATH']
fh = open(filepath)
r = csv.reader(fh)

header = r.__next__()

failed = []
to_execute = []

def email_vals(data):
    sql_vals = []
    for sender_addr, to_addr, cc_addr, bcc_addr, sent_ts, received_ts in data:
        parsed_sender = parse_addrs(sender_addr)
        parsed_to = parse_addrs(to_addr)
        parsed_cc = parse_addrs(cc_addr)
        parsed_bcc = parse_addrs(bcc_addr)

        if not sent_ts:
            sent_ts = None
        if not received_ts:
            sent_ts = None
    
        email_id = insert_email('houston')
    
        if not sent_ts:
            sent_ts = None
        if not received_ts:
            received__ts = None
    
        for sender_addr, sender_alias in parsed_sender:
            for to_addr, to_alias in parsed_to:
                 yield (email_id, sender_addr, sender_alias, 
                              to_addr, to_alias, 'to', sent_ts, received_ts)
    
            for cc_addr, cc_alias in parsed_cc:
                 yield (email_id, cc_addr, cc_alias, 
                              cc_addr, cc_alias, 'cc', sent_ts, received_ts)
    
            for bcc_addr, bcc_alias in parsed_bcc:
                 yield (email_id, bcc_addr, bcc_alias, 
                              bcc_addr, bcc_alias, 'bcc', sent_ts, received_ts)

sqlstr = "INSERT INTO email_communications (email_id, sender_addr, sender_alias, recip_addr, recip_alias, comm_type, sent_time, received_time) values (%s, %s, %s, %s, %s, %s, %s, %s)"

email_data = email_vals(r)
email_data_test = ( email_data.__next__() for z in range(10000) )

c.executemany(sqlstr, (email_data_test))
conn.commit()
