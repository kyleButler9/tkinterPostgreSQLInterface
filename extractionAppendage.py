import tkinter as tk
from tkinter import ttk
from sql import *
from config import DBI
from donationBanner import *
from dataclasses import dataclass,fields,field
from collections import namedtuple


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
    def __init__(self,parent,*args,**kwargs):
        self.parent = parent
        tk.Frame.__init__(self,parent,*args)
        DBI.__init__(self,ini_section = kwargs['ini_section'])
        self.donationID = kwargs['donationID']
        self.lastDevice=kwargs['lastDevice_info']
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
        tk.OptionMenu(parent,self.staffName,"staff:",*snames).grid(row=0,column=1)
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
        self.err = tk.StringVar(parent)

        #the order of fields on the form is determined by the Entry_Vals objects ordering
        #as that's the order of "grid" in the next loop
        Entry_Vals_Fields = fields(Entry_Vals)[:-1]
        self.EV_fields = [Entry_Vals_Fields[i].name for i in range(len(Entry_Vals_Fields))]
        #self.entries = namedtuple('self.entries',self.EV_fields)
        self.entries={key : tk.Entry(parent,fg='black',bg='white',width=25) for key in self.EV_fields}
        rowIter=1
        for key in self.EV_fields:
            tk.Label(parent,text=key.replace("_"," ")+":").grid(row=rowIter,column=0)
            self.entries[key]=tk.Entry(parent,fg='black',bg='white',width=25)
            self.entries[key].grid(row=rowIter,column=1)
            rowIter+=1

        self.qualityDD.grid(row=rowIter,column=0)
        self.typeDD.grid(row=rowIter,column=1)
        rowIter+=1
        tk.Label(parent,textvariable=self.err).grid(row=rowIter,column=0)
        rowIter+=1
        self.insertDeviceTypeButton.grid(row=rowIter,column=0)
        self.insertDeviceButton.grid(row=rowIter,column=1)
        rowIter+=1
        tk.Label(parent,text="last entries:").grid(row=rowIter,column=0) #consider including a columnspan
        rowIter+=1
        tk.Label(parent,textvariable=self.lastDevice.pc_id).grid(row=rowIter,column=1)
        tk.Label(parent,textvariable=self.lastDevice.hd_id).grid(row=rowIter,column=2)
        rowIter+=1
        tk.Label(parent,textvariable=self.lastDevice.pc_sn).grid(row=rowIter,column=1)
        tk.Label(parent,textvariable=self.lastDevice.hd_sn).grid(row=rowIter,column=2)
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
        if self.entries['pc_id'].index("end") < 2:
            pc_id = None
        else:
            pc_id = self.entries['pc_id'].get()
            if not (pc_id[:2] == 'MD' or pc_id[:2] == 'md'):
                self.err.set('please provide a pid that begins with "MD"')
                return self
            if pc_id[-1] == " " or pc_id[-1] == "\`":
                self.err.set('please remove trailing space or tick from pid.')
                return self

        if self.entries['pc_sn'].index("end") < 2:
            pc_sn = None
        else:
            pc_sn = self.entries['pc_sn'].get()
            if pc_id is None:
                self.err.set("Please provide a PC ID with Computer SN or clear Computer Serial Entry.")
                return self
            if pc_sn[0] == " " or pc_sn[0] == "\`" or pc_sn[-1] == " " or pc_sn[-1] =="\`":
                self.err.set('please provide a valid device serial or clear the form. Check for an extra space at the end of the entry or something..')
                return self
        if self.entries['hd_id'].index("end") < 2:
            hd_id=None
        else:
            hd_id = self.entries['hd_id'].get()
            if hd_id[0] == " " or hd_id[0]== "\`" or hd_id[-1] == " " or hd_id[-1]== "\`":
                self.err.set('please provide a valid hard drive id or clear the entry')
                return self
        if self.entries['hd_sn'].index("end") < 2:
            hd_sn = None
        else:
            hd_sn = self.entries['hd_sn'].get()
            if hd_id is None:
                self.err.set("Please provide a HD ID with Hard Drive or clear Hard Drive Serial Entry.")
                return self
            if hd_sn[0] == " " or hd_sn[0]== "\`" or hd_sn[-1] == " " or hd_sn[-1]== "\`":
                self.err.set('please provide a valid hard drive serial or clear the entry. Check the beginning and end of the serial number for an extra space or something.')
                return self

        if self.entries['asset_tag'].index("end") != 0:
            asset_tag = self.entries['asset_tag'].get()
            if asset_tag[0] == " " or asset_tag[0] =="\`" or asset_tag[-1] == " " or asset_tag[-1]== "\`":
                self.err.set('Please provide a valid asset tag. Check the beginning and end of the serial number for an extra space or something.')
                return self
        else:
            asset_tag = None
        return (donationID,asset_tag,pc_id,pc_sn,hd_id,hd_sn,staff,type,quality)
    def insertDevice(self,event):
        args = self.get_vals_from_form()
        for arg in args:
            print(type(arg),arg)
        submitted_headers= Header_Vals(args[0],args[6],args[7],args[8])
        submitted_form=Entry_Vals(args[2],args[3],args[4],args[5],args[1])
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
            self.conn.commit()
            print(out,'here')
            self.update_last_device_log(out,submitted_form)
            self.clear_form()
            self.entries.pc_id.focus()
            self.err.set("success!")
        except (Exception, psycopg2.DatabaseError) as error:
            self.err.set(error)
            print(error)
        finally:
            return self
    def update_last_device_log(self,ids,submitted_form):
        for key in self.EV_fields:
            getattr(self.lastDevice,key).set(getattr(submitted_form,key))
        self.lastDevice.pks=ids
        return self
    def clear_form(self):
        for key in self.EV_fields:
            self.entries[key].delete(0,'end')
        return self

