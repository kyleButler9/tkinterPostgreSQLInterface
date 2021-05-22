import tkinter as tk
from config import DBI
import datetime
from os import system
from datetime import datetime,timedelta
from dataclasses import dataclass,field,fields
import time
@dataclass(order=True,frozen=True)
class Entry_Vals:
    pc_id: str = None
    pc_sn: str = None
    hd_id: str = None
    hd_sn: str = None
    asset_tag: str = None
class Entry_Form(tk.Frame):
    def __init__(self,parent,ROW,*args,**kwargs):
        LABEL_COLUMN=0
        ENTRY_COLUMN=1
        tk.Frame.__init__(self,parent,*args)
        # note that we're ignoring the pks list with the [:-1] below
        #      that we're using the Entry_Vals object to determine the fields in the Entry Form
        self.Entry_Vals_Fields = fields(Entry_Vals)# [:-1]
        self.EV_field_names = [Entry_Vals_Field.name for Entry_Vals_Field in self.Entry_Vals_Fields]
        self.row_count=len(self.EV_field_names)
        if 'TO_GENERATE' in kwargs:
            switch = kwargs['TO_GENERATE']
        else:
            switch = None
        if not switch or switch == 'ENTRIES ONLY':
            for key in self.EV_field_names:
                setattr(self,key,tk.Entry(parent,fg='black',bg='white',width=25))
        elif switch == 'ENTRIES AND VARIABLES':
            for key in self.EV_field_names:
                # use the below code to assign stringvars also to the entries
                string_var=None
                string_var=tk.StringVar(parent)
                setattr(self,key,tk.Entry(parent,fg='black',bg='white',width=25,textvariable=string_var))
                setattr(self,key+'_var',string_var)
        elif switch == 'VARIABLES ONLY':
            for key in self.EV_field_names:
                string_var=None
                string_var=tk.StringVar(parent)
                setattr(self,key,string_var)
        if ROW is not None:
            for key in self.EV_field_names:
                tk.Label(parent,text=key.replace("_"," ")+":").grid(row=ROW,column=LABEL_COLUMN)
                getattr(self,key).grid(row=ROW,column=ENTRY_COLUMN)
                ROW+=1
    def get_rowcount(self):
        return self.row_count
    def get_entry_fields(self):
        return self.Entry_Vals_Fields
    def get_entryfield_names(self):
        return self.EV_field_names
# here we're defining all the variables we're seeking to associate with
# each key in a struct-like class.
@dataclass(frozen=True)
class Key:
    is_pressed : bool = False
    time_pressed : datetime = datetime.now()
    widget : tk.Entry = None
    is_being_held : bool = False

# this object will be used to enable toggling between keyboard and  barcode scanner modes of input
class BarcodeScannerMode(Entry_Form):
    #note: this class is not finished. It still needs help
    # this is not the best way to handle scanner vs. keyboard
    def __init__(self,parent,ROW,*args,**kwargs):
        self.parent=parent
        # this keys dict will have a key for each possible keyboard input
        # and a value that is an instance of the Key dataclass
        self.keys=dict()
        # this button toggles between Keyboard mode and Scanner mode.
        self.Button = tk.Button(parent,
            text='Scanner Mode',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.Button.bind('<Button-1>',self.bind_or_unbind)
        self.Button.grid(row=ROW,column=1)
        ROW+=1
        Entry_Form.__init__(self,parent,ROW,*args,**kwargs)
        self.grid(row=ROW,columnspan=2,rowspan=self.row_count)
        self.initialize_bindings()
    def initialize_bindings(self):
        try:
            for key in self.EV_field_names:
                getattr(self,key).bind("<KeyPress>",self.keydown)
                getattr(self,key).bind("<KeyRelease>",self.keyup)
        except AttributeError as err:
            print(err)
            print('You need to run this method after initializing Entry_Form.')
    def bind_or_unbind(self,event):
        # if the button says keyboard mode, then start scanner mode
        # and rename the button
        if self.Button['text'] == 'Keyboard Mode':
            for key in self.EV_field_names:
                getattr(self,key).bind("<KeyPress>",self.keydown)
                getattr(self,key).bind("<KeyRelease>",self.keyup)
            self.Button['text'] = 'Scanner Mode'
        elif self.Button['text'] == 'Scanner Mode':
            for key in self.EV_field_names:
                getattr(self,key).bind("<KeyPress>",self.human_keydown)
                getattr(self,key).bind("<KeyRelease>",self.human_keyup)
            self.Button['text'] = 'Keyboard Mode'
    def keydown(self,e):
        try:
            self.keys[e.char].is_pressed == True
        except KeyError:
            self.keys[e.char] = Key()
        if self.keys[e.char].is_pressed == True and self.keys[e.char].widget==e.widget:
            self.keys[e.char]=Key(True,datetime.now(),e.widget,True)
            # delete last input if key is being held down.
            # i.e. this stops a user from holding down the j key
            # as a means of filling the entry with j's.
            e.widget.delete(len(e.widget.get())-1,tk.END)
        else:
            self.keys[e.char]=Key(True,datetime.now(),e.widget,False)
        return self
    def human_keydown(self,e):
        pass
    def keyup(self,e):
        # if the key is held down for too long,
        # i.e. as long as a keyboard keypress by a human takes,
        # then delete the last.
        try:
            self.keys[e.char].is_pressed == True
        except KeyError:
            self.keys[e.char] = Key()
            time.sleep(1)
        if self.keys[e.char].widget ==e.widget and (self.keys[e.char].is_being_held or (datetime.now() - self.keys[e.char].time_pressed).microseconds > 100000):
            e.widget.delete(len(e.widget.get())-1,tk.END)
        elif self.keys[e.char].is_being_held or (datetime.now() - self.keys[e.char].time_pressed).microseconds > 100000:
            self.keys[e.char].widget.delete(len(e.widget.get())-1,tk.END)
        self.keys[e.char]=Key(False)
        return self
    def human_keyup(self,e):
        pass

if __name__ == "__main__":
    #when you run the script, actually only this stuff below runs. Everything above was definitions. Within definitions you instantiate other things you've defined,
    #but its all just definitions! Up until the stuff below.
    #this first line is basic for all tkinter GUI creation. this "root" becomes "parent" in the classes defined above.
    root = tk.Tk()
    #here we set the top banner of the app. We can also mess with the geometry, etc. of the GUI by other root.[some stuff]
    root.title("Log Licenses")
    #here we instantiate the SNPK class (which itself instantiates the other classes and so on, so forth)
    #ini_section is the section that has the DB info in the .ini file
    app = BarcodeScannerMode(root,0,ini_section='local_launcher')
    #this just runs the GUI. And we're off!
    app.mainloop()
