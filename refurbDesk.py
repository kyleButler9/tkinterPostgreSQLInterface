import tkinter as tk
from config import *
class Banner(tk.Frame):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent)
        self.headermessage = tk.Entry(parent,text='Log new issue \n or retrieve a log')
class InsertLog(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args)
        DBI.__init__(self,ini_section = kwargs['ini_section'])
        self.pid = tk.Entry(parent,width=25)
        self.qual = tk.Entry(parent,width=25)
        self.log = tk.Entry(parent,width=100)
        self.notes = tk.Text(parent)
        self.passBackSelection = tk.Button(parent,
            text='Log',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.pidLabel = tk.Label(parent,text="pid:").grid(column=0,row=0)
        self.qualLabel = tk.Label(parent,text="Quality:").grid(column=0,row=1)
        self.logLabel = tk.Label(parent,text="log:").grid(column=0,row=2)
        self.notesLabel = tk.Label(parent,text="notes:").grid(column=0,row=3)
        self.passBackSelection.bind('<Button-1>',self.logit)
        self.pid.grid(column=1,row=0)
        self.qual.grid(column=1,row=1)
        self.log.grid(column=1,row=2)
        self.notes.grid(column=1,row=3)
        self.passBackSelection.grid(column=1,row=4)
    def logit(self,event):
        pid = self.pid.get()
        quality = self.qual.get()
        log = self.log.get()
        notes = self.notes.get()
        self.insertToDB(refurb.insertLog,quality,False,log,notes,pid)
        self.pid.delete(0,'end')
        self.log.delete(0,'end')
        self.notes.delete(0,'end')
class refurbDeskGUI(ttk.Notebook):
    def __init__(self,parent,*args,**kwargs):
        self.donationIDVar = tk.StringVar()
        self.donorIdentifier = Banner(parent)
        ttk.Notebook.__init__(self,parent,*args)
        self.tab1 = ttk.Frame()
        self.tab2 = ttk.Frame()
        InsertLog(self.tab2,ini_section=kwargs['ini_section'])
