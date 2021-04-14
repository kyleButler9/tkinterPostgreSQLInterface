from config import DBI;
import tkinter as tk
import datetime
from demoWriteSheet import *
import wiperSQL as sql
from extractionAppendage import *
import psycopg2
from pathlib import Path
from os.path import join
from multiprocessing import Process
# class GenerateReport(tk.Frame,DBI):
#     def __init__(self,parent,*args,**kwargs):
#         tk.Frame.__init__(self,parent,*args)
#         DBI.__init__(self,ini_section = kwargs['ini_section'])
#         self.donationID = kwargs['donationID']
#         if 'sheetID' not in kwargs:
#             self.sheetIDLabel = tk.Label(parent,text='Google Sheet ID:').pack()
#             self.sheetID = tk.Entry(parent,fg='black',bg='white',width=40)
#             self.sheetID.pack()
#         self.getReportButton = tk.Button(parent,
#             text='Generate New Report',
#             width = 15,
#             height = 2,
#             bg = "blue",
#             fg = "yellow",
#         )
#         self.getReportButton.bind('<Button-1>',self.createTextFile)
#         self.getReportButton.pack()
#     def writeSheet(self,event):
#         donationID = self.donationID.get()
#         print(donationID)
#         print('\n\n\n'
#         )
#         donationInfo=self.fetchone(sql.Report.donationInfo,donationID)
#         report = [
#             ['Company Name: {}'.format(donationInfo[0])],
#             ['Date Received: {} '.format(donationInfo[1].strftime('%m/%d/%Y'))],
#             ['Lot Number: {}'.format(donationInfo[2])],
#             ['']
#         ]
#         cols = 'Drive	Item Type	Item Serial	HD Serial Number	Asset Tag	Destroyed	Data Sanitized	Staff	Entry Date'
#         report.append(cols.split('	'))
#         devices = self.fetchall(sql.Report.deviceInfo,donationID)
#         print(devices)
#         print('\n\n\n')
#         drive = [1]
#         for device in devices:
#             dlist = list(device)
#             try:
#                 dlist[-1] = dlist[-1].strftime("%m/%d/%Y %H:%M")
#             except:
#                 pass
#             finally:
#                 report.append(drive + dlist)
#                 drive[0]+=1
#         sid = self.sheetID.get()
#         import csv
#         with open('report.csv', 'w', newline='') as f:
#             writer = csv.writer(f)
#             writer.writerows(report)
#         print(report)
#         write_to_sheet(sid,report)
#     def createTextFile(self,event):
#         report = list()
#         cols = 'Drive	Item Type	Item Serial	HD Serial Number	Asset Tag	Destroyed	Data Sanitized	Staff	Entry Date'
#         report.append(cols.split('\t'))
#         devices = self.fetchall(sql.Report.deviceInfo,donationID)
#     def devicesToTabDelimitedFile(self,donationID):
#         devices = self.fetchall(sql.Report.deviceInfo,donationID)
#         drive = [1]
#         report = []
#         for device in devices:
#             dlist = list(device)
#             try:
#                 dlist[-1] = dlist[-1].strftime("%m/%d/%Y %H:%M")
#             except:
#                 pass
#             finally:
#                 report.append(tuple(drive + dlist))
#                 drive[0]+=1
#         return tuple(report)
class ProcessedHardDrives(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        self.parent=parent
        tk.Frame.__init__(self,parent,*args)
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
        self.hdLabel = tk.Label(parent,text="Hard Drive Serial:")
        self.hd = tk.Entry(parent,fg='black',bg='white',width=15)
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
        self.hdLabel.pack()
        self.hd.pack()
        self.wiperProductMenu.pack()
        self.errorFlag.pack()
        self.finishHDButton.pack()
        self.qcbutton.pack()
        self.genReport.pack()
    def finishHD(self,event):
        now = datetime.datetime.now()
        wiped = self.wiperProduct.get()
        name = self.staffName.get()
        hd = self.hd.get()
        if name != "staff:":
            wipedOrDestroyedUpdate = \
            """
            with w as(
            UPDATE processing
            set {},
                wipeDate = %s,
                staff_id = (Select staff_id from staff s where s.name = %s)
            WHERE deviceHDSN = LOWER(%s)
            RETURNING donation_id as d_id
            )
            UPDATE donations
            SET numwiped = numwiped + 1
            WHERE donation_id = (select d_id from w)
            RETURNING numwiped;
            """
            if wiped == "Wiped.":
                finalizeHDStatus = wipedOrDestroyedUpdate.format("sanitized = TRUE, destroyed = FALSE")
            elif wiped == "Destroyed.":
                finalizeHDStatus =wipedOrDestroyedUpdate.format("sanitized = FALSE, destroyed = TRUE")
            try:
                #self.cur.execute(finalizeHDStatus,(now,name,hd))
                #self.conn.commit()
                out = self.fetchall(finalizeHDStatus,now,name,hd)
                if len(out) == 0:
                    self.err.set('Error! Error! provided HD SN '+hd +' isn\'t in system!')
                    pop_up = tk.Toplevel(self.parent)
                    pop_up.title('Deeper Hard Drive Search')
                    deeperHardDriveSearch(pop_up,ini_section=self.ini_section,
                                         hdserial=hd,name=name,wipedVar=wiped,sqlupdate=finalizeHDStatus)
                else:
                    self.err.set('success!')
                    if out[0][0] % 50 == 1:
                        self.qualityCheck(name,hd,wiped)
                self.hd.delete(0,'end')
            except (Exception, psycopg2.DatabaseError) as error:
                self.err.set(error)
            finally:
                pass
        else:
            self.err.set('select a staff from the drop down.')
    def getReport(self,event):
        pop_up = tk.Toplevel(self.parent)
        pop_up.title('Generate CRM Report')
        Report(pop_up,ini_section=self.ini_section)
    def manualQC(self,event):
        self.qualityCheck(self.staffName.get(),self.hd.get(),self.wiperProduct.get())
    def qualityCheck(self,name,hd,status):
        pop_up = tk.Toplevel(self.parent)
        pop_up.title('Quality Check')
        qc(pop_up,name=name,hdserial=hd,status=status,
            ini_section=self.ini_section)
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
        print('here2')
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
            FROM processing
            WHERE destroyed = FALSE
            AND sanitized = FALSE
            AND devicehdsn ~* (SELECT SUBSTRING(
                (SELECT value from userinput),2,
                LENGTH((SELECT value from userinput))-2
            ))
            LIMIT 10;
            """
        else:
            return """
            with userinput as (SELECT %s as value)
            SELECT devicehdsn
            FROM processing
            WHERE destroyed = FALSE
            AND sanitized = FALSE
            AND devicehdsn ~* (SELECT SUBSTRING(
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



class qc(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args)
        self.hd = kwargs['hdserial']
        self.hdstatus=kwargs['status']
        DBI.__init__(self,ini_section = kwargs['ini_section'])
        if 'donationID' in kwargs:
            self.donation_id = kwargs['donationID']
        else:
            self.donation_id = self.fetchone(sql.DeviceInfo.donationIDFromHDSN,self.hd)[0]
        stafflist = self.fetchall(sql.DeviceInfo.getStaffqc,kwargs['name'])
        snames =[staff[0] for staff in stafflist]
        self.staffName = tk.StringVar(parent,value="staff:")
        self.staffDD = tk.OptionMenu(parent,self.staffName,"staff:",*snames)
        instructions=tk.Label(parent,text='please get another staff member to perform quality check\nfor hard drive:').pack()
        hdlabel = tk.Label(parent,text =self.hd).pack()
        self.wiperProduct = tk.StringVar(parent,value="Wiped?")
        self.wiperProductMenu = tk.OptionMenu(parent,self.wiperProduct,
                                            "Wiped.","Destroyed.")
        self.wiperProductMenu.pack()
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
        self.err = tk.StringVar()
        tk.Label(parent,textvariable=self.err).pack()
    def logQC(self,event):
        now = datetime.datetime.now()
        name = self.staffName.get()
        if name != "staff:":
            try:
                self.cur.execute(sql.Report.qualityControlLog,
                    (self.hd,now,self.donation_id,name,self.donation_id))
                self.conn.commit()
                self.err.set('success!')
            except (Exception, psycopg2.DatabaseError) as error:
                self.err.set(error)
            finally:
                pass
        else:
            self.err.set('select a staff from the drop down.')
class InvestigateLots(DonationBanner,DBI):
    def __init__(self,parent,*args,**kwargs):
        #DonationBanner.__init__(self,parent,ini_section=kwargs['ini_section'])
        self.donationIDVar=kwargs['donationID']
        DBI.__init__(self,ini_section = kwargs['ini_section'])
        self.getInfoButton = tk.Button(parent,
            text='Get Info',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.getInfoButton.bind('<Button-1>',self.getInfo)
        self.num_HDSN=tk.StringVar(parent,value="Hard Drive Count: ")
        self.num_SN=tk.StringVar(parent,value="Device Count: ")
        self.how_many_HDs_left=tk.StringVar(parent,value="Count Remaining: ")
        tk.Label(parent,textvariable=self.num_HDSN).pack()
        tk.Label(parent,textvariable=self.num_SN).pack()
        tk.Label(parent,textvariable=self.how_many_HDs_left).pack()
        self.err = tk.StringVar(parent)
        tk.Label(parent,textvariable=self.err).pack()
        self.getInfo(None)

    def getInfo(self,event):
        donationID=self.donationIDVar.get()
        if len(donationID) == 0:
            self.err.set('Please select a donation.')
            return self
        getInfo = \
        """
        SELECT count(DISTINCT devicehdsn),count(DISTINCT devicesn)
        FROM processing
        WHERE donation_id = %s;
        """ % (donationID)
        res = self.fetchone(getInfo)
        print(res)
        msg=dict()
        self.num_HDSN.set("Hard Drive Count: " + str(res[0]))
        self.num_SN.set("Device Count: "+str(res[1]))
        queryPartiallyCompletedLot = \
        """
        SELECT count(devicehdsn) as howmanyleft
        from processing
        inner join donations USING (donation_id)
        where destroyed=FALSE and sanitized=FALSE
        and donation_id = %s
        group by donation_id;
        """ % (donationID,)
        hmlRes=self.fetchone(queryPartiallyCompletedLot)
        if len(hmlRes) !=0:
            self.how_many_HDs_left.set("Count Remaining: "+str(hmlRes[0]))
        else:
            self.how_many_HDs_left.set("Count Remaining: "+str(0))


class Report(DonationBanner,DBI):
    def __init__(self,parent,*args,**kwargs):
        self.ini_section = kwargs['ini_section']
        self.parent=parent
        DBI.__init__(self,ini_section = kwargs['ini_section'])

        queryCompletedLots = \
        """
        with completedlots as
        (select avg(donors.donor_id) as donor_id, donation_id,
        bool_and(case when destroyed = TRUE or sanitized=TRUE THEN TRUE ELSE FALSE END)
        from processing inner join donations using (donation_id)
        inner join donors USING (donor_id)
        where devicehdsn is not null and reported=FALSE
        group by donation_id
        having bool_and(case when destroyed = TRUE or sanitized=TRUE THEN TRUE ELSE FALSE END) = TRUE)

        select donors.name, donations.lotnumber
        from completedlots
        inner join donors on completedlots.donor_id = donors.donor_id
        inner join donations on completedlots.donation_id=donations.donation_id
        order by lotnumber;
        """
        tk.Label(parent,text='Completed Lots:').pack()
        completedLots = self.fetchall(queryCompletedLots)
        clots =list()
        for lot in completedLots:
            lotdesc = str()
            for lotDescriptor in lot:
                lotdesc+=str(lotDescriptor)
                if lotDescriptor !=lot[-1]:
                    lotdesc += ' | '
            clots.append(lotdesc)

        self.lotvar = tk.StringVar(parent,value="donor name | lotnumber")
        self.clotsDD = tk.OptionMenu(parent,self.lotvar,"donor name | lotnumber",*clots)
        self.clotsDD.pack()

        queryPartiallyCompletedLots = \
        """
        with PartiallyCompletedLots as (select donation_id, count(devicehdsn) as howmanyleft
        from processing
        inner join donations USING (donation_id)
        where destroyed=FALSE and sanitized=FALSE and reported=FALSE
        group by donation_id
        having count(devicehdsn) < %s
        and count(devicehdsn)>0)

        select donors.name,lotnumber, howmanyleft
        from PartiallyCompletedLots
        inner join donations using (donation_id)
        inner join donors using (donor_id)
        order by lotnumber;
        """
        tk.Label(parent,text='Partially Completed Lots with Maximum Number left: ').pack()
        self.maximum = tk.StringVar(parent,value='15')
        maxEntry=tk.Entry(parent,width=5,textvariable=self.maximum)
        maxEntry.pack()
        partialLots = self.fetchall(queryPartiallyCompletedLots % (self.maximum.get(),))
        pclots =list()
        for lot in partialLots:
            lotdesc = str()
            for lotDescriptor in lot:
                lotdesc+=str(lotDescriptor)
                if lotDescriptor !=lot[-1]:
                    lotdesc += ' | '
            pclots.append(lotdesc)

        self.plotvar = tk.StringVar(parent,value="donor name | lotnumber | how many left")
        self.pclotsDD = tk.OptionMenu(parent,self.plotvar,"donor name | lotnumber | how many left",*pclots)
        self.pclotsDD.pack()

        DonationBanner.__init__(self,parent,ini_section=kwargs['ini_section'])
        self.lookIntoLot = tk.Button(parent,
            text='Look into selected lot',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.lookIntoLot.bind('<Button-1>',self.lookIntoLots)
        self.lookIntoLot.pack()
        self.genReport = tk.Button(parent,
            text='Get Receipts',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.genReport.bind('<Button-1>',self.getTextFiles)
        self.genReport.pack()

        self.devicesTuple = tuple()
        self.err = tk.StringVar()
        tk.Label(parent,textvariable=self.err).pack()
    def getTextFiles(self,event):
        self.donationID=self.donationIDVar.get()
        if len(self.donationID) == 0:
            self.err.set('Please select a donation.')
            return self
        self.donationID=self.donationIDVar.get()
        self.donationInfo=self.fetchone(sql.Report.donationInfo,self.donationID)
        devices = self.devicesToTuple()
        qcdevices=self.qcDevicesToTuple()
        devicesFilePath=self.TupleToTabDelimitedReport('',devices)
        qcFilePath=self.TupleToTabDelimitedReport('QC',qcdevices)
        procs = []
        for outfile in [devicesFilePath,qcFilePath]:
            proc = Process(target=os.system,args=('notepad {}'.format(outfile),))
            procs.append(proc)
            proc.start()
        for proc in procs:
            proc.join()
        self.err.set('Files successfully saved in your Downloads folder.')
        return self
    def devicesToTuple(self):
        deviceInfo = \
        """
        SELECT dts.deviceType, p.deviceSN, COALESCE(p.devicehdsn,''),
            p.assetTag, p.destroyed, p.sanitized, s.nameabbrev,
            CASE WHEN p.deviceHDSN is NULL THEN TO_CHAR(p.entryDate,'MM/DD/YYYY HH24:MI')
            ELSE TO_CHAR(p.wipeDate,'MM/DD/YYYY HH24:MI')
            END AS date
        FROM processing p
        INNER JOIN deviceTypes dts on dts.type_id = p.deviceType_id
        INNER JOIN staff s on s.staff_id = p.staff_id
        WHERE p.donation_id = %s
        ORDER BY p.entryDate;
        """
        print(deviceInfo % (self.donationID,))
        devices = self.fetchall(deviceInfo,self.donationID)
        cols = 'Drive	Item Type	Item Serial	HD Serial Number	Asset Tag	Destroyed	Data Sanitized	Staff	Entry Date'
        devices.insert(0,tuple(cols.split('\t')))
        for driveNum in range(1,len(devices)):
            devices[driveNum] = (driveNum,) + devices[driveNum]
        return tuple(devices)
    def qcDevicesToTuple(self):
        devices = self.fetchall(sql.Report.qcInfo,self.donationID)
        cols = 'Sample	HD Serial Number	Date Reviewed	Staff'
        devices.insert(0,tuple(cols.split('\t')))
        for driveNum in range(1,len(devices)):
            devices[driveNum] = (driveNum,) + devices[driveNum]
        return tuple(devices)
    def removeDuplicates(self):
        self.cur.execute(sql.tidyup.cutdown % (self.donationIDVar.get(),))
        self.conn.commit()
        return self
    def TupleToTabDelimitedReport(self,appendage,devicesTuple):
        downloadsFolder = join(Path.home(),'Downloads')
        fileName = '%s - %s - %s.txt' % (self.donationInfo[2],self.donationInfo[0],str(appendage))
        filepath = join(downloadsFolder,fileName)
        outfile = open(filepath,"w")
        for row in devicesTuple:
            for col in row:
                outfile.write(str(col) + '\t')
            outfile.write('\n')
        outfile.close()
        return filepath
    def lookIntoLots(self,event):
        pop_up = tk.Toplevel(self.parent)
        pop_up.title('Lots info')
        InvestigateLots(pop_up,ini_section=self.ini_section,donationID=self.donationIDVar)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Drive register Station")
    app = ProcessedHardDrives(root,ini_section='appendage')
    app.mainloop()
