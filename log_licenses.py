import tkinter as tk
from config import DBI
from tkinter import TOP,LEFT,BOTTOM,RIGHT
from dataclasses import dataclass
import psycopg2
NUM_PK_SECTIONS = 5

class PK_Entries(tk.Frame):
    #this object is the product key
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args,**kwargs)
        self.PKEntry1 = tk.StringVar()
        self.PKEntry2 = tk.StringVar()
        self.PKEntry3 = tk.StringVar()
        self.PKEntry4 = tk.StringVar()
        self.PKEntry5 = tk.StringVar()
        self.microsoftPK1 = tk.Entry(self,fg='black',bg='white',width=6,textvariable=self.PKEntry1)
        self.microsoftPK2 = tk.Entry(self,fg='black',bg='white',width=6,textvariable=self.PKEntry2)
        self.microsoftPK3 = tk.Entry(self,fg='black',bg='white',width=6,textvariable=self.PKEntry3)
        self.microsoftPK4 = tk.Entry(self,fg='black',bg='white',width=6,textvariable=self.PKEntry4)
        self.microsoftPK5 = tk.Entry(self,fg='black',bg='white',width=6,textvariable=self.PKEntry5)
        self.PKEntry1.trace("w", lambda *args: self.microsoftPK2.focus() if len(self.PKEntry1.get())==5 else False)
        self.PKEntry2.trace("w", lambda *args: self.microsoftPK3.focus() if len(self.PKEntry2.get())==5 else False)
        self.PKEntry3.trace("w", lambda *args: self.microsoftPK4.focus() if len(self.PKEntry3.get())==5 else False)
        self.PKEntry4.trace("w", lambda *args: self.microsoftPK5.focus() if len(self.PKEntry4.get())==5 else False)
        self.microsoftPK1.pack(side=LEFT)
        self.microsoftPK2.pack(side=LEFT)
        self.microsoftPK3.pack(side=LEFT)
        self.microsoftPK4.pack(side=LEFT)
        self.microsoftPK5.pack(side=LEFT)

class SNPK(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        self.parent=parent
        tk.Frame.__init__(self,parent)
        DBI.__init__(self,ini_section=kwargs['ini_section'])
        getStaff = \
        """
        SELECT name
        FROM staff
        WHERE active=TRUE;
        """
        stafflist = self.fetchall(getStaff)
        snames =[staff[0] for staff in stafflist]
        self.staffName = tk.StringVar(parent,value="staff:")
        tk.OptionMenu(parent,self.staffName,"staff:",*snames).pack()
        self.serialNumber = tk.Entry(parent,fg='black',bg='white',width=20)
        NUM_PK_SECTIONS=6
        tk.Label(parent,text="Microsoft SN:").pack()
        self.serialNumber = tk.Entry(parent,fg='black',bg='white',width=20)
        self.serialNumber.pack()
        tk.Label(parent,text="Microsoft PK").pack()
        self.PK = PK_Entries(parent)
        self.PK.pack()
        self.submitSNPK = tk.Button(parent,
            text='submit',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.submitSNPK.bind('<Button-1>',self.insertSNPK)
        self.submitSNPK.pack()
        self.last_license_id=None
        self.err = tk.StringVar(parent)
        tk.Label(parent,textvariable=self.err).pack()
        self.last_SN = tk.StringVar(parent)
        self.last_PK=tk.StringVar(parent)
        tk.Label(parent,text='last SN:').pack()
        tk.Label(parent,textvariable=self.last_SN).pack()
        tk.Label(parent,text='last PK:').pack()
        tk.Label(parent,textvariable=self.last_PK).pack()
        self.retrieveLast = tk.Button(parent,
            text='retrieve Last',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.retrieveLast.bind('<Button-1>',self.retrieve_last_entry)
        self.retrieveLast.pack()
        self.last_entry_update=False

    def insertSNPK(self,event):
        #this code section (function) runs when the submit button is clicked
        if self.last_entry_update is True:
            pop_up = tk.Toplevel(self.parent)
            UpdateVsSubmission(pop_up)
            self.last_entry_update=False
        staff = self.staffName.get()
        if staff == "staff:":
            self.err.set('please select staff member')
            return self
        pk = str().join([getattr(self.PK,'microsoftPK'+str(i)).get() for i in range(1,NUM_PK_SECTIONS+1)])
        last_pk = str('-').join([getattr(self.PK,'microsoftPK'+str(i)).get() for i in range(1,NUM_PK_SECTIONS+1)])
        sn=self.serialNumber.get()
        insert_snpk = \
        """
        WITH inputs as (SELECT TRIM(LOWER(%s)) as sn, TRIM(LOWER(%s)) as pk, (SELECT s.staff_id FROM staff s where s.name = %s) as s_id)
        INSERT INTO licenses(
            serialNumber,productKey,staff_id)
        VALUES(
            (SELECT sn from inputs),
            (SELECT pk from inputs),
            (SELECT s_id from inputs)
            )
        ON CONFLICT (serialnumber) DO UPDATE
            SET productkey = (select pk from inputs),
            staff_id = (SELECT s_id from inputs)
        RETURNING license_id
        ;
        """
        back = self.insertToDB(insert_snpk,sn,pk,staff)
        try:
            print(back, " license id")
            self.err.set("success! "+ str(back))
            if self.serialNumber.index('end') !=0:
                self.serialNumber.delete(0,'end')
            for i in range(1,NUM_PK_SECTIONS+1):
                if getattr(self.PK,'microsoftPK'+str(i)).index('end') !=0:
                    getattr(self.PK,'microsoftPK'+str(i)).delete(0,'end')
            self.last_SN.set(sn)
            self.last_PK.set(last_pk)
            self.last_license_id=back[0]
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            self.err.set(error)
        finally:
            print(back)
            return self

    def retrieve_last_entry(self,event):
        self._clear_form()
        self.serialNumber.insert(0,self.last_SN.get())
        pk = self.last_PK.get().split('-')
        for i in range(1,NUM_PK_SECTIONS+1):
            getattr(self.PK,'microsoftPK'+str(i)).insert(0,pk[i-1])
        self.last_entry_update=True
    def _clear_form(self):
        if self.serialNumber.index('end') !=0:
            self.serialNumber.delete(0,'end')
        for i in range(1,NUM_PK_SECTIONS+1):
            if getattr(self.PK,'microsoftPK'+str(i)).index('end') !=0:
                getattr(self.PK,'microsoftPK'+str(i)).delete(0,'end')

class UpdateVsSubmission(tk.Frame):
    #this object is the checker of the incorrect submit click. will pop up when submit is clicked after a form repopulation
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent)
        tk.Label(parent,text='It appears you repopulated the form with the last submission').pack()
        tk.Label(parent,text='Note that I proceeded to update the PK if the SN was the same as a previous submission').pack()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Log Licenses")
    app = SNPK(root,ini_section='appendage')
    app.mainloop()
