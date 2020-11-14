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


class database:

    def __init__(self):
        """ initalize class and get connection parameters """
        self.conn = None
        self.db_params = {}
        db_params["host"] = "localhost"
        db_params["database"] = "postgres"
        db_params["user"] = os.environ['POSTGRES_USER']
        db_params["password"] = os.environ['POSTGRES_PASSWORD']
        db_params["port"] = 5432


    def connect(self):
        """ Connect to the PostgreSQL database server """
        try:
            # connect to the PostgreSQL server
            self.conn = psycopg2.connect(**self.db_params)         
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)


    def execute(self, request):
        # create a cursor
        cur = self.conn.cursor()

        cur.execute(request)

        result = cur.fetchone()

        # close the communication with the PostgreSQL
        cur.close()

        return result


    def getVersion(self):
        print('PostgreSQL database version:')
        db_version = self.execute('SELECT version()') 
        print(db_version)

    def close(self):
        if self.conn is not None:
            self.conn.close()

    def __del__(self):
        self.close()


if __name__ == '__main__':
    db = database()
    db.connect()
    db.getVersion()



