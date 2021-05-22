import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import datetime
import re
from sql import *
from config import DBI

class InsertLog(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args)
        DBI.__init__(self,ini_section = kwargs['ini_section'])
        deviceQualities = self.fetchall(DeviceInfo.getDeviceQualities)
        qtypes =[quality[0] for quality in deviceQualities]
        self.qualityName = tk.StringVar(parent,value="quality:")
        self.qualityDD = tk.OptionMenu(parent,self.qualityName,"quality:",*qtypes)
        self.pid = tk.Entry(parent,width=25)
        self.log = tk.Entry(parent,width=50)
        self.notes = tk.Text(parent,height=4,width=25)
        self.pallet = tk.Entry(parent,width=25)
        self.passBackSelection = tk.Button(parent,
            text='Log',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.pidLabel = tk.Label(parent,text="pid:").grid(column=0,row=2)
        self.logLabel = tk.Label(parent,text="log:").grid(column=0,row=3)
        self.notesLabel = tk.Label(parent,text="notes:").grid(column=0,row=4)
        self.palletlabel = tk.Label(parent,text='location:').grid(column=0,row=0)
        self.qualityDD.grid(column=1,row=1)
        self.passBackSelection.bind('<Button-1>',self.logit)
        self.pid.grid(column=1,row=2)
        self.log.grid(column=1,row=3)
        self.notes.grid(column=1,row=4)
        self.pallet.grid(column=1,row=0)
        self.passBackSelection.grid(column=1,row=5)
        self.outVar = tk.StringVar()
        self.outVarLabel = tk.Label(parent,textvariable=self.outVar)
        self.outVarLabel.grid(column=0,row=5)
    def logit(self,event):
        pid_ = self.pid.get()
        pid = ''
        for item in pid_.split(' '):
            if len(item) > 0:
                pid+=item
        quality = self.qualityName.get()
        log = self.log.get()
        notes = self.notes.get('1.0',tk.END)
        pallet = self.pallet.get()
        back = self.fetchone(testStation.insertLog,quality,False,
                            log,notes,pid,pallet)
        bool = True
        if back == None:
            bool = False
            err = 'log not inserted.'
        else:
            for id in back:
                if id == None:
                    bool = False
                    err = 'pid not registered.'
        if bool is True:
            self.conn.commit()
            self.pid.delete(0,'end')
            self.log.delete(0,'end')
            self.notes.delete('1.0',tk.END)
            err = 'success!'
        self.outVar.set(err)

# class SNPK(tk.Frame,DBI):
#     def __init__(self,parent,*args,**kwargs):
#         tk.Frame.__init__(self,parent)
#         DBI.__init__(self,ini_section=kwargs['ini_section'])
#         self.microsoftSNLabel = tk.Label(parent,text="Microsoft SN:")
#         self.microsoftPKLabel = tk.Label(parent,text="Microsoft PK")
#         self.microsoftSN = tk.Entry(parent,fg='black',bg='white',width=20)
#         self.PKEntry1 = tk.StringVar()
#         self.PKEntry2 = tk.StringVar()
#         self.PKEntry3 = tk.StringVar()
#         self.PKEntry4 = tk.StringVar()
#         self.PKEntry5 = tk.StringVar()
#         self.microsoftPK1 = tk.Entry(parent,fg='black',bg='white',width=6,textvariable=self.PKEntry1)
#         self.microsoftPK2 = tk.Entry(parent,fg='black',bg='white',width=6,textvariable=self.PKEntry2)
#         self.microsoftPK3 = tk.Entry(parent,fg='black',bg='white',width=6,textvariable=self.PKEntry3)
#         self.microsoftPK4 = tk.Entry(parent,fg='black',bg='white',width=6,textvariable=self.PKEntry4)
#         self.microsoftPK5 = tk.Entry(parent,fg='black',bg='white',width=6,textvariable=self.PKEntry5)
#         self.microsoftPK6 = tk.Entry(parent,fg='black',bg='white',width=6)
#
#         self.microsoftSNLabel.grid(column=0,row=0)
#         self.microsoftSN.grid(row=0,column=1)
#         self.microsoftPKLabel.grid(row=1,column=0)
#         self.microsoftPK1.grid(row=1,column=1)
#         self.microsoftPK2.grid(row=1,column=2)
#         self.microsoftPK3.grid(row=1,column=3)
#         self.microsoftPK4.grid(row=1,column=4)
#         self.microsoftPK5.grid(row=1,column=5)
#         self.microsoftPK6.grid(row=1,column=6)
#         self.submitSNPK = tk.Button(parent,
#             text='submit',
#             width = 15,
#             height = 2,
#             bg = "blue",
#             fg = "yellow",
#         )
#         self.submitSNPK.bind('<Button-1>',self.insertSNPK)
#         self.submitSNPK.grid(row=2,column=1)
#         self.err = tk.StringVar(parent)
#         self.errorLabel = tk.Label(parent,textvariable=self.err)
#         self.errorLabel.grid(row=2,column=0)
#
#         self.PKEntry1.trace("w", lambda *args: self.microsoftPK2.focus() if len(self.PKEntry1.get())==5 else False)
#         self.PKEntry2.trace("w", lambda *args: self.microsoftPK3.focus() if len(self.PKEntry2.get())==5 else False)
#         self.PKEntry3.trace("w", lambda *args: self.microsoftPK4.focus() if len(self.PKEntry3.get())==5 else False)
#         self.PKEntry4.trace("w", lambda *args: self.microsoftPK5.focus() if len(self.PKEntry4.get())==5 else False)
#         self.PKEntry5.trace("w", lambda *args: self.microsoftPK6.focus() if len(self.PKEntry5.get())==5 else False)
#     def autoMoveCursor(self,textVar):
#         if len(textVar.get()) == 5:
#             self.microsoftPK2.focus()
#     def insertSNPK(self,event):
#         pk=[]
#         pk.append(self.microsoftPK1.get())
#         pk.append(self.microsoftPK2.get())
#         pk.append(self.microsoftPK3.get())
#         pk.append(self.microsoftPK4.get())
#         pk.append(self.microsoftPK5.get())
#         pk.append(self.microsoftPK6.get())
#         pks = ''
#         for item in pk:
#             if len(item) >0:
#                 pks+=item
#         sn=self.microsoftSN.get()
#         back = self.insertToDB(testStation.insertSNPK,sn,pks)
#         self.err.set(back)
#         self.microsoftPK1.delete(0,'end')
#         self.microsoftPK2.delete(0,'end')
#         self.microsoftPK3.delete(0,'end')
#         self.microsoftPK4.delete(0,'end')
#         self.microsoftPK5.delete(0,'end')
#         self.microsoftPK6.delete(0,'end')
#         self.microsoftSN.delete(0,'end')
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
            self.cur.execute(sql,(sn,quality,pid,))
        else:
            sql = testStation.licenseToPid
            self.cur.execute(sql,(sn,pid,))
        back = self.cur.fetchone()
        bool = True
        if back == None:
            bool = False
            err = 'pid not registered'
        else:
            for id in back:
                if id == None:
                    bool = False
                    err = 'license serial number not registered'
        if bool == True:
            self.conn.commit()
            self.err.set('success!')
            self.pid.delete(0,'end')
            self.sn.delete(0,'end')
        else:
            self.err.set(err)
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
        #self.tab3 = ttk.Frame()
        #SNPK(self.tab3,ini_section=kwargs['ini_section'])
        InsertLog(self.tab2,ini_section=kwargs['ini_section'])
        AssociatePidAndLicense(self.tab1,ini_section=kwargs['ini_section'])
        self.add(self.tab1,text="Attach Licenses to Devices")
        self.add(self.tab2,text="Log Issue")
        #self.add(self.tab3,text="Insert More Licenses")
        #self.add(self.banner)
        self.pack(expand=True,fill='both')
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Test Station")
    app = testGUI(root,ini_section='local_appendage')
    app.mainloop()
