#!/usr/bin/python3

import re
import psycopg2

import matplotlib.pyplot as plt
import networkx as nx

from bokeh.io import show, output_file
from bokeh.plotting import figure
from bokeh.models.graphs import from_networkx

def pg_conn():
    connstr = "port=5432 dbname=metadata host=%s user=metadata password=metadata" % "localhost"
    conn = psycopg2.connect(connstr)

    return conn

def email_ids():
    conn = pg_conn()
    curs = conn.cursor()

    sqlstr = """SELECT email_id, sender_addr, recip_addr, 
                       comm_type, sent_time, received_time
                FROM email_communications"""

    curs.execute(sqlstr)
    results = curs.fetchall()

    return results

def email_comms():
    conn = pg_conn()
    curs = conn.cursor()

    sqlstr = """SELECT email_id, sender_addr, recip_addr, 
                       comm_type, sent_time, received_time
                FROM email_communications"""

    curs.execute(sqlstr)

    results = curs.fetchall()
    conn.close()

    return results

def email_edges():
    conn = pg_conn()
    curs = conn.cursor()

    sqlstr = """SELECT sender_addr, recip_addr
                FROM email_communications"""

    curs.execute(sqlstr)

    results = curs.fetchall()
    conn.close()
    return results

def unique_addrs():
    conn = pg_conn()
    curs = conn.cursor()

    sqlstr = """(SELECT distinct(sender_addr)
                FROM email_communications)
                UNION 
                (SELECT distinct(recip_addr)
                FROM email_communications)
                """
    curs.execute(sqlstr)

    results = curs.fetchall()
    conn.close()

    return results

def create_email_graph():
    email_graph = nx.Graph()

    email_graph.add_nodes_from(unique_addrs())
    email_graph.add_edges_from(email_edges())

    return email_graph 

def show_email_graph(size=None, options=None):
    if not options:
        options = {'node_color': 'black', 'node_size': 10, 'width': 1}
 
    graph = create_email_graph()

    #nx.draw_kamada_kawai(graph, **options)
    nx.draw(graph, **options)

    plt.savefig("houston_graph.png")
    plt.show()




plot = figure(title="Networkx Integration Demonstration",
              tools="", toolbar_location=None)

G = create_email_graph()

bokeh_graph = from_networkx(G, nx.spring_layout, scale=2)
plot.renderers.append(bokeh_graph)

output_file("networkx_graph.html")
show(plot)
