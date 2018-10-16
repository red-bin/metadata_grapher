#!/usr/bin/python3

import csv
import re

from datetime import datetime

from multiprocessing import Pool

edges = []


fp = '/opt/data/seattle_ppnsao.csv'
fh = open(fp)
r = csv.reader(fh)
r.__next__() #skip header

def clean_address(address):
    address = re.sub("['\"]", '', address).strip()
    return address

def process_line(data):
    sender, tos, ccs, bccs, time = data

    if not sender:
        return [] 

    sender = clean_address(sender)
    if re.search('\<.*@.*\>$', sender):
        sender = re.split('[<>]', sender)[1]

    line_data = []

    for to in re.split('(;|>,)', tos):
        if to:
            if not to:
                continue
            line_data.append((sender, clean_address(to), time, 'to'))

    for cc in re.split('(;|>,)', ccs):
        if cc:
            line_data.append((sender, clean_address(cc), time, 'cc'))

    for bcc in re.split('(;|>,)', bccs):
        if bcc:
            line_data.append((sender, clean_address(bcc), time, 'bcc'))

    return line_data

print("Cacheing data")
lines = (l for l in r)

print("edging cached data by email")

pool = Pool(processes=24)
#emails = pool.map(process_line, lines)
emails = tuple([process_line(l) for l in lines])

##create nodes file
nodes_fh = csv.writer(open('/opt/data/testdata/nodes.csv','w'))

print("preparing nodes for indexing")
nodes = []
for email in emails:
    for edge in email:
        from_node = edge[0]
        recip_node = edge[1]
        if from_node:
            nodes.append(from_node)

        if recip_node:
            nodes.append(recip_node)

print("indexing nodes")
nodes = list(tuple(set(nodes)))
indexed_nodes = dict([ (nodes[n],n) for n in range(0, len(nodes))])

print("writing nodes file")
nodes_fh.writerow(['Label','Id'])
nodes_fh.writerows(indexed_nodes.items())

##create edges file
print("writing edges file")
edge_writer = csv.writer(open('/opt/data/testdata/seattle_edges.csv', 'w'))
edge_writer.writerow("Source,Target,Time,Type,Email_ID".split(','))
edges = []
email_no = 1
for email in emails:
    for edge in email:
        edge = list(edge)
        if edge[0]:
            edge[0] = indexed_nodes[edge[0]]
        if edge[1]:
            edge[1] = indexed_nodes[edge[1]]
        if edge[2]:
            edge[2] = datetime.strptime(edge[2], '%Y-%m-%d %H:%M:%S').isoformat()

        edge.append(email_no)

        edge_writer.writerow(edge)

    email_no+=1
