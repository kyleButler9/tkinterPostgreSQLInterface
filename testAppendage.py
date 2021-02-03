import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import datetime
import re
from sql import *
from config import DBI


class SNPK(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent)
        DBI.__init__(self,ini_section=kwargs['ini_section'])
        self.microsoftSNLabel = tk.Label(parent,text="Microsoft SN:")
        self.microsoftPKLabel = tk.Label(parent,text="Microsoft PK")
        self.microsoftSN = tk.Entry(parent,fg='black',bg='white',width=15)
        self.microsoftPK = tk.Entry(parent,fg='black',bg='white',width=20)
        self.microsoftSNLabel.grid(column=0,row=0)
        self.microsoftSN.grid(row=0,column=1)
        self.microsoftPKLabel.grid(row=1,column=0)
        self.microsoftPK.grid(row=1,column=1)
        self.submitSNPK = tk.Button(parent,
            text='submit',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.submitSNPK.bind('<Button-1>',self.insertSNPK)
        self.submitSNPK.grid(row=2,column=1)
        self.err = tk.StringVar(parent)
        self.errorLabel = tk.Label(parent,textvariable=self.err)
        self.errorLabel.grid(row=2,column=0)
    def insertSNPK(self,event):
        pk=self.microsoftPK.get()
        sn=self.microsoftSN.get()
        back = self.insertToDB(testStation.insertSNPK,sn,pk)
        self.err.set(back)
        self.microsoftPK.delete(0,'end')
        self.microsoftSN.delete(0,'end')
class AssociatePidAndLicense(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent)
        DBI.__init__(self,ini_section=kwargs['ini_section'])
        deviceQualities = self.fetchall(DeviceInfo.getDeviceQualities)
        qtypes =[quality[0] for quality in deviceQualities]
        self.qualityName = tk.StringVar(parent,value="quality:")
        self.qualityDD = tk.OptionMenu(parent,self.qualityName,"quality:",*qtypes)
        self.snLabel = tk.Label(parent,text="Microsoft Serial Number:")
        self.pidLabel = tk.Label(parent,text="device PID:")
        self.pid = tk.Entry(parent,fg='black',bg='white',width=15)
        self.sn = tk.Entry(parent,fg='black',bg='white',width=15)
        self.submitMatch = tk.Button(parent,
            text='submit',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.submitMatch.bind('<Button-1>',self.submit)
        self.pidLabel.grid(row=0,column=0)
        self.pid.grid(row=0,column=1)
        self.snLabel.grid(row=1,column=0)
        self.sn.grid(row=1,column=1)
        self.qualityDD.grid(row=2,column=1)
        self.submitMatch.grid(row=3,column=1)
        self.err = tk.StringVar()
        self.errorLabel = tk.Label(parent,textvariable=self.err)
        self.errorLabel.grid(row=3,column=0)
    def submit(self,event):
        quality = self.qualityName.get()
        sn = self.sn.get()
        pid = self.pid.get()
        if quality != "quality:":
            sql = testStation.licenseToPid_QualityIncluded
            #back = self.insertToDB(sql,sn,quality,pid)
            self.cur.execute(sql,(sn,quality,pid,))
        else:
            sql = testStation.licenseToPid
            #back = self.insertToDB(sql,sn,pid)
            self.cur.execute(sql,(sn,pid,))
        back = self.cur.fetchall()
        self.conn.commit()
        self.err.set(back)
class Banner(tk.Frame):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent)
        l = tk.Label(parent,text='Please insert licenses \n then attach to devices.')
        l.pack()
class testGUI(ttk.Notebook):
    def __init__(self,parent,*args,**kwargs):
        self.donationIDVar = tk.StringVar()
        Banner(parent)
        ttk.Notebook.__init__(self,parent,*args)
        self.tab1 = ttk.Frame()
        self.tab2 = ttk.Frame()
        SNPK(self.tab2,
            ini_section=kwargs['ini_section'])
        AssociatePidAndLicense(self.tab1,
            ini_section=kwargs['ini_section'])
        self.add(self.tab1,text="Attach Licenses to Devices")
        self.add(self.tab2,text="Insert More Licenses")
        #self.add(self.banner)
        self.pack(expand=True,fill='both')
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Test Station")
    app = testGUI(root,ini_section='local_appendage')
    app.mainloop()
