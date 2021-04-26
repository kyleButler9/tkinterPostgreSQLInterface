from config import DBI;
import tkinter as tk
import datetime
#from demoWriteSheet import *
import wiperSQL as sql
import psycopg2

from reportsAppendage import *

class ProcessedHardDrives(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        self.parent=parent
        tk.Frame.__init__(self,parent,*args)
        parent.geometry("300x500")
        DBI.__init__(self,ini_section = kwargs['ini_section'])
        #tk.Frame.__init__(self,parent,*args)
        self.parent=parent
        self.ini_section = kwargs['ini_section']
        self.devicesTuple = tuple()
        #DBI.__init__(self,ini_section = kwargs['ini_section'])
        stafflist = self.fetchall(sql.DeviceInfo.getStaff)
        snames =[staff[0] for staff in stafflist]
        self.staffName = tk.StringVar(parent,value="staff:")
        self.staffDD = tk.OptionMenu(parent,self.staffName,"staff:",*snames)
        self.hdpidL = tk.Label(parent,text='Hard Drive PID:')
        self.hdpid = tk.Entry(parent,fg='black',bg='white',width=25)
        self.hdLabel = tk.Label(parent,text="Hard Drive Serial:")
        self.hd = tk.Entry(parent,fg='black',bg='white',width=25)
        self.wiperProduct = tk.StringVar(parent,value="Wiped?")
        self.wiperProductMenu = tk.OptionMenu(parent,self.wiperProduct,
                                            "Wiped.","Destroyed.")
        self.finishHDButton = tk.Button(parent,
            text='submit',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.finishHDButton.bind('<Button-1>',self.finishHD)
        self.qcbutton = tk.Button(parent,
            text='Quality Check',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.genReport = tk.Button(parent,
            text='Get Reports',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.qcbutton.bind('<Button-1>',self.manualQC)
        self.genReport.bind('<Button-1>',self.getReport)
        self.err = tk.StringVar()
        self.errorFlag = tk.Label(parent,textvariable=self.err)
        self.staffDD.pack()
        self.hdpidL.pack()
        self.hdpid.pack()
        self.hdLabel.pack()
        self.hd.pack()
        self.wiperProductMenu.pack()
        self.errorFlag.pack()
        self.finishHDButton.pack()
        self.qcbutton.pack()
        self.genReport.pack()
        self.hdpidVal = tk.StringVar(parent)
        self.hdVal = tk.StringVar(parent)
        self.hdpidLog=tk.StringVar(parent)
        self.hdLog = tk.StringVar(parent)
        self.updatehdsnbutton = tk.Button(parent,
            text='Update HD SN',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.updatehdsnbutton.bind('<Button-1>',self.updatehdsn)
        self.getHdsnInfobutton = tk.Button(parent,
            text='Get HD Facts',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.getHdsnInfobutton.bind('<Button-1>',self.getHdsnInfo)
        self.getHdsnInfobutton.pack()
        tk.Label(parent,textvariable=self.hdpidLog).pack()
        tk.Label(parent,textvariable=self.hdLog).pack()
        self.updatehdsnbutton.pack()
    def getHdsnInfo(self,event):
        pop_up = tk.Toplevel(self.parent)
        kwargs = dict()
        kwargs['ini_section']=self.ini_section
        if self.hdpid.index('end') != 0:
            kwargs['hdpid']=self.hdpid.get()
        else:
            kwargs['hdsn']=self.hd.get()
        HdFacts(pop_up,**kwargs)

    def updatehdsn(self,event):
        updatehdSQL = \
        """
        UPDATE harddrives
            set devicehdsn = %s
            WHERE {}
            RETURNING device_id;
        """
        if self.hdpid.index("end") != 0:
            rowIdentifier = 'hdpid = %s' % (self.hdpid.get(),)
        else:
            rowIdentifier = 'hdpid = %s' % (self.hdpidVal.get(),)
        updatehdSQL.format(rowIdentifier)
        self.fetchone(updatehdSQL,self.hd.get())
        self.hd.delete(0,'end')
        self.hdpid.delete(0,'end')
    def finishHD(self,event):
        name = self.staffName.get()
        if name == "staff:":
            self.err.set('select a staff from the drop down.')
            return self
        hdStatusUpdate = \
        """
        with logHdStatus as(
        UPDATE harddrives
        set {},
            wipeDate = %s,
            staff_id = (Select staff_id from staff s where s.name = %s)
        WHERE {}
        RETURNING hd_id,hdsn
        )
        UPDATE donations
        SET numwiped = (CASE WHEN numwiped is not null THEN (numwiped + 1) ELSE 0 END)
        WHERE donation_id = (
                            SELECT donation_id
                            FROM processing
                            WHERE hd_id = (SELECT hd_id FROM logHdStatus)
                            )
        RETURNING numwiped,(select hdsn from logHdStatus),(select hd_id from logHdStatus),donation_id;
        """
        wiped = self.wiperProduct.get()
        if wiped == "Wiped.":
            wipedOrDestroyed="sanitized = TRUE, destroyed = FALSE"
        elif wiped == "Destroyed.":
            wipedOrDestroyed="sanitized = FALSE, destroyed = TRUE"
        if self.hdpid.index("end") != 0:
            hardDriveIdentifier = "hdpid = LOWER('%s')" % (self.hdpid.get(),)
        else:
            hardDriveIdentifier = "devicehdsn = LOWER('%s')" % (self.hd.get(),)
        hdStatusUpdate = hdStatusUpdate.format(wipedOrDestroyed,hardDriveIdentifier)
        try:
            now = datetime.datetime.now()
            out = self.fetchone(hdStatusUpdate,now,name)
            self.conn.commit()
            if len(out) == 0:
                self.err.set('Error! Error! provided '+ hardDriveIdentifier +' isn\'t in system!')
                pop_up = tk.Toplevel(self.parent)
                pop_up.title('Deeper Hard Drive Search')
                deeperHardDriveSearch(pop_up,ini_section=self.ini_section,
                                     hdserial=hd,name=name,wipedVar=wiped,sqlupdate=finalizeHDStatus)
            else:
                print(out)
                if out[0] == 0:
                    self.err.set('First HD for Lot. Please do Quality Check.')
                    self.qualityCheck(name,out[1],wiped,hd_id=out[2],donation_id=out[3])
                else:
                    self.err.set('success! Its been {} drives sence QC'.format(out[0]-1))
                self.hdpidVal = self.hdpid.get()
                self.hdVal=out[1]
                self.hdpidLog.set('HD PID: %s' % (self.hdpidVal,))
                self.hdLog.set('HD SN: %s' % (self.hdVal,))
                self.hd.delete(0,'end')
                self.hdpid.delete(0,'end')
        except (Exception, psycopg2.DatabaseError) as error:
            self.err.set(error)
        finally:
            return self
    def getReport(self,event):
        pop_up = tk.Toplevel(self.parent)
        pop_up.title('Generate CRM Report')
        Report(pop_up,ini_section=self.ini_section)
    def manualQC(self,event):
        self.qualityCheck(self.staffName.get(),self.hd.get(),self.wiperProduct.get())
    def qualityCheck(self,name,hd,status,**kwargs):
        pop_up = tk.Toplevel(self.parent)
        pop_up.title('Quality Check')
        if 'donation_id' in kwargs:
            qc(pop_up,name=name,hdserial=hd,status=status,
                ini_section=self.ini_section,
                donation_id = kwargs['donation_id'],
                hd_id = kwargs['hd_id'])
        else:
            qc(pop_up,name=name,hdserial=hd,status=status,
                ini_section=self.ini_section,
                hd_id=kwargs['hd_id'])
class deeperHardDriveSearch(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args)
        self.parent=parent
        DBI.__init__(self,ini_section = kwargs['ini_section'])
        self.sqlUpdateStatement=kwargs['sqlupdate']
        self.username = kwargs['name']
        self.hd=tk.StringVar(parent)
        self.hd.set(kwargs['hdserial'])
        self.stringEntry = tk.Entry(parent,width=20,textvariable=self.hd)
        hds = self.fetchall(self.getQuery(self.hd.get()),self.hd.get())
        hds =[hd[0] for hd in hds]
        self.hdvar = tk.StringVar(parent,value="select a hd:")
        self.hdDD = tk.OptionMenu(parent,self.hdvar,"select a hd:",*hds)
        self.searchButton = tk.Button(parent,
            text='Search',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.searchButton.bind('<Button-1>',self.search)
        self.stringEntry.pack()
        self.searchButton.pack()
        self.hdDD.pack()
        self.updateButton = tk.Button(parent,
            text='commit it',
            width = 25,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        tk.Label(parent,text=kwargs['wipedVar']).pack()
        self.updateButton.bind('<Button-1>',self.runUpdate)
        self.updateButton.pack()
        # self.tv = tk.ttk.Treeview(self,columns=(1,),show='headings',height=8)
        # self.tv.heading(1,text='HDSN')
        # self.tv.pack()
        # sb = tk.Scrollbar(self, orient=tk.VERTICAL)
        # sb.pack(side=tk.RIGHT, fill=tk.Y)
        # self.tv.config(yscrollcommand=sb.set)
        # sb.config(command=self.tv.yview)
        # style = tk.ttk.Style()
        # style.theme_use("default")
        # style.map("Treeview")

    def getQuery(self,hd):
        if len(hd) < 6:
            return """
            with userinput as (SELECT %s as value)
            SELECT devicehdsn
            FROM harddrives
            WHERE destroyed = FALSE
            AND sanitized = FALSE
            AND hdsn ~* (SELECT SUBSTRING(
                (SELECT value from userinput),2,
                LENGTH((SELECT value from userinput))-2
            ))
            LIMIT 10;
            """
        else:
            return """
            with userinput as (SELECT %s as value)
            SELECT hdsn
            FROM harddrives
            WHERE destroyed = FALSE
            AND sanitized = FALSE
            AND hdsn ~* (SELECT SUBSTRING(
                (SELECT value from userinput),3,
                LENGTH((SELECT value from userinput))-3
            ))
            LIMIT 10;
            """
    def search(self,event):
        print('here2')
        hds =self.fetchall(self.getQuery(self.hd.get()),self.hd.get())
        self.hdDD['menu'].delete(0,'end')
        filtered_hds = self.fetchall(self.getQuery(self.hd.get()),self.hd.get())
        for hd in filtered_hds:
            self.hdDD['menu'].add_command(label=hd[0],
                command=tk._setit(self.hdvar,hd[0]))
        return self
    def runUpdate(self,event):
        hd = self.hdvar.get()
        if hd == "select a hd:":
            self.err.set('please select a value from drop down.')
        else:
            now = datetime.datetime.now()
            self.fetchall(self.sqlUpdateStatement,(now,self.username,hd))

class HdFacts(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args)
        self.parent=parent
        DBI.__init__(self,ini_section = kwargs['ini_section'])
        hdpidL=tk.Label(parent,text='HD PID:')
        self.hdpid=tk.Entry(parent,width=25)
        devicehdsnL=tk.Label(parent,text='HD SN:')
        self.devicehdsn=tk.Entry(parent,width=25)
        self.lotNumber=tk.StringVar(parent)
        self.donorName=tk.StringVar(parent)
        self.name=tk.StringVar(parent)
        self.entryDate=tk.StringVar(parent)
        self.wipeDate=tk.StringVar(parent)
        self.devicesn=tk.StringVar(parent)
        lotNumberL=tk.Label(parent,textvariable=self.lotNumber)
        donorNameL=tk.Label(parent,textvariable=self.donorName)
        nameL=tk.Label(parent,textvariable=self.name)
        entryDateL=tk.Label(parent,textvariable=self.entryDate)
        wipedateL=tk.Label(parent,textvariable=self.wipeDate)
        devicesnL=tk.Label(parent,textvariable=self.devicesn)
        self.SqlGetHdInfo = \
        """
        SELECT don.lotnumber,d.name,s.name,
                p.entrydate,hd.wipedate,
                p.devicesn,hd.hdsn,hd.hdpid
        FROM processing p
        INNER JOIN harddrives hd USING (hd_id)
        INNER JOIN donations don USING (donation_id)
        INNER JOIN donors d USING (donor_id)
        INNER JOIN staff s ON s.staff_id=hd.staff_id
        WHERE hd.{};
        """
        if 'hdpid' in kwargs:
            rowIdentifier="hdpid = LOWER('%s')" % (kwargs['hdpid'],)
            self.hdpid.insert(0,kwargs['hdpid'])
        else:
            rowIdentifier="hdsn = LOWER('%s')" % (kwargs['hdsn'],)
            self.hdsn.insert(0,kwargs['hdsn'])
        hdInfo=self.fetchone(self.SqlGetHdInfo.format(rowIdentifier))
        self.updateFrame(hdInfo)
        hdpidL.pack()
        self.hdpid.pack()
        devicehdsnL.pack()
        self.devicehdsn.pack()
        lotNumberL.pack()
        donorNameL.pack()
        nameL.pack()
        entryDateL.pack()
        wipedateL.pack()
        devicesnL.pack()
        getInfoB = tk.Button(parent,
            text='Get Info',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        getInfoB.bind('<Button-1>',self.getNewInfo)
        getInfoB.pack()
        self.err=tk.StringVar(parent)
        tk.Label(parent,textvariable=self.err).pack()
    def getNewInfo(self,event):
        if self.hdpid.get() != self.hdpidLog:
            rowIdentifier='hdpid = %s' % (self.hdpid.get(),)
        elif self.devicehdsn.get() != self.hdsnLog:
            rowIdentifier='devicehdsn = %s' % (self.devicehdsn.get(),)
        else:
            self.err.set('please enter a new HD PID or HD SN.')
            return self
        try:
            hdInfo=self.fetchone(self.SqlGetHdInfo.format(rowIdentifier))
            self.updateFrame(hdInfo)
        except (Exception, psycopg2.DatabaseError) as error:
            self.err.set(error)
        finally:
            return self
    def updateFrame(self,hdInfo):
        try:
            self.lotNumber.set('lotnumber: '+str(hdInfo[0]))
            self.donorName.set('donorName: '+str(hdInfo[1]))
            self.name.set('Wiper name: '+str(hdInfo[2]))
            self.entryDate.set('entryDate: '+str(hdInfo[3]))
            self.wipedate.set('wipedate: '+str(hdInfo[4]))
            self.devicesn.set('devicesn: '+str(hdInfo[5]))

            self.devicehdsn.delete(0,'end')
            self.devicehdpid.delete(0,'end')
            self.devicehdsn.insert(0,str(hdInfo[6]))
            self.hdpid.insert(0,str(hdInfo[7]))
            self.hdsnLog = self.devicehdsn.get()
            self.hdpidLog=self.hdpid.get()
        except:
            self.err.set('incompatable values for updating pane.')
        finally:
            return self

class qc(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args)
        self.hd = kwargs['hdserial']
        if "hd_id" in kwargs:
            self.hd_id = kwargs['hd_id']
        else:
            hd_idSQL = \
            """
            SELECT hd_id
            FROM harddrives
            WHERE hdsn = LOWER(%s);
            """
            self.hd_id = self.fetchone(hd_idSQL,self.hd)[0]
        self.hdstatus=kwargs['status']
        DBI.__init__(self,ini_section = kwargs['ini_section'])
        if 'donation_id' in kwargs:
            self.donation_id = kwargs['donation_id']
        else:
            donationIDFromHDSN= \
            """
            SELECT donation_id
            FROM processing
            INNER JOIN harddrives hd USING (hd_id)
            WHERE hd.hdsn = lower(%s);
            """
            self.donation_id = self.fetchone(donationIDFromHDSN,self.hd)[0]
        stafflist = self.fetchall(sql.DeviceInfo.getStaffqc,kwargs['name'])
        snames =[staff[0] for staff in stafflist]
        self.staffName = tk.StringVar(parent,value="staff:")
        self.staffDD = tk.OptionMenu(parent,self.staffName,"staff:",*snames)
        instructions=tk.Label(parent,text='please get another staff member to perform quality check\nfor hard drive:').pack()
        hdlabel = tk.Label(parent,text =self.hd).pack()
        self.wiperProduct = tk.Label(parent,text="HD is " + kwargs['status']).pack()
        self.staffDD.pack()
        logQC = tk.Button(parent,
            text='log QC',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        logQC.bind('<Button-1>',self.logQC)
        logQC.pack()
        self.err = tk.StringVar(parent)
        tk.Label(parent,textvariable=self.err).pack()
    def logQC(self,event):
        now = datetime.datetime.now()
        name = self.staffName.get()
        if name != "staff:":
            try:
                qualityControlLog = \
                """
                INSERT INTO qualitycontrol(hd_id,qcDate,donation_id,staff_id)
                VALUES(%s,%s,%s,
                    (SELECT s.staff_id from staff s
                    WHERE s.name = %s));
                Update donations
                set numwiped = 1
                WHERE donation_id = %s;
                """
                out=self.insertToDB(qualityControlLog,self.hd_id,now,self.donation_id,name,self.donation_id)
                self.err.set(out)
            except (Exception, psycopg2.DatabaseError) as error:
                self.err.set(error)
            finally:
                pass
        else:
            self.err.set('select a staff from the drop down.')

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Drive register Station")
    app = ProcessedHardDrives(root,ini_section='appendage')
    app.mainloop()
