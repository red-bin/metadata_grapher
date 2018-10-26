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
    address = re.sub("['\"]", '', address).strip().lower()
    return address

def process_line(data):
    sender, tos, ccs, bccs, time, book = data

    if not sender:
        return [] 

    sender = clean_address(sender)
    if re.search('\<.*@.*\>$', sender):
        sender = re.split('[<>]', sender)[1]

    line_data = []

    for to in re.split('(;|>,)', tos)[::2]:
        if to:
            line_data.append((sender, clean_address(to), time, 'to', book))

    for cc in re.split('(;|>,)', ccs)[::2]:
        if cc:
            line_data.append((sender, clean_address(cc), time, 'cc', book))

    for bcc in re.split('(;|>,)', bccs)[::2]:
        if bcc:
            line_data.append((sender, clean_address(bcc), time, 'bcc', book))

    return line_data

print("Cacheing data")
lines = tuple([l for l in r])

print("edging cached data by email")

pool = Pool(processes=24)
#emails = pool.map(process_line, lines)
emails = tuple([process_line(l) for l in lines])

##create nodes file
nodes_fh = open('/opt/data/testdata/nodes.csv','w')
nodes_writer = csv.writer(nodes_fh)

print("preparing nodes for indexing")
nodes = []

for email in emails:
    for edge in email:
        from_node = edge[0]
        recip_node = edge[1]

        dopass = False
        for i in ignores:
            if i in from_node:
                dopass = True
                break
            
            if i in recip_node:
                dopass = True
                break

        if dopass:
            continue

        if from_node:
            nodes.append(from_node)

        if recip_node:
            nodes.append(recip_node)

print("indexing nodes")
nodes = tuple(set(nodes))
indexed_nodes = dict([ (nodes[n],n) for n in range(0, len(nodes))])

print("writing nodes file")
nodes_writer.writerow(['Label','Id'])
nodes_writer.writerows(indexed_nodes.items())

nodes_fh.close()

##create edges file
print("writing edges file")
edges_fh = open('/opt/data/testdata/seattle_edges.csv', 'w')
edge_writer = csv.writer(edges_fh)
edge_writer.writerow("Source,Target,Time,Email_Type,Email_ID".split(','))
edges = []
email_no = 1
for email in emails:
    for edge in email:
        edge = list(edge)
        try:
            if edge[0]:
                edge[0] = indexed_nodes[edge[0]]
        except:
            continue
        try:
            if edge[1]:
                edge[1] = indexed_nodes[edge[1]]
        except:
            continue
        try:
            if edge[2]:
                edge[2] = datetime.strptime(edge[2], '%Y-%m-%d %H:%M:%S').isoformat()
        except:
            continue 

        edge.append(email_no)

        edge_writer.writerow(edge)

        email_no+=1

edges_fh.close()
