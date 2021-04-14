import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import datetime
import re
from sql import *
from config import DBI
from demoWriteSheet import *
class DonationBanner(tk.Frame):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent)
        self.parent = parent
        if 'donationIDVar' in kwargs:
            self.donationIDVar = kwargs['donationIDVar']
        else:
            self.donationIDVar = tk.StringVar(parent)
        if 'sheetIDVar' in kwargs:
            self.sheetIDVar = kwargs['sheetIDVar']
        else:
            self.sheetIDVar = tk.StringVar(parent)
        self.companyNameVar = tk.StringVar(parent)
        self.lotNumberVar = tk.StringVar()
        self.dateReceivedVar = tk.StringVar(parent)
        if 'ini_section' in kwargs:
            self.ini_section=kwargs['ini_section']
        else:
            print('no ini section provided. defaulting to default local...')
            self.ini_section = 'local_appendage'
        if 'companyName' in kwargs:
            self.companyNameVar.set("Donor Name: " + kwargs['companyName'])
        else:
            self.companyNameVar.set("Donor Name: "+'NO COMPANY NAME PROVIDED')
        if 'dateReceived' in kwargs:
            self.dateReceivedVar.set("Date Media Received: " +kwargs['dateReceived'])
        else:
            self.dateReceivedVar.set("Date Media Received: "+"None")
        if 'lotNumber' in kwargs:
            self.lotNumberVar.set("Lot Number: " +kwargs['lotNumber'])
        else:
            self.lotNumberVar.set("Lot Number: "+"None")
        self.companyName = tk.Label(parent,textvariable=self.companyNameVar)
        self.dateReceived = tk.Label(parent,textvariable=self.dateReceivedVar)
        self.lotNumber = tk.Label(parent,textvariable=self.lotNumberVar)
        self.sheetIDVar_ = tk.StringVar()
        self.sheetID = tk.Label(parent,textvariable=self.sheetIDVar_)
        self.selDonationButton = tk.Button(parent,
            text='Select Donation',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.selDonationButton.bind('<Button-1>',self.chooseDonation)
        self.companyName.pack(padx=10,pady=10)
        self.dateReceived.pack(padx=10,pady=10)
        self.lotNumber.pack(padx=10,pady=10)
        self.selDonationButton.pack(padx=10,pady=10)

    def chooseDonation(self,event):
        pop_up = tk.Toplevel(self.parent)
        SelectDonation(pop_up,
            ini_section=self.ini_section,
            companyNameVar=self.companyNameVar,
            dateReceivedVar=self.dateReceivedVar,
            lotNumberVar=self.lotNumberVar,
            donationID=self.donationIDVar,
            sheetIDVar = self.sheetIDVar,
            bannerSheetIDVar = self.sheetIDVar_)
class SelectDonation(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args)
        self.parent = parent
        self.companyNameVar = kwargs['companyNameVar']
        self.dateReceivedVar = kwargs['dateReceivedVar']
        self.lotNumberVar = kwargs['lotNumberVar']
        self.donationIDVar = kwargs['donationID']
        self.ini_section = kwargs['ini_section']
        self.sheetIDVar = kwargs['sheetIDVar']
        self.sheetIDVar_ = kwargs['bannerSheetIDVar']
        DBI.__init__(self)
        self.donorInfoVar = tk.StringVar(parent,value="select donation:")
        donationInfo = self.fetchall(DonorInfo.getDonationHeader,'')
        donationInfo =[str(dInfo[0]) + ', '+dInfo[1].strftime('%m/%d/%y')+', '+str(dInfo[2])
            for dInfo in donationInfo]
        if len(donationInfo) == 0:
            self.NewDonationPopUp(None)
        self.donationInfoDD = tk.OptionMenu(parent,self.donorInfoVar,*donationInfo)
        self.donationFilter = tk.Entry(parent,fg='black',bg='white',width=10)
        donationFilterLabel = tk.Label(parent,text='filter donation names via:')
        self.passBackSelection = tk.Button(parent,
            text='Pass Back Selection',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.passBackSelection.bind('<Button-1>',self.updateBanner)
        self.updateDDButton = tk.Button(parent,
            text='Update Dropdown',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.updateDDButton.bind('<Button-1>',self.refreshOptionMenu)
        self.insertDonationButton = tk.Button(parent,
            text='Insert New Donoation',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.insertDonationButton.bind('<Button-1>',self.NewDonationPopUp)
        self.insertDonationButton.grid(row=2,column=2)
        self.updateDDButton.grid(row=0,column=2)
        donationFilterLabel.grid(column=0,row=0)
        self.donationFilter.grid(column=1,row=0)
        self.donationInfoDD.grid(row=1,column=1)
        self.passBackSelection.grid(row=2,column=1)
    def NewDonationPopUp(self,event):
        popUp = tk.Toplevel(self.parent)
        NewDonation(popUp,ini_section=self.ini_section,donationID=self.donationIDVar)
    def refreshOptionMenu(self,event):
        self.donationInfoDD['menu'].delete(0,'end')
        filtered_donorInfo = self.fetchall(DonorInfo.getDonationHeader,
                                        self.donationFilter.get())
        for dInfo in filtered_donorInfo:
            dinfoStr = str(dInfo[0]) + ', '+dInfo[1].strftime('%m/%d/%y')+', '+str(dInfo[2])
            self.donationInfoDD['menu'].add_command(label=dinfoStr,
                command=tk._setit(self.donorInfoVar,dinfoStr))
    def updateBanner(self,event):
        var = self.donorInfoVar.get().split(',')
        self.companyNameVar.set("Donor Name: "+var[0])
        self.dateReceivedVar.set("Date Media Received: "+var[1])
        self.lotNumberVar.set("Lot Number: "+var[2])
        ids = self.fetchone(DonorInfo.getDonationID,*var)
        self.donationIDVar.set(ids[0])
        self.sheetIDVar.set(ids[1])
        self.sheetIDVar_.set('Sheet ID: '+ids[1])
        self.parent.destroy()
class NewDonor(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args)
        if 'ini_section' in kwargs:
            self.ini_section = kwargs['ini_section']
        DBI.__init__(self)
        self.donorName = tk.Entry(parent,fg='black',bg='white',width=35)
        self.dnLabel = tk.Label(parent,text="Donor Name:")
        self.donorAddress = tk.Entry(parent,fg='black',bg='white',width=50)
        self.daLabel = tk.Label(parent,text="Donor Address:")
        self.status = tk.StringVar(parent)
        self.statusNote = tk.Label(parent,textvariable=self.status)
        self.insertDonorButton = tk.Button(parent,
            text='Insert New Donor',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.insertDonorButton.bind('<Button-1>',self.insertDonor)
        parent.bind('<Return>',self.insertDonor)
        self.dnLabel.grid(row=0,column=0)
        self.donorName.grid(row=0,column=1)
        self.daLabel.grid(row=1,column=0)
        self.donorAddress.grid(row=1,column=1)
        self.statusNote.grid(row=2,column=0)
        self.insertDonorButton.grid(row=2,column=1)
    def insertDonor(self,event):
        donorName = str(self.donorName.get())
        donorAddress = str(self.donorAddress.get())
        back = self.insertToDB(DonorInfo.insertNewDonor,
        donorName,donorAddress)
        self.status.set(back)
        if back == "success!":
            self.donorName.delete(0,'end')
            self.donorAddress.delete(0,'end')

class NewDonation(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args)
        self.parent=parent
        self.ini_section=kwargs['ini_section']
        self.donationID=kwargs['donationID']
        DBI.__init__(self)
        donors = self.fetchall(DonorInfo.getDonors,'')
        donors =[donor[0] for donor in donors]
        self.donorName = tk.StringVar(parent,value="select a donor:")
        self.donorsDD = tk.OptionMenu(parent,self.donorName,*donors)
        self.insertDonoationButton = tk.Button(parent,
            text='Insert New Donation',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        now = datetime.datetime.now()
        self.cal = Calendar(parent, font="Arial 14", selectmode='day',
                   cursor="hand1", year=now.year, month=now.month, day=now.day)
        self.calLabel = tk.Label(parent,text='Date Received')
        self.donorFilter = tk.Entry(parent,fg='black',bg='white',width=10)
        self.lotNumber = tk.Entry(parent,fg='black',bg='white',width=10)
        self.lotNumberLabel = tk.Label(parent,text="Lot Number: ")
        self.donorFilterLabel = tk.Label(parent,text="Filter Donors By:")
        self.donorFilterLaunch = tk.Button(parent,
            text='Update Dropdown',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.newDonorLaunch = tk.Button(parent,
            text='Insert New Donor',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.calLabel.grid(row=2,column=1)
        self.cal.grid(row=3,column=1)
        self.donorFilterLaunch.bind('<Button-1>',self.refreshOptionMenu)
        self.insertDonoationButton.bind('<Button-1>',self.insertDonation)
        self.newDonorLaunch.bind('<Button-1>',self.NewDonorPopUp)
        self.donorsDD.grid(row=1,column=1)
        self.donorFilterLabel.grid(row=0,column=0)
        self.donorFilter.grid(row=0,column=1)
        self.donorFilterLaunch.grid(row=0,column=2)
        self.lotNumberLabel.grid(row=4,column=0)
        self.lotNumber.grid(row=4,column=1)
        self.newDonorLaunch.grid(row=5,column=0)
        self.insertDonoationButton.grid(row=5,column=2)
        self.status = tk.StringVar(parent)
        self.statusBar = tk.Label(parent,textvariable=self.status)
        self.statusBar.grid(row=5,column=1)
    def NewDonorPopUp(self,event):
        popUp = tk.Toplevel(self.parent)
        NewDonor(popUp,ini_section=self.ini_section)
    def refreshOptionMenu(self,event):
        self.donorsDD['menu'].delete(0,'end')
        filtered_donors = self.fetchall(DonorInfo.getDonors,
                                        self.donorFilter.get())
        for donor in filtered_donors:
            self.donorsDD['menu'].add_command(label=donor[0],
                command=tk._setit(self.donorName,donor[0]))
    def insertDonation(self,event):
        donorName = self.donorName.get()
        donationDate = self.cal.selection_get()
        lotNumber = self.lotNumber.get()
        sheetID = createSheet(lotNumber + ' - '+donorName+' - Data Sanitization & QC Log')
        if lotNumber == '':
            lotNumber = 0
            statusAppendage = 'with lot number = 0'
        else:
            statusAppendage = ''
        out = self.insertToDB(DonorInfo.insertNewDonation,
            lotNumber,
            donationDate,
            donorName,
            str(sheetID))
        report = [
            ['Company Name: {}'.format(donorName)],
            ['Date Received: {} '.format(donationDate.strftime('%m/%d/%Y'))],
            ['Lot Number: {}'.format(lotNumber)],
            ['']
        ]
        cols = 'Drive	Item Type	Item Serial	HD Serial Number	Asset Tag	Destroyed	Data Sanitized	Staff	Entry Date'
        report.append(cols.split('	'))
        write_to_sheet(str(sheetID),report)
        self.status.set(out+statusAppendage)
class GenerateReport(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args)
        DBI.__init__(self,ini_section = kwargs['ini_section'])
        self.donationID = kwargs['donationID']
        if 'sheetID' not in kwargs:
            self.sheetIDLabel = tk.Label(parent,text='Google Sheet ID:').grid(column=0,row=0)
            self.sheetID = tk.Entry(parent,fg='black',bg='white',width=40)
            self.sheetID.grid(column=1,row=0)
        self.getReportButton = tk.Button(parent,
            text='Generate New Report',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.getReportButton.bind('<Button-1>',self.writeSheet)
        self.getReportButton.grid(column=1,row=2)
    def writeSheet(self,event):
        donationID = self.donationID.get()
        donationInfo=self.fetchone(Report.donationInfo,donationID)
        report = [
            ['Company Name: {}'.format(donationInfo[0])],
            ['Date Received: {} '.format(donationInfo[1].strftime('%m/%d/%Y'))],
            ['Lot Number: {}'.format(donationInfo[2])],
            ['']
        ]
        cols = 'Drive	Item Type	Item Serial	HD Serial Number	Asset Tag	Destroyed	Data Sanitized	Staff	Entry Date'
        report.append(cols.split('	'))
        devices = self.fetchall(Report.deviceInfo,donationID)
        drive = [1]
        for device in devices:
            dlist = list(device)
            try:
                dlist[-1] = dlist[-1].strftime("%m/%d/%Y %H:%M")
            except:
                pass
            finally:
                report.append(drive + dlist)
                drive[0]+=1
        sid = self.sheetID.get()
        import csv
        with open('report.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(report)
        write_to_sheet(sid,report)
class ProcessedHardDrives(GenerateReport):
    def __init__(self,parent,*args,**kwargs):
        #tk.Frame.__init__(self,parent,*args)
        GenerateReport.__init__(self,parent,
            ini_section = kwargs['ini_section'],
            donationID = kwargs['donationID'],
            sheetID = kwargs['sheetID'])
        self.sheetID = kwargs['sheetID']
        #DBI.__init__(self,ini_section = kwargs['ini_section'])
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
        self.updateSheetButton = tk.Button(parent,
            text='update Sheet',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.updateSheetButton.bind('<Button-1>',self.writeSheet)
        self.err = tk.StringVar()
        self.errorFlag = tk.Label(parent,textvariable=self.err)
        self.hdLabel.grid(row=0,column=0)
        self.hd.grid(row=0,column=1)
        self.wiperProductMenu.grid(row=1,column=1)
        self.errorFlag.grid(row=2,column=0)
        self.finishHDButton.grid(row=2,column=1)
        self.updateSheetButton.grid(row=3,column=1)
    def finishHD(self,event):
        now = datetime.datetime.now()
        wiped = self.wiperProduct.get()
        hd = self.hd.get()
        if wiped == "Wiped.":
            sql = DeviceInfo.noteWipedHD
        elif wiped == "Destroyed.":
            sql = DeviceInfo.noteDestroyedHD
        try:
            self.cur.execute(sql,(now,hd,))
            self.conn.commit()
            if len(self.cur.fetchall()) == 0:
                self.err.set('Error! Error! provided HD SN '+hd +' isn\'t in system!')
            else:
                self.err.set('success!')
            self.hd.delete(0,'end')
        except (Exception, psycopg2.DatabaseError) as error:
            self.err.set(error)
        finally:
            pass
class InsertDeviceType(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        self.parent=parent
        tk.Frame.__init__(self,parent,*args)
        DBI.__init__(self,ini_section = kwargs['ini_section'])
        self.dtdd = kwargs['DTDD']
        self.typeVar = kwargs['typeVar']
        self.type = tk.Entry(parent,fg='black',bg='white',width=25)
        self.insertTypeButton = tk.Button(parent,
            text='insert',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.insertTypeButton.bind('<Button-1>',self.insertType)
        self.typeLabel=tk.Label(parent,text="new type:").grid(row=0,column=0)
        self.type.grid(row=0,column=1)
        self.insertTypeButton.grid(row=1,column=1)
    def insertType(self,event):
        self.insertToDB(DeviceInfo.insertNewDeviceType,self.type.get())
        self.refreshDTOptionMenu()
        self.parent.destroy()
    def refreshDTOptionMenu(self):
        self.dtdd['menu'].delete(0,'end')
        deviceTypes = self.fetchall(DeviceInfo.getDeviceTypes)
        for type in deviceTypes:
            self.dtdd['menu'].add_command(label=type[0],
                command=tk._setit(self.typeVar,type[0]))
class InsertDrives(tk.Frame,DBI):
    def __init__(self,parent,root,*args,**kwargs):
        self.parent = parent
        tk.Frame.__init__(self,parent,*args)
        DBI.__init__(self,ini_section = kwargs['ini_section'])
        self.donationID = kwargs['donationID']
        self.sheetIDVar = kwargs['sheetID']
        deviceTypes = self.fetchall(DeviceInfo.getDeviceTypes)
        dtypes =[type[0] for type in deviceTypes]
        self.typeName = tk.StringVar(parent,value="device type:")
        self.typeDD = tk.OptionMenu(parent,self.typeName,"device type:",*dtypes)
        deviceQualities = self.fetchall(DeviceInfo.getDeviceQualities)
        qtypes =[quality[0] for quality in deviceQualities]
        self.qualityName = tk.StringVar(parent,value="quality:")
        self.qualityDD = tk.OptionMenu(parent,self.qualityName,"quality:",*qtypes)
        stafflist = self.fetchall(DeviceInfo.getStaff)
        snames =[staff[0] for staff in stafflist]
        self.staffName = tk.StringVar(parent,value="staff:")
        self.staffDD = tk.OptionMenu(parent,self.staffName,"staff:",*snames)
        self.dSerialL = tk.Label(parent,text="Device Serial #:")
        self.hdSerialL = tk.Label(parent,text="Hard Drive Serial:")
        self.assetTagL = tk.Label(parent,text="Asset Tag:")
        self.pidL = tk.Label(parent,text="pid:")
        self.pid = tk.Entry(parent,fg='black',bg='white',width=12)
        self.dSerial = tk.Entry(parent,fg='black',bg='white',width=10)
        self.hdSerial = tk.Entry(parent,fg='black',bg='white',width=10)
        self.assetTag = tk.Entry(parent,fg='black',bg='white',width=10)
        self.insertDeviceButton = tk.Button(parent,
            text='insert',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.insertDeviceButton.bind('<Button-1>',self.insertDevice)
        root.bind('<Return>',self.insertDevice)
        self.insertDeviceTypeButton = tk.Button(parent,
            text='new Device Type',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.insertDeviceTypeButton.bind('<Button-1>',self.NewDTPopUp)
        self.insertDeviceTypeButton.grid(row=7,column=0)
        self.successVar = tk.StringVar()
        self.successLabel = tk.Label(parent,textvariable=self.successVar)
        self.pidL.grid(row=1,column=0)
        self.pid.grid(row=1,column=1)
        self.staffDD.grid(row=0,column=1)
        self.dSerialL.grid(row=2,column=0)
        self.dSerial.grid(row=2,column=1)
        self.hdSerialL.grid(row=3,column=0)
        self.hdSerial.grid(row=3,column=1)
        self.assetTagL.grid(row=4,column=0)
        self.assetTag.grid(row=4,column=1)
        self.qualityDD.grid(row=5,column=0)
        self.typeDD.grid(row=5,column=1)
        self.successLabel.grid(row=6,column=0)
        self.insertDeviceButton.grid(row=6,column=1)
        self.lastDeviceSNvar = tk.StringVar(parent)
        self.lastDeviceHDSNvar = tk.StringVar(parent)
        tk.Label(parent,text="last entries:").grid(row=8,column=0)
        tk.Label(parent,textvariable=self.lastDeviceSNvar).grid(row=8,column=1)
        tk.Label(parent,textvariable=self.lastDeviceHDSNvar).grid(row=8,column=2)
    def NewDTPopUp(self,event):
        popUp = tk.Toplevel(self.parent)
        InsertDeviceType(popUp,ini_section=self.ini_section,
            DTDD =self.typeDD,typeVar=self.typeName)
    def insertDevice(self,event):
        staff = self.staffName.get()
        if staff == "staff:":
            self.successVar.set('please select staff member')
        else:
            dSerial = self.dSerial.get()
            hdSerial = self.hdSerial.get()
            assetTag = self.assetTag.get()
            type = self.typeName.get()
            if type == "device type:":
                self.successVar.set('please select (or insert) device type')
            else:
                quality = self.qualityName.get()
                pid = self.pid.get()
                donationID = self.donationID.get()
                args =[str(type),str(dSerial),str(hdSerial),
                str(assetTag),str(staff),str(pid),str(donationID),
                datetime.datetime.now()]
                if len(str(hdSerial)) > 0:
                    out = self.insertToDB(DeviceInfo.insertDevice,*args)
                else:
                    argsNoHd = args[:2]+args[3:]
                    out = self.insertToDB(DeviceInfo.insertDeviceNoHD,*argsNoHd)
                if quality != "quality:":
                    out = self.insertToDB(DeviceInfo.updateDeviceQuality,quality,dSerial)
                self.successVar.set(out)
                self.lastDeviceSNvar.set(str(dSerial))
                self.lastDeviceHDSNvar.set(str(hdSerial))
                self.successVar.set(out)
                googleArgs = [str(-1)] + args[:4]+['','']+args[4:5]+[args[-1].strftime('%m/%d/%Y %I:%M:%S')]
                append_to_sheet(self.sheetIDVar.get(),[googleArgs])
                self.pid.delete(0,'end')
                self.dSerial.delete(0,'end')
                self.hdSerial.delete(0,'end')
                self.assetTag.delete(0,'end')
                self.pid.focus()

class extractionGUI(ttk.Notebook):
    def __init__(self,parent,*args,**kwargs):
        self.donationIDVar = tk.StringVar()
        self.sheetIDVar = tk.StringVar()
        self.donorIdentifier = DonationBanner(parent,
                                ini_section=kwargs['ini_section'],
                                donationIDVar = self.donationIDVar,
                                sheetIDVar = self.sheetIDVar)
        ttk.Notebook.__init__(self,parent,*args)
        self.tab1 = ttk.Frame()
        #self.tab2 = ttk.Frame()
        self.tab3 = ttk.Frame()
        # ProcessedHardDrives(self.tab2,
        #     ini_section=kwargs['ini_section'],
        #     donationID=self.donationIDVar,
        #     sheetID = self.sheetIDVar)
        InsertDrives(self.tab1,parent,
            ini_section=kwargs['ini_section'],
            donationID=self.donationIDVar,
            sheetID = self.sheetIDVar)
        GenerateReport(self.tab3,
            ini_section=kwargs['ini_section'],
            donationID=self.donationIDVar)
        self.add(self.tab1,text="Insert New Drives.")
        #self.add(self.tab2,text="Note Wiped Hard Drives.")
        self.add(self.tab3,text="Generate Report")
        #self.add(self.banner)
        self.pack(expand=True,fill='both')
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Hard Drive Extraction Station")
    app = extractionGUI(root,ini_section='appendage')
    app.mainloop()