class Review(InsertDrives):
    def __init__(self,parent,*args,**kwargs):
        self.parent = parent
        self.ini_section=kwargs['ini_section']
        InsertDrives.__init__(self,self.parent,
            ini_section=kwargs['ini_section'],
            donationID=kwargs['donationID'],
            lastDevice_info=kwargs['lastDevice_info'])
        self.repopulate_form = tk.Button(parent,
            text='insert',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.repopulate_form.bind('<Button-1>',self.repopulate)
        self.repopulate_form.grid()
    def repopulate(self,event):
        self.clear_form()
        for key in self.EV_fields:
            getattr(self.entries,key).insert(0,getattr(self.lastDevice,key).get())
        return self
    def InsertDrives(self,event):
        pass

@dataclass(order=True,frozen=True)
class Entry_Vals:
    pc_id: str = None
    pc_sn: str = None
    hd_id: str = None
    hd_sn: str = None
    asset_tag: str = None
    pks : list[int] =field(default_factory=list)
@dataclass(order=True,frozen=True)
class Header_Vals:
    donation_id: str = None
    staff_name: str = None
    type_name: str = None
    quality_name: str = None

class Form_Entries:
    def __init__(self,parent):
        self.pc_id=tk.Entry(parent,fg='black',bg='white',width=25),
        self.pc_sn=tk.Entry(parent,fg='black',bg='white',width=25),
        self.hd_id=tk.Entry(parent,fg='black',bg='white',width=25),
        self.hd_sn=tk.Entry(parent,fg='black',bg='white',width=25),
        self.asset_tag=tk.Entry(parent,fg='black',bg='white',width=25)

class Form_Stringvars:
    def __init__(self,parent):
        self.pc_id=tk.StringVar(parent)
        self.pc_sn=tk.StringVar(parent)
        self.hd_id=tk.StringVar(parent)
        self.hd_sn=tk.StringVar(parent)
        self.asset_tag=tk.StringVar(parent)
class extractionGUI(ttk.Notebook):
    def __init__(self,parent,*args,**kwargs):
        donationIDVar = tk.StringVar(parent)
        last_device = Entry_Vals()
        lastDevice = Form_Stringvars(parent)
        #self.sheetIDVar = tk.StringVar()
        DonationBanner(parent,
            ini_section=kwargs['ini_section'],
            donationIDVar = donationIDVar)
        ttk.Notebook.__init__(self,parent,*args)
        self.tab1 = ttk.Frame()
        InsertDrives(self.tab1,
            ini_section=kwargs['ini_section'],
            donationID=donationIDVar,
            lastDevice_info=lastDevice)
        parent.bind('<Control-s>',InsertDrives.insertDevice)
        self.tab2 = ttk.Frame()
        Review(self.tab2,
            ini_section=kwargs['ini_section'],
            donationID=donationIDVar,
            lastDevice_info=lastDevice)
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
    app = extractionGUI(root,ini_section='appendage')
    app.mainloop()
