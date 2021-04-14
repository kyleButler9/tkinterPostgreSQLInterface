from configparser import ConfigParser
import psycopg2

def config(ini_file='database.ini', ini_section='local_distribution_sheet'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(ini_file)

    # get section, default to postgresql
    db = {}
    if parser.has_section(ini_section):
        params = parser.items(ini_section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(ini_section, ini_file))

    return db

class DBI:
    def __init__(self,**kwargs):
        if 'ini_section' in kwargs:
            self.ini_section = kwargs['ini_section']
        self.connectToDB(self.ini_section)
    def connectToDB(self,ini_section):
        try:
            # read database configuration
            params = config(ini_section=ini_section)
            self.conn = psycopg2.connect(**params)
            self.cur = self.conn.cursor()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            return self
    def restartConnection(self,ini_section):
        if self.conn is not None:
            self.conn.close()
        print('\nretrying connection...\n')
        self.connectToDB(self.ini_section)
    def insertToDB(self,sql,*args):
        try:
            cur = self.conn.cursor()
            if len(args) != 0:
                cur.execute(sql,(*args,))
            else:
                cur.execute(sql)
            self.conn.commit()
            cur.close()
            out="success!"
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            print('\nretrying connection...\n')
            self.restartConnection(self.ini_section)
            try:
                cur = self.conn.cursor()
                if len(args) != 0:
                    cur.execute(sql,(*args,))
                else:
                    cur.execute(sql)
                self.conn.commit()
                cur.close()
                out="success!"
            except (Exception, psycopg2.DatabaseError) as error:
                out=error
            finally:
                pass
        finally:
            return out
    def fetchone(self,sql,*args):
        #returns one tuple
        if self.testConnection() == 0:
            self.restartConnection(self.ini_section)
        self.cur = self.conn.cursor()
        if len(args) != 0:
            self.cur.execute(sql,(*args,))
        else:
            self.cur.execute(sql)
        return self.cur.fetchone()

    def fetchall(self,sql,*args):
        #returns a list of tuples
        if self.testConnection() == 0:
            self.restartConnection(self.ini_section)
        if len(args) != 0:
            self.cur.execute(sql,(*args,))
        else:
            self.cur.execute(sql)
        return self.cur.fetchall()
    def testConnection(self):
        try:
            self.cur.execute("SELECT 1")
            back = self.cur.fetchone()[0]
        except:
            back = 0
        finally:
            return back
if __name__ == "__main__":
    DBI = DBI(ini_section='local_appendage')
    from datetime import datetime
    from sql import *
    now =datetime.now()
    DBI.cur.execute(DeviceInfo.noteWipedHD,(now,'abc',))
    print(len(DBI.cur.fetchall()))
