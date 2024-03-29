#!/usr/bin/python
import os

import psycopg2

"""
Comments:
This class should be rewritten so it can be called like:
with open('blabla', 'r/w') as DBpointer:
    # Further processing goes here
How:
def __init__(self)
def __enter__(self):
    self.fd = open(self.dev, MODE)
    return self.fd
def __exit__(self, type, value, traceback):
    #Exception handling here
    close(self.fd)
"""


class Database:

    def __init__(self):
        """ initalize class and get connection parameters """
        self.conn = None
        self.db_params = {
            "host": "postgres",
            "database": "postgres",
            "user": os.environ['POSTGRES_USER'],
            "password": os.environ['POSTGRES_PASSWORD'],
            "port": 5432
        }

    def connect(self):
        """ Connect to the PostgreSQL database server """
        try:
            # connect to the PostgreSQL server
            self.conn = psycopg2.connect(**self.db_params)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    # to retrieve actual values from the database
    def retrieveValues(self, request):
        # create a cursor
        cur = self.conn.cursor()

        cur.execute(request)

        result = cur.fetchall()

        # close the communication with the PostgreSQL
        cur.close()

        return result

    # execute raw sql commands (no data fetching possible, only things like UPDATE etc.
    def execute(self, request):
        # create a cursor
        cur = self.conn.cursor()

        cur.execute(request)

        self.conn.commit()
        # close the communication with the PostgreSQL
        cur.close()

    def getVersion(self):
        try:
            print('PostgreSQL database version:')
            db_version = self.retrieveValues('SELECT version()')
            print(db_version)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def getTestTableMeta(self):
        try:
            print('test:')
            db_version = self.retrieveValues('SELECT * FROM information_schema.tables WHERE table_name = \'test\'')
            print(db_version)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def close(self):
        if self.conn is not None:
            self.conn.close()

    def __del__(self):
        self.close()
