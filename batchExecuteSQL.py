import psycopg2
from config import config
from sql import *

testCommand = ('SELECT 1',)
def batchExecuteSqlCommands(ini_section,commands=testCommand):
    conn = None
    try:
        # read the connection parameters
        params = config(ini_section=ini_section)
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    #batchExecuteSqlCommands('local_appendage',commands=DBAdmin.dropTablesCommands)
    batchExecuteSqlCommands('appendage',commands=DBAdmin.createTableCommands)
    batchExecuteSqlCommands('appendage',commands=DBAdmin.initializeDatabaseCommands)
