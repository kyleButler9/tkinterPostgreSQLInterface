import tkinter as tk
from tkinter import ttk
from sql import *
from config import DBI
from donationBanner import *
from dataclasses import dataclass,fields,field
from collections import namedtuple
from Barcode_Scanner_Entries import *
from batchExecuteSQL import batchExecuteSqlCommands
@dataclass(frozen=True)
class Table_Keys:
    dg: str = None
    pcs: str = None
    hds: str = None
    donations: str = None
    # id, p_id,hd_id,donation_id;
    # this is the order of keys that comes outta the insert device query
    # whenever you hit insert.
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
    def __init__(self,parent,Barcode_Vals,*args,**kwargs):
        self.parent = parent
        tk.Frame.__init__(self,parent,*args)
        DBI.__init__(self,ini_section = kwargs['ini_section'])
        self.donationID = kwargs['donationID']
        self.lastDevice=kwargs['lastDevice_info']
        self.lastDevice_nonBarCode=kwargs['lastDevice_nonBarCode']
        #self.sheetIDVar = kwargs['sheetID']
        deviceTypes = self.fetchall("SELECT deviceType FROM deviceTypes;")
        dtypes =[type[0] for type in deviceTypes]
        self.typeName = tk.StringVar(parent,value="device type:")
        self.typeDD = tk.OptionMenu(parent,self.typeName,"device type:",*dtypes)
        deviceQualities = self.fetchall("SELECT q.quality FROM qualities q;")
        qtypes =[quality[0] for quality in deviceQualities]
        self.qualityName = tk.StringVar(parent,value="quality:")
        self.qualityDD = tk.OptionMenu(parent,self.qualityName,"quality:",*qtypes)
        getStaff = \
        """
        SELECT name
        FROM staff
        WHERE active=TRUE;
        """
        stafflist = self.fetchall(getStaff)
        snames =[staff[0] for staff in stafflist]
        self.staffName = tk.StringVar(parent,value="staff:")
        ROW=0
        tk.OptionMenu(parent,self.staffName,"staff:",*snames).grid(row=ROW,column=0)
        self.entries=BarcodeScannerMode(parent,ROW,Barcode_Vals)
        row_count = self.entries.get_rowcount()
        self.entries.grid(row=ROW,columnspan=2,rowspan=row_count)
        ROW+=row_count
        ROW+=1
        self.qualityDD.grid(row=ROW,column=0)
        self.typeDD.grid(row=ROW,column=1)
        ROW+=1
        self.err = tk.StringVar(parent)
        tk.Label(parent,textvariable=self.err).grid(row=ROW,column=0)
        ROW+=1
        self.insertDeviceButton = tk.Button(parent,
            text='insert',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.insertDeviceButton.bind('<Button-1>',self.insertDevice)
        self.insertDeviceTypeButton = tk.Button(parent,
            text='new Device Type',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.insertDeviceTypeButton.bind('<Button-1>',self.NewDTPopUp)
        self.insertDeviceTypeButton.grid(row=ROW,column=0)
        self.insertDeviceButton.grid(row=ROW,column=1)
        ROW+=1
        tk.Label(parent,text="last entries:").grid(row=ROW,column=0) #consider including a columnspan
        tk.Label(parent,text="Computer").grid(row=ROW,column=1)
        tk.Label(parent,text="HD").grid(row=ROW,column=2)
        ROW+=1
        tk.Label(parent,textvariable=self.lastDevice.pc_id).grid(row=ROW,column=1)
        tk.Label(parent,textvariable=self.lastDevice.hd_id).grid(row=ROW,column=2)
        ROW+=1
        tk.Label(parent,textvariable=self.lastDevice.pc_sn).grid(row=ROW,column=1)
        tk.Label(parent,textvariable=self.lastDevice.hd_sn).grid(row=ROW,column=2)
    def NewDTPopUp(self,event):
        popUp = tk.Toplevel(self.parent)
        InsertDeviceType(popUp,ini_section=self.ini_section,
            DTDD =self.typeDD,typeVar=self.typeName)
    def get_vals_from_form(self):
        donationID = self.donationID.get()
        if len(donationID) == 0:
            self.err.set("Please select a donation.")
            return self

        staff = self.staffName.get()
        if staff == "staff:":
            self.err.set('please select staff member')
            return self

        type = self.typeName.get()
        if type == "device type:":
            self.err.set('please select (or insert) device type')
            return self

        quality = self.qualityName.get()
        if quality == "quality:":
            quality = None
            #consider forcing a quality choice here as done above with staff and type.
        if self.entries.pc_id.index("end") < 2:
            pc_id = None
        else:
            pc_id = self.entries.pc_id.get()
            if not (pc_id[:2] == 'MD' or pc_id[:2] == 'md'):
                self.err.set('please provide a pid that begins with "MD"')
                return self
            if pc_id[-1] == " " or pc_id[-1] == "\`":
                self.err.set('please remove trailing space or tick from pid.')
                return self

        if self.entries.pc_sn.index("end") < 2:
            pc_sn = None
        else:
            pc_sn = self.entries.pc_sn.get()
            if pc_id is None:
                self.err.set("Please provide a PC ID with Computer SN or clear Computer Serial Entry.")
                return self
            if pc_sn[0] == " " or pc_sn[0] == "\`" or pc_sn[-1] == " " or pc_sn[-1] =="\`":
                self.err.set('please provide a valid device serial or clear the form. Check for an extra space at the end of the entry or something..')
                return self
        if self.entries.hd_id.index("end") < 2:
            hd_id=None
        else:
            hd_id = self.entries.hd_id.get()
            if hd_id[0] == " " or hd_id[0]== "\`" or hd_id[-1] == " " or hd_id[-1]== "\`":
                self.err.set('please provide a valid hard drive id or clear the entry')
                return self
        if self.entries.hd_sn.index("end") < 2:
            hd_sn = None
        else:
            hd_sn = self.entries.hd_sn.get()
            if hd_id is None:
                self.err.set("Please provide a HD ID with Hard Drive or clear Hard Drive Serial Entry.")
                return self
            if hd_sn[0] == " " or hd_sn[0]== "\`" or hd_sn[-1] == " " or hd_sn[-1]== "\`":
                self.err.set('please provide a valid hard drive serial or clear the entry. Check the beginning and end of the serial number for an extra space or something.')
                return self

        if self.entries.asset_tag.index("end") != 0:
            asset_tag = self.entries.asset_tag.get()
            if asset_tag[0] == " " or asset_tag[0] =="\`" or asset_tag[-1] == " " or asset_tag[-1]== "\`":
                self.err.set('Please provide a valid asset tag. Check the beginning and end of the serial number for an extra space or something.')
                return self
        else:
            asset_tag = None
        return (donationID,asset_tag,pc_id,pc_sn,hd_id,hd_sn,staff,type,quality)
    def insertDevice(self,event):
        args = self.get_vals_from_form()
        submitted_headers= NonBarcode_Vals(args[0],args[6],args[7],args[8])
        submitted_form=Barcode_Vals(args[2],args[3],args[4],args[5],args[1])
        insertDevice = \
        """
        DROP TABLE IF EXISTS user_inputs;
        CREATE TEMP TABLE user_inputs(
            devicetype_id integer,
            pc_sn VARCHAR(20),
            hd_sn VARCHAR(20),
            pc_id VARCHAR(20),
            hd_id VARCHAR(20),
            asset_tag VARCHAR(255),
            quality_id integer,
            staff_id integer,
            intake_date timestamp,
            donation_id integer,
            pc_table_id INTEGER,
            hd_table_id INTEGER
            );
        INSERT INTO user_inputs(
            donation_id,
            asset_tag,
            pc_id,
            pc_sn,
            hd_id,
            hd_sn,
            staff_id,
            devicetype_id,
            quality_id,
            intake_date
	)
        VALUES (
            %s,
            %s,
            TRIM(LOWER(%s)),
            TRIM(LOWER(%s)),
            TRIM(LOWER(%s)),
            TRIM(LOWER(%s)),
            (SELECT s.staff_id FROM staff s WHERE s.name =%s),
            (SELECT dt.type_id FROM deviceTypes dt WHERE dt.deviceType = %s),
            (SELECT quality_id from qualities where quality = %s),
            NOW()
        );
        with device_info as (
            INSERT INTO computers(pid,sn,type_id,quality_id)
                SELECT pc_id,pc_sn,devicetype_id, quality_id
                    FROM user_inputs
            ON CONFLICT (pid) DO UPDATE
                SET quality_id = EXCLUDED.quality_id,
                    type_id = EXCLUDED.type_id
            RETURNING p_id as pc_table_id
            ), harddrive_info as (
            INSERT INTO harddrives(hdpid,hdsn)
                SELECT hd_id,hd_sn
                    FROM user_inputs
            ON CONFLICT (hdpid) DO UPDATE
                SET hdsn = harddrives.hdsn
            RETURNING hd_id as hd_table_id
            )
        UPDATE user_inputs
            SET pc_table_id = (select pc_table_id from device_info),
                hd_table_id = (select hd_table_id from harddrive_info);
        INSERT INTO donatedgoods(donation_id,p_id,hd_id,intakedate,assettag,staff_id)
            SELECT donation_id,pc_table_id,hd_table_id,intake_date,asset_tag,staff_id
            FROM user_inputs
        RETURNING id, p_id,hd_id,donation_id;
        """
            #note that I'm leaving blank from the update the SN so that we can just scan the pid to add an additional HD
            #also note that when there is a harddrive conflict
            #the hdsn isnt updated
        if submitted_form.pc_id is not None:
            #recall that above we confirmed that
            #the computer serial number cannot be entered without a PC ID
            #however, a PC ID can be entered without a PC SN
            computer_insert = \
            """
            INSERT INTO computers(pid,sn,type_id,quality_id)
                SELECT pid,device_sn,devicetype_id, quality_id
                    FROM user_inputs
            ON CONFLICT (pid) DO UPDATE
                SET quality_id = EXCLUDED.quality_id,
                    type_id = EXCLUDED.type_id
            RETURNING p_id
            """
        else:
            computer_insert = "SELECT NULL AS p_id"
        if submitted_form.hd_id is not None:
            #recall that above we confirmed that
            #the hard drive serial number cannot be entered without a HD ID
            #however, a HD ID can be entered without a HD SN
            hd_insert = \
            """
            INSERT INTO harddrives(hdpid,hdsn)
                SELECT hdpid,device_hdsn
                    FROM user_inputs
            ON CONFLICT (hdpid) DO UPDATE
                SET hdsn = harddrives.hdsn
            RETURNING hd_id
            """
        else:
            hd_insert = "SELECT NULL as hd_id"
        insert_device_sql = insertDevice.format(computer_insert,hd_insert)
        try:
            out=self.fetchone(insert_device_sql,*args)
            self.lastDevice.table_keys = Table_Keys(*out)
            self.conn.commit()
            #note: next line is breaking.
            self.update_last_device_log(out,submitted_form,submitted_headers)
            self.clear_form()
            self.entries.pc_id.focus()
            self.err.set("success!")
        except (Exception, psycopg2.DatabaseError) as error:
            self.err.set(error)
            print(error)
        finally:
            return self
    def update_last_device_log(self,ids,submitted_form,submitted_headers):
        for key in self.lastDevice.get_entryfield_names():
            getattr(self.lastDevice,key).set(getattr(submitted_form,key))
        Entry_Vals_Fields = fields(submitted_headers)# [:-1]
        EV_field_names = [Entry_Vals_Field.name for Entry_Vals_Field in Entry_Vals_Fields]
        for key in EV_field_names:
            getattr(self.lastDevice_nonBarCode,key).set(getattr(submitted_headers,key))
        #self.lastDevice.pks=ids
        return self
    def clear_form(self):
        for key in self.entries.get_entryfield_names():
            getattr(self.entries,key).delete(0,'end')
        return self

class Review(InsertDrives):
    def __init__(self,parent,Barcode_Vals,*args,**kwargs):
        self.parent = parent
        self.ini_section=kwargs['ini_section']
        self.donationID=kwargs['donationID']
        InsertDrives.__init__(self,self.parent,Barcode_Vals,
            ini_section=kwargs['ini_section'],
            donationID=kwargs['donationID'],
            lastDevice_info=kwargs['lastDevice_info'],
            lastDevice_nonBarCode=kwargs['lastDevice_nonBarCode'])
        self.repopulate_form = tk.Button(parent,
            text='Get Last Submission',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.repopulate_form.bind('<Button-1>',self.repopulate)
        self.repopulate_form.grid()
    def repopulate(self,event):
        self.clear_form()
        for key in self.lastDevice.get_entryfield_names():
            getattr(self.entries,key).insert(0,getattr(self.lastDevice,key).get())
        self.staffName.set(self.lastDevice_nonBarCode.staff_name.get())
        self.typeName.set(self.lastDevice_nonBarCode.type_name.get())
        self.qualityName.set(self.lastDevice_nonBarCode.quality_name.get())
        #getattr(self.entries,key).insert(0,getattr(self.lastDevice_nonBarCode,key).get())
        return self
    def InsertDrives(self,event):
        donatedgoods_vals = tuple()
        donatedgoods_command=str()
        donatedgoods_command += "Update donatedgoods "
        idChange=False
        if self.donationID.get() != self.lastDevice_nonBarCode.donation_id.get():
            donatedgoods_command += "SET donation_id= %s "
            donatedgoods_vals+= (self.donationID.get(),)
            idChange=True
        if self.staffName.get() != self.lastDevice_nonBarCode.staff_name.get():
            if idChange:
                donatedgoods_command+=', '
            donatedgoods_command += "SET staff_id=(SELECT staff_id from staff where name = %s) "
            donatedgoods_vals+= (self.staffName.get(),)
        donatedgoods_command+="Where dg_id=%s" + ';'
        donatedgoods_vals +=(self.lastDevice.table_keys.dg,)
        donatedgoods = UpdateSql(donatedgoods_command,donatedgoods_vals)
        computers_vals=tuple()
        computers_command=str()
        computers_command+="UPDATE computers "
        typeChange=False
        if self.typeName.get() != self.lastDevice_nonBarCode.type_name.get():
            computers_command += "SET type_id=(SELECT type_id from devicetypes where devicetype = %s)"
            computers_vals+=(self.typeName.get(),)
            typeChange=True
        if self.qualityName.get() != self.lastDevice_nonBarCode.quality_name.get():
            if typeChange:
                sql_commands+=', '
            sql_commands += "SET quality_id=(SELECT quality_id from qualities where quality = %s)" + ' '
            computers_vals+=(self.qualityName.get(),)
        computers_command+="WHERE p_id=(SELECT p_id from donatedgoods where dg_id = %s);"
        computers_vals +=(self.lastDevice.table_keys.dg,)
        computers = UpdateSql(computers_command,computers_vals)
        nonBarcode_Commands =tuple(donatedgoods,computers,)
        barcode_commands=tuple()
        if getattr(self.entries,'pc_sn').get() !=getattr(self.lastDevice,'pc_sn').get():
            computers_command ="""
            Update computers
            SET sn = %s
            WHERE p_id =
                (SELECT p_id
                 FROM donatedgoods
                 WHERE id=%s);
            """
            computers_vals = tuple([getattr(self.entries,'pc_sn').get(),
                                    self.lastDevice.table_keys.dg])
            barcode_commands+=(UpdateSql(computers_command,computers_vals),)
        if getattr(self.entries,'hd_sn').get() !=getattr(self.lastDevice,'hd_sn').get():
            hds_command +="""
            Update harddrives
            SET hdsn = %s
            WHERE hd_id =
                (SELECT hd_id
                 FROM donatedgoods
                 WHERE id=%s);
            """
            computers_vals = tuple([getattr(self.entries,'hd_sn').get(),self.lastDevice.table_keys.dg])
            barcode_commands+=(UpdateSql(computers_command,computers_vals),)
        if getattr(self.entries,'asset_tag').get() !=getattr(self.lastDevice,'asset_tag').get():
            dg_command +="""
            Update donatedgoods
            SET assettag = %s
            WHERE id =%s;
            """
            dg_vals = tuple([getattr(self.entries,'asset_tag').get(),self.lastDevice.table_keys.dg])
            barcode_commands+=(UpdateSql(dg_command,dg_vals),)
        for sql in nonBarcode_Commands + barcode_commands:
            out=self.insertToDB(sql.msg,*sql.args)
            print(out)


@dataclass(frozen=True)
class UpdateSql:
    msg : str = None
    args : tuple[str] = field(default_factory=tuple)

@dataclass(order=True,frozen=True)
class NonBarcode_Vals:
    donation_id: int = None
    staff_name: str = "staff:"
    type_name: str = "device type:"
    quality_name: str = "quality:"
    # pks : list[int] =field(default_factory=list)
# this class here determines the entries part of the gui.
# you can add another label and entry row
# by merely editing this class and adding another row there
@dataclass(order=True,frozen=True)
class Barcode_Vals:
    pc_id: str = None
    pc_sn: str = None
    hd_id: str = None
    hd_sn: str = None
    asset_tag: str = None

class extractionGUI(ttk.Notebook):
    def __init__(self,parent,*args,**kwargs):
        donationIDVar = tk.StringVar(parent)
        lastDevice_nonBarCode=Entry_Form(parent,None,NonBarcode_Vals,TO_GENERATE='VARIABLES ONLY')
        lastDevice = Entry_Form(parent,None,Barcode_Vals,TO_GENERATE='VARIABLES ONLY')
        #self.sheetIDVar = tk.StringVar()
        DonationBanner(parent,
            ini_section=kwargs['ini_section'],
            donationIDVar = donationIDVar)
        ttk.Notebook.__init__(self,parent,*args)
        self.tab1 = ttk.Frame()
        InsertDrives(self.tab1,Barcode_Vals,
            ini_section=kwargs['ini_section'],
            donationID=donationIDVar,
            lastDevice_info=lastDevice,
            lastDevice_nonBarCode=lastDevice_nonBarCode)
        parent.bind('<Control-s>',InsertDrives.insertDevice)
        self.tab2 = ttk.Frame()
        Review(self.tab2,Barcode_Vals,
            ini_section=kwargs['ini_section'],
            donationID=donationIDVar,
            lastDevice_info=lastDevice,
            lastDevice_nonBarCode=lastDevice_nonBarCode)
            #sheetID = self.sheetIDVar)
        # GenerateReport(self.tab3,
        #     ini_section=kwargs['ini_section'],
        #     donationID=self.donationIDVar)
        self.add(self.tab1,text="Insert New Drives.")
        self.add(self.tab2,text="Review Submissions")
        #self.add(self.tab3,text="Generate Report")
        #self.add(self.banner)
        self.pack(expand=True,fill='both')
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Hard Drive Extraction Station")
    app = extractionGUI(root,ini_section='local_launcher')
    app.mainloop()
