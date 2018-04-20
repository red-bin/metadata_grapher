#!/bin/bash

set -e

DBUSER="metadata"
DBNAME="metadata"

SQLDIR="/home/matt/git/metadata_grapher/sql"
DATADIR="/opt/data/foia"

export HOUSTON_METADATA_PATH="$DATADIR/coh_email_metadata_1Q17.csv"

function test_mode {
    HOUSTON_METADATA_PATH="$DATADIR/houston_emails.test.csv"
}

function sql_from_file {
    echo "running $SQLDIR/$1" 
    time psql -p5432 -d $DBNAME -U $DBUSER \
              -v houston_metadata_path="'$HOUSTON_METADATA_PATH'" \
                 < $SQLDIR/$1
}

#test_mode

echo "CREATE A TEST FILE"

echo "restarting postgres"
#sudo service postgresql restart
sudo su postgres -c "psql -p 5432 < $SQLDIR/init_db.sql"

sql_from_file create_tables.sql

echo "Inserting data"
./insert_data.py #needed because psql doesn't accept doublequotes.

#sql_from_file setup_triggers.sql
#sql_from_file load_from_files.sql
