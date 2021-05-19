import tkinter as tk
from config import DBI
from tkinter import TOP,LEFT,BOTTOM,RIGHT
from dataclasses import dataclass
import psycopg2
NUM_PK_SECTIONS = 6

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
        self.microsoftPK6 = tk.Entry(self,fg='black',bg='white',width=6)
        self.PKEntry1.trace("w", lambda *args: self.microsoftPK2.focus() if len(self.PKEntry1.get())==5 else False)
        self.PKEntry2.trace("w", lambda *args: self.microsoftPK3.focus() if len(self.PKEntry2.get())==5 else False)
        self.PKEntry3.trace("w", lambda *args: self.microsoftPK4.focus() if len(self.PKEntry3.get())==5 else False)
        self.PKEntry4.trace("w", lambda *args: self.microsoftPK5.focus() if len(self.PKEntry4.get())==5 else False)
        self.PKEntry5.trace("w", lambda *args: self.microsoftPK6.focus() if len(self.PKEntry5.get())==5 else False)
        self.microsoftPK1.pack(side=LEFT)
        self.microsoftPK2.pack(side=LEFT)
        self.microsoftPK3.pack(side=LEFT)
        self.microsoftPK4.pack(side=LEFT)
        self.microsoftPK5.pack(side=LEFT)
        self.microsoftPK6.pack(side=LEFT)

class SNPK(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
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
        self.update_PKB = tk.Button(parent,
            text='Update PK Via SN',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.update_PKB.bind('<Button-1>',self.update_PK)
        self.update_PKB.pack()
        self.last_entry_update=False

    def insertSNPK(self,event):
        #this code section (function) runs when the submit button is clicked
        #the next few lines of code check for an accidental clicking of the submit button
        cont=True
        if self.last_entry_update is True:
            pop_up = tk.Toplevel()
            UpdateVsSubmission(pop_up,cont=cont)
            self.last_entry_update=False
        # if cont == :
        #     self.update_SN()
        #     return self
        if cont ==False:
            self.update_PK()
            return self
        staff = self.staffName.get()
        if staff == "staff:":
            self.err.set('please select staff member')
            return self
        pk = str().join([getattr(self.PK,'microsoftPK'+str(i)).get() for i in range(1,NUM_PK_SECTIONS+1)])
        last_pk = str('-').join([getattr(self.PK,'microsoftPK'+str(i)).get() for i in range(1,NUM_PK_SECTIONS+1)])
        sn=self.serialNumber.get()
        insert_snpk = \
        """
        WITH inputs as (SELECT TRIM(LOWER(%s)) as sn, TRIM(LOWER(%s)) as pk, %s as s_id)
        INSERT INTO licenses(
            serialNumber,productKey,staff_id)
        VALUES(
            (SELECT sn from inputs),
            (SELECT pk from inputs),
        (SELECT s.staff_id FROM staff s where s.name =
            (SELECT s_id from inputs))
            )
        ON CONFLICT (serialnumber) DO UPDATE
            SET productkey = (select pk from inputs)
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

    def update_PK(self,event):
        staff = self.staffName.get()
        if staff == "staff:":
            self.err.set('please select staff member')
            return self
        pk = str().join([getattr(self.PK,'microsoftPK'+str(i)).get() for i in range(1,NUM_PK_SECTIONS+1)])
        last_pk = str('-').join([getattr(self.PK,'microsoftPK'+str(i)).get() for i in range(1,NUM_PK_SECTIONS+1)])
        sn=self.serialNumber.get()
        sql = \
        """
        UPDATE licenses
        SET productKey=TRIM(LOWER(%s)),
            staff_id = (select staff_id from staff where staff.name=%s)
        WHERE serialnumber = TRIM(LOWER(%s));
        """
        try:
            out = self.insertToDB(sql,pk,staff,sn)
            self.err.set(out)
            self._clear_form()
        except (Exception, psycopg2.DatabaseError) as error:
            self.err.set(error)
        finally:
            return self

class UpdateVsSubmission(tk.Frame):
    #this object is the checker of the incorrect submit click. will pop up when submit is clicked after a form repopulation
    def __init__(self,parent,*args,**kwargs):
        self.parent=parent
        self.cont=kwargs['cont']
        tk.Frame.__init__(self,parent)
        tk.Label(parent,text='It appears you repopulated the form with the last submission').pack()
        tk.Label(parent,text='Are you sure you don\'t want to click one of the update buttons below to update instead of submitting a new entry?').pack()
        self.updatePK = tk.Button(parent,
            text='Update PK Via SN',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow"
        )
        self.updatePK.bind('<Button-1>',self.updatePK_)
        self.updatePK.pack()
        self.submitB = tk.Button(parent,
            text='Try Submit',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow"
        )
        self.submitB.bind('<Button-1>',self.submit_)
        self.submitB.pack()
    def submit_(self,event):
        self.cont=True
        self.parent.destroy()
    def updatePK_(self,event):
        self.cont=False
        self.parent.destroy()



if __name__ == "__main__":
    root = tk.Tk()
    root.title("Log Licenses")
    app = SNPK(root,ini_section='appendage')
    app.mainloop()
