from extractionAppendage import *
import tkinter as tk
import sys
import os
import tkinter as tk
from config import DBI
import psycopg2

class PrintHids(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args)
        DBI.__init__(self,ini_section = kwargs['ini_section'])
        self.donationIDVar = tk.StringVar()
        self.printer=kwargs['printer']
        DonationBanner(parent,ini_section=kwargs['ini_section'],donationIDVar=self.donationIDVar)
        tk.Label(parent,text='How Many Hids?').pack()
        self.hidCount = tk.Entry(parent,width=10)
        self.hidCount.pack()
        self.printIt = tk.Button(parent,
            text='Print',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.printIt.bind('<Button-1>',self.printToZebra)
        self.printIt.pack()
        self.err = tk.StringVar(parent)
        self.errMsg = tk.Label(parent,textvariable=self.err).pack()
    def printToZebra(self,event):
        try:
            hidCount = int(self.hidCount.get())
        except ValueError:
            self.err.set("Count: " +self.hidCount.get()+" \ncan't be converted to an integer.")
            self.hidCount.delete(0,'end')
            return self
        try:
            maxmin = self.UpdateHidsLog(hidCount)
            getLotNumber = \
            """
            SELECT lotnumber from donations where donation_id = %s;
            """
            lotnum = self.fetchone(getLotNumber,self.donationIDVar.get())[0]
            headerFile = open('header.prn','r')
            header = headerFile.read()
            file = open('out.prn','w')
            file.write(header)
            for i in range(maxmin[1]+1,maxmin[0]+1):
                file.write(self.hidTemplate(lotnum,i))
            file.close()
        except TypeError:
            self.err.set('No lotnumber associated with that donation...')
        try:
            os.system("powershell \" Get-Content -Path .\out.prn | Out-Printer -Name '{}'\"".format(self.printer))
        except:
            self.err.set('problem printing.')
        finally:
            return self
    def UpdateHidsLog(self,max):
        try:
            logStatement = \
            """
            With currentMax as (SELECT maxHidIter,donation_id from donations
                                WHERE donation_id = %s)
            UPDATE donations
            SET maxHidIter = maxHidIter + %s
            WHERE donation_id = (select donation_id from currentMax)
            RETURNING maxHidIter,(select maxHidIter from currentMax);
            """
            maxmin = self.fetchone(logStatement,self.donationIDVar.get(),max)
            self.conn.commit()
            return maxmin
        except (Exception, psycopg2.DatabaseError) as error:
             self.err.set(error)
             return None

    def hidTemplate(self,prefix,iter):
        Hid = \
"""
^XA
^MMT
^PW450
^LL0180
^LS0
^BY3,3,79^FT83,114^BCN,,Y,N
^FD>;{}>6{}-{}^FS
^PQ1,0,1,Y^XZ""".format(str(prefix)[:-1],str(prefix)[-1],iter)
        return Hid

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Hard Drive Extraction Station")
    printer = sys.argv[1]
    #printer = 'USB003 ZPL'
    app = PrintHids(root,ini_section='appendage',printer=printer)
    app.mainloop()
