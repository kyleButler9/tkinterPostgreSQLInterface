import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import datetime
import re
from sql import *
from config import DBI
class DonationBanner(tk.Frame):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent)
        self.parent = parent
        if 'donationIDVar' in kwargs:
            self.donationIDVar = kwargs['donationIDVar']
        else:
            self.donationIDVar = tk.StringVar(parent)
        self.companyNameVar = tk.StringVar(parent)
        self.lotNumberVar = tk.StringVar()
        self.dateReceivedVar = tk.StringVar(parent)
        if 'ini_section' in kwargs:
            self.ini_section=kwargs['ini_section']
        else:
            print('no ini section provided. defaulting to local...')
            self.ini_section = local_appendage
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
    def updateBanner(self,**kwargs):
        self.companyNameVar.set(kwargs['companyName'])
        self.dateReceivedVar.set(kwargs['dateReceived'])
        self.lotNumberVar.set(kwargs['lotNumber'])
        donation_id = self.fetchone(DonorInfo.getDonationID,
                                    kwargs['companyName'],
                                    kwargs['dateReceived'],
                                    kwargs['lotNumber'])
        self.donationIDVar.set(donation_id)
    def chooseDonation(self,event):
        pop_up = tk.Toplevel(self.parent)
        SelectDonation(pop_up,
            ini_section='local_appendage',
            companyNameVar=self.companyNameVar,
            dateReceivedVar=self.dateReceivedVar,
            lotNumberVar=self.lotNumberVar,
            donationID=self.donationIDVar)
class SelectDonation(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args)
        self.parent = parent
        self.companyNameVar = kwargs['companyNameVar']
        self.dateReceivedVar = kwargs['dateReceivedVar']
        self.lotNumberVar = kwargs['lotNumberVar']
        self.donationIDVar = kwargs['donationID']
        if 'ini_section' in kwargs:
            self.ini_section = kwargs['ini_section']
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
        NewDonation(popUp,ini_section=self.ini_section)
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
        donation_id = self.fetchone(DonorInfo.getDonationID,*var)
        self.donationIDVar.set(donation_id[0])
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
        if 'ini_section' in kwargs:
            self.ini_section=kwargs['ini_section']
        DBI.__init__(self)
        donors = self.fetchall(DonorInfo.getDonors,'')
        donors =[donor[0] for donor in donors]
        self.donorName = tk.StringVar(parent,value="select a donor:")
        self.donorsDD = tk.OptionMenu(parent,self.donorName,*donors)
        self.insertDonoationButton = tk.Button(parent,
            text='Create New Donation',
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
            text='Filter Donors',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.newDonorLaunch = tk.Button(parent,
            text='New Donor',
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
        self.newDonorLaunch.grid(row=5,column=2)
        self.insertDonoationButton.grid(row=5,column=0)
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
        if lotNumber == '':
            lotNumber = 0
            statusAppendage = 'with lot number = 0'
        else:
            statusAppendage = ''
        out = self.insertToDB(DonorInfo.insertNewDonation,
            lotNumber,
            donationDate,
            donorName)
        self.status.set(out+statusAppendage)
class InsertDrives(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args)
        DBI.__init__(self,ini_section = kwargs['ini_section'])
        self.donationID = kwargs['donationID']
        deviceTypes = self.fetchall(DeviceInfo.getDeviceTypes)
        dtypes =[type[0] for type in deviceTypes]
        self.typeName = tk.StringVar(parent,value="device type:")
        self.typeDD = tk.OptionMenu(parent,self.typeName,"device type:",*dtypes)
        deviceQualities = self.fetchall(DeviceInfo.getDeviceQualities)
        qtypes =[quality[0] for quality in deviceQualities]
        self.qualityName = tk.StringVar(parent,value="quality:")
        self.qualityDD = tk.OptionMenu(parent,self.qualityName,"quality:",*qtypes)
        self.dSerialL = tk.Label(parent,text="Device Serial #:")
        self.hdSerialL = tk.Label(parent,text="Hard Drive Serial:")
        self.assetTagL = tk.Label(parent,text="Asset Tag:")
        self.pidL = tk.Label(parent,text="pid:")
        self.staffL = tk.Label(parent,text="Staff:")
        self.staff = tk.Entry(parent,fg='black',bg='white',width=20)
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
        self.successVar = tk.StringVar()
        self.successLabel = tk.Label(parent,textvariable=self.successVar)
        self.pidL.grid(row=1,column=0)
        self.pid.grid(row=1,column=1)
        self.staffL.grid(row=0,column=0)
        self.staff.grid(row=0,column=1)
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
    def insertDevice(self,event):
        dSerial = self.dSerial.get()
        hdSerial = self.hdSerial.get()
        assetTag = self.assetTag.get()
        staff = self.staff.get()
        type = self.typeName.get()
        quality = self.qualityName.get()
        pid = self.pid.get()
        donationID = self.donationID.get()
        self.pid.delete(0,'end')
        self.dSerial.delete(0,'end')
        self.hdSerial.delete(0,'end')
        self.assetTag.delete(0,'end')
        args =(str(dSerial),str(hdSerial),
        str(assetTag),str(staff),str(pid),
        str(donationID),datetime.datetime.now().strftime('%m/%d/%y'),)
        self.insertToDB(DeviceInfo.insertDevice,*args)
        if type != "device type:":
            out = self.insertToDB(DeviceInfo.updateDeviceType,type,dSerial)
        if quality != "quality:":
            out = self.insertToDB(DeviceInfo.updateDeviceQuality,quality,dSerial)
        self.successVar.set(out)
class ProcessedHardDrives(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args)
        DBI.__init__(self,ini_section = kwargs['ini_section'])
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
        self.err = tk.StringVar()
        self.errorFlag = tk.Label(parent,textvariable=self.err)
        self.hdLabel.grid(row=0,column=0)
        self.hd.grid(row=0,column=1)
        self.wiperProductMenu.grid(row=1,column=1)
        self.errorFlag.grid(row=2,column=0)
        self.finishHDButton.grid(row=2,column=1)
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

class extractionGUI(ttk.Notebook):
    def __init__(self,parent,*args,**kwargs):
        self.donationIDVar = tk.StringVar()
        self.donorIdentifier = DonationBanner(parent,
                                ini_section=kwargs['ini_section'],
                                donationIDVar = self.donationIDVar)
        ttk.Notebook.__init__(self,parent,*args)
        self.tab1 = ttk.Frame()
        self.tab2 = ttk.Frame()
        ProcessedHardDrives(self.tab2,
            ini_section=kwargs['ini_section'])
        InsertDrives(self.tab1,
            ini_section=kwargs['ini_section'],
            donationID=self.donationIDVar)
        self.add(self.tab1,text="Insert New Drives.")
        self.add(self.tab2,text="Note Wiped Hard Drives.")
        #self.add(self.banner)
        self.pack(expand=True,fill='both')
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Hard Drive Extraction Station")
    app = extractionGUI(root,ini_section='local_appendage')
    app.mainloop()
