from config import DBI;
import tkinter as tk
from multiprocessing import Process
from pathlib import Path
import os
from os.path import join
from extractionAppendage import *


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
        SELECT count(DISTINCT hd.hd_id),count(DISTINCT p.devicesn)
        FROM processing p INNER JOIN harddrives hd using (hd_id)
        WHERE p.donation_id = %s;
        """ % (donationID)
        res = self.fetchone(getInfo)
        msg=dict()
        self.num_HDSN.set("Hard Drive Count: " + str(res[0]))
        self.num_SN.set("Device Count: "+str(res[1]))
        queryPartiallyCompletedLot = \
        """
        SELECT count(hd_id) as howmanyleft
        from harddrives hd
        inner join processing USING (hd_id)
        inner join donations USING (donation_id)
        where hd.destroyed=FALSE and hd.sanitized=FALSE
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
        bool_and(case when hd.destroyed = TRUE or hd.sanitized=TRUE THEN TRUE ELSE FALSE END)
        from processing
        inner join donations using (donation_id)
        inner join donors USING (donor_id)
        inner join harddrives hd USING (hd_id)
        where processing.hd_id is not null and reported=FALSE
        group by donation_id
        having bool_and(case when hd.destroyed = TRUE or hd.sanitized=TRUE THEN TRUE ELSE FALSE END) = TRUE)

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
        with PartiallyCompletedLots as (select donation_id, count(p.hd_id) as howmanyleft
        from processing p
        inner join donations USING (donation_id)
        inner join harddrives hd USING (hd_id)
        where hd.destroyed=FALSE and hd.sanitized=FALSE and reported=FALSE
        group by donation_id
        having count(p.hd_id) < %s
        and count(p.hd_id)>0)

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
        self.markReportedButton = tk.Button(parent,
            text='Remove from Dropdown',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.markReportedButton.bind('<Button-1>',self.markReported)
        self.markReportedButton.pack()

        self.devicesTuple = tuple()
        self.err = tk.StringVar()
        tk.Label(parent,textvariable=self.err).pack()
    def markReported(self,event):
        self.donationID = self.donationIDVar.get()
        if len(self.donationID) == 0:
            self.err.set('Please select a donation.')
            return self
        markReportedSQL = \
        """
        WITH reportgen as (
        UPDATE donations
        SET reported = TRUE
        WHERE donation_id = %s
        RETURNING donation_id
        )
        SELECT donors.name, donations.lotnumber
        FROM donors
        INNER JOIN donations USING (donor_id)
        WHERE donation_id =
            (select donation_id from reportgen);
        """
        try:
            donorName=self.fetchone(markReportedSQL, self.donationID)
            self.conn.commit()
            self.err.set(str(donorName[0]) + ' | '+str(donorName[1]) + ' removed from dropdown.')
        except:
            self.err.set('unable to mark provided lot reported.')
            return self

    def getTextFiles(self,event):
        self.donationID=self.donationIDVar.get()
        if len(self.donationID) == 0:
            self.err.set('Please select a donation.')
            return self
        donationInfo = \
            """
            SELECT d.name, don.dateReceived, don.lotNumber
            FROM donors d
            INNER JOIN donations don USING (donor_id)
            WHERE don.donation_id = %s;
            """
        self.donationInfo=self.fetchone(donationInfo,self.donationID)
        devices = self.devicesToTuple()
        qcdevices=self.qcDevicesToTuple()
        devicesFilePath=self.TupleToTabDelimitedReport('',devices)
        qcFilePath=self.TupleToTabDelimitedReport('QC',qcdevices)
        procs = []
        # for outfile in [devicesFilePath,qcFilePath]:
        #     proc = Process(target=os.system,args=('notepad {}'.format(outfile),))
        #     procs.append(proc)
        #     proc.start()
        # for proc in procs:
        #     proc.join()
        self.err.set('Files successfully saved in your Downloads folder.')
        return self
    def devicesToTuple(self):
        deviceInfo = \
        """
        SELECT dts.deviceType, p.deviceSN,
            CASE WHEN hd.hdsn is NULL and hd.hdpid is NULL THEN COALESCE(hd.hdsn,'')
                WHEN hd.hdsn is NULL THEN COALESCE(hd.hdsn,'N/A')
                ELSE hd.hdsn END,
            p.assetTag, hd.destroyed, hd.sanitized, s.nameabbrev,
            CASE WHEN hd.hdpid is NULL THEN TO_CHAR(p.entryDate,'MM/DD/YYYY HH24:MI')
            ELSE TO_CHAR(hd.wipeDate,'MM/DD/YYYY HH24:MI')
            END AS date
        FROM processing p
        INNER JOIN deviceTypes dts on dts.type_id = p.deviceType_id
        INNER JOIN staff s on s.staff_id = p.staff_id
        INNER JOIN harddrives hd USING (hd_id)
        WHERE p.donation_id = %s
        ORDER BY p.entryDate;
        """
        devices = self.fetchall(deviceInfo,self.donationID)
        cols = 'Drive	Item Type	Item Serial	HD Serial Number	Asset Tag	Destroyed	Data Sanitized	Staff	Entry Date'
        devices.insert(0,tuple(cols.split('\t')))
        for driveNum in range(1,len(devices)):
            devices[driveNum] = (driveNum,) + devices[driveNum]
        return tuple(devices)
    def qcDevicesToTuple(self):
        qcInfo = \
        """
        SELECT hd.hdsn, TO_CHAR(qc.qcDate,'MM/DD/YYYY'),s.name
        FROM qualitycontrol qc
        INNER JOIN staff s ON qc.staff_id = s.staff_id
        INNER JOIN harddrives hd USING (hd_id)
        WHERE qc.donation_id = %s;
        """
        devices = self.fetchall(qcInfo,self.donationID)
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
    root.title("Report Generation Station")
    app = Report(root,ini_section='appendage')
    app.mainloop()

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
