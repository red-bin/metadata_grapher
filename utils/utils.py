#!/usr/bin/python3

import psycopg2

def pg_conn():
    connstr = "port=5432 dbname=houston_metadata host=%s user=houston_metadata password=houston_metadata" % "localhost"
    conn = psycopg2.connect(connstr)

    return conn
