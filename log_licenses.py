import tkinter as tk
from config import DBI
from tkinter import TOP,LEFT,BOTTOM,RIGHT
from dataclasses import dataclass
import psycopg2

class PK_Entries(tk.Frame):
    #this object is the product key
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent,*args,**kwargs)
        #this variable is used mroe spairingly then I origionally intended
        #I hoped to be able to define the product key row of entries
        #in a variable fashion where you can just specify how many
        #and how long they are and then that would be auto generated by the PK_Entries object but I failed to pull it off.
        self.NUM_PK_SECTIONS = 5
        #here we're creating 5 string variables
        #a string variable, as compaired to an IntVar() integer variable, contains a string
        #by assigning a string variable to an entry, any time you run:
            #x = StringVar.get(), x will be a string
        #and in order to set a StringVar to some value, you run
            #x="some string"; StringVar.set(x)
        #these particular StringVars will be assigned to entries below, where anytime StringVar.get() is run,
        #the value presently in the associated entry will be returned.
        self.PKEntry1 = tk.StringVar()
        self.PKEntry2 = tk.StringVar()
        self.PKEntry3 = tk.StringVar()
        self.PKEntry4 = tk.StringVar()
        self.PKEntry5 = tk.StringVar()
        #here we're creating the entries for the product key "cells", each one is assigned a StringVar
        self.microsoftPK1 = tk.Entry(self,fg='black',bg='white',width=6,textvariable=self.PKEntry1)
        self.microsoftPK2 = tk.Entry(self,fg='black',bg='white',width=6,textvariable=self.PKEntry2)
        self.microsoftPK3 = tk.Entry(self,fg='black',bg='white',width=6,textvariable=self.PKEntry3)
        self.microsoftPK4 = tk.Entry(self,fg='black',bg='white',width=6,textvariable=self.PKEntry4)
        self.microsoftPK5 = tk.Entry(self,fg='black',bg='white',width=6,textvariable=self.PKEntry5)
        #here we're adding a trace operation to each StringVar
        #what's going on here is that for a particular StringVar, when its length is equal to 5,
        #then the cursor (or, in computer speak, the focus) will be moved to the next entry
        self.PKEntry1.trace("w", lambda *args: self.microsoftPK2.focus() if len(self.PKEntry1.get())==5 else False)
        self.PKEntry2.trace("w", lambda *args: self.microsoftPK3.focus() if len(self.PKEntry2.get())==5 else False)
        self.PKEntry3.trace("w", lambda *args: self.microsoftPK4.focus() if len(self.PKEntry3.get())==5 else False)
        self.PKEntry4.trace("w", lambda *args: self.microsoftPK5.focus() if len(self.PKEntry4.get())==5 else False)
        #here we're packing the entries together on this PK_Entries object from left to right.
        #an alternative to .pack is .grid, where you assign a row and column (along with columnspans and rowspans) for each widget
        #(i.e. entry or label) which is used elsewhere in other apps.
        self.microsoftPK1.pack(side=LEFT)
        self.microsoftPK2.pack(side=LEFT)
        self.microsoftPK3.pack(side=LEFT)
        self.microsoftPK4.pack(side=LEFT)
        self.microsoftPK5.pack(side=LEFT)
    def clear_entries(self):
        #this method could definately be implimented better, especially if the entries in this classes __init__ were done in a loop or otherwise more generally.
        for i in range(1,self.NUM_PK_SECTIONS+1):
            if getattr(self,'microsoftPK'+str(i)).index('end') !=0:
                #clear the PK non-empty entries
                getattr(self,'microsoftPK'+str(i)).delete(0,'end')
        return self
    def get(self,punctuation):
        #Ok this next line of code is very pythonic, and an equivalent functionality could be done over many more lines of code that would do the same but more expressively
        #and thus more easily understood, but this is a good way, a pythonic way, of doing this! Ok lets break it down...
        #what this line does is take the values input into each entry of the Product Key and concatenates them as if there was just one long entry
        #the getattr function grabs from self.PK, which we instantiated the PK_Entries object as in this classes __init__ method, each entries value in PK_entries
        #recall that the entries were named "microsoftPK1","microsoftPK2",... and the .get() method retrieves the present value in each of those objects and concatenates them to
        #an initially empty string. Equivalently, I could have written:
            #pk= "".join([getattr(self.PK,'microsoftPK'+str(i)).get() for i in range(1,NUM_PK_SECTIONS+1)])
        #with the same results. Another example of the join method of string classes is the following:
            #x=["hello","world","my","name","is"]
            #y = str().join(x)
            #print(y) -> "helloworldmynameis"
            #or equivalently, y=str().join([i for i in x])
        return str(punctuation).join([getattr(self,'microsoftPK'+str(i)).get() for i in range(1,self.NUM_PK_SECTIONS+1)])
    def insert(self,PK_Entry_List):
        #set entry values in order based on a list
        #it does not clear the remaining entries if you only insert values into the first, say, three entries.
        if len(PK_Entry_List) > self.NUM_PK_SECTIONS:
            print('too many entries for form. Max Limit of {}'.format(self.NUM_PK_SECTIONS))
            maxLength=self.NUM_PK_SECTIONS
        else:
            maxLength=len(PK_Entry_List)
        for i in range(1,maxLength+1):
            getattr(self,'microsoftPK'+str(i)).insert(0,PK_Entry_List[i-1])
        return self

class SNPK(tk.Frame,DBI):
    def __init__(self,parent,*args,**kwargs):
        self.parent=parent
        tk.Frame.__init__(self,parent)
        #the above is broilerplate, you can see it in probably all the other classes that inheret from tk.Frame
        #this is just the basic way of expressing that this class is going to represent a particular frame, such as a single pop up.
        #the next line you will also see repeated, its what connects to the database based on the .ini file's username,password,database etc.
        #its inclusion allows for the use of self.fetchone() and self.insertToDB()... it assignes those "methods" to the "self" variable associated with this class
        DBI.__init__(self,ini_section=kwargs['ini_section'])
        #BEGIN STAFF DROPDOWN POPULATION
        #this line assigns to the variable getStaff the string "SELECT name from staff where active = TRUE;"
        #I just spread it out in a more structured, readable way. Line breaks, spaces, tabs. etc. are all the same to SQL.
        #SQL (Structured Query Lenguage) is best understood in terms of independent clauses that perform different tasks, for example:
            #the SELECT clause determines which columns will be returned
            #the FROM clause determines what table(s) will return columns
            #the WHERE clause takes designates a subset of the table(s) specified in the from clause
        #There are other SQL clauses, such as the ORDER BY clause and the GROUP BY clause. Google about them all! Or bing... microsoft websites are verbose on SQL info
        getStaff = \
        """
        SELECT name
        FROM staff
        WHERE active=TRUE;
        """
        #this next line uses the fetchall method from the DBI class located in the config.py file
        #it returns all the results from the query getStaff, with a simple checker that it completed successfully, as a list of tuples for each row returned
        #i.e. if my table looks like
        # name | age | gender | ...
        # joe  | 21  | male
        # sarah| 22  | female
        # ...
        #and the query is requesting name, age, and gender (and not just name as in getStaff) then the query will return
        #[('joe',21,'male'),('sarah',22,'female'),...]
        #note: if this had an insert clause instead of a select clause, i.e. it was changing data in the database instead of just getting a peak,
        #then no harm no foul using fetchall -- this is limited to only "fetching" data and does not "commit" changes to the database.
        #in order to update or insert data into the database, use the self.insertToDB() command.
        stafflist = self.fetchall(getStaff)
        #this next command downsamples the list of tuples to a list of single values, only keeping the first value of every tuple
        #so for the above example, the next line takes as input stafflist
            # [('joe',21,'male'),('sarah',22,'female'),...]
        # and returns ['joe','sarah',...] as snames
        snames =[staff[0] for staff in stafflist]
        #this next command creates a StringVar and assigns it an initial value "staff:"
        #NOTE:
            #the self. at the beginning of the variable (i.e. "self.staffName" instead of just "staffName")
            #allows this variable to be accessable, to live on, if you will, in other methods of this SNPK class.
        #In other words, snames cannot be accessed in the method insertSNPK but self.staffName can be.
        #snames gets destroyed once all the lines of code  in the __init__ method have been executed
        #self.staffName lingers until the object is destroyed!
        #In more low level programming lenguages such as C++ you have to handle class destruction, but python handles that for you.
        #so only concern youself with "what can see what where?" and note that no self.
        #in front of a variable means this variable cannot be accessed outside its the method its created inside of.
        self.staffName = tk.StringVar(parent,value="staff:")
        tk.OptionMenu(parent,self.staffName,"staff:",*snames).pack()
        #END STAFF DROPDOWN POPULATION
        #the next two lines creates the label and entry for the serialNumber and then pack them onto the objects frame.
        tk.Label(parent,text="Microsoft SN:").pack()
        self.serialNumber = tk.Entry(parent,fg='black',bg='white',width=20)
        self.serialNumber.pack()
        #the next few lines create and instantiate the product key label and entries, and then pack them.
        tk.Label(parent,text="Microsoft PK").pack()
        self.PK = PK_Entries(parent)
        self.PK.pack()
        #th next few lines create the botton and assign a method to run when the button is clicked,
        #the button itself is then packed on.
        self.submitSNPK = tk.Button(parent,
            text='submit',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.submitSNPK.bind('<Button-1>',self.insertSNPK)
        self.submitSNPK.pack()
        #the next variable can be used to keep track of the license table's serial row counter
        #not currently in use
        self.last_license_id=None
        #the next 2 lines of code create a StringVar and assign in to a label.
        #this particular string var will serve as the place where error messages are returned to the app user.
        self.err = tk.StringVar(parent)
        tk.Label(parent,textvariable=self.err).pack()
        #the next two StringVars will hold the last submitted SN and PK for form repululation and PK updating.
        self.last_SN = tk.StringVar(parent)
        self.last_PK=tk.StringVar(parent)
        #These next 4 labels lack labels and, like the error label, are associated with the StringVars showing the last submitted SN and PK for review
        tk.Label(parent,text='last SN:').pack()
        tk.Label(parent,textvariable=self.last_SN).pack()
        tk.Label(parent,text='last PK:').pack()
        tk.Label(parent,textvariable=self.last_PK).pack()
        #here we're creating the button that will trigger the retrieve_last_entry method which repopulates the form.
        self.retrieveLast = tk.Button(parent,
            text='retrieve Last',
            width = 15,
            height = 2,
            bg = "blue",
            fg = "yellow",
        )
        self.retrieveLast.bind('<Button-1>',self.retrieve_last_entry)
        self.retrieveLast.pack()
        #this variable is used to initialize the trigger that throws the pop up.
        self.last_entry_update=False

    def insertSNPK(self,event):
        #this code section (function) runs when the submit button is clicked
        if self.last_entry_update is True:
            #this code indented from this if statement trigger the throwing of the pop up
            pop_up = tk.Toplevel(self.parent)
            UpdateVsSubmission(pop_up)
            self.last_entry_update=False
        #this next line of code retrieves into a variable the present value of the staff string var.
        staff = self.staffName.get()
        #recall that this StringVar was given the inital value "staff:" so this if statement checks if a staff was chosen (bescides the initial value!)
        if staff == "staff:":
            self.err.set('please select staff member')\
            #return self basically means do nothing else in this method. you'll be seeing a lot of "return self"
            return self
        #returns entries punctuated via the input "punctuation"
        #set punctuation = "" to use no punctuation and return entries as if it were from one long intry instead of 5 short ones.
        pk = self.PK.get("")
        #this next statement does the same thing, but sticks hyphens (-) inbetween each string element its concatenating
        last_pk = self.PK.get("-")
        #now we get the SN from the stringvar into a var
        if self.serialNumber.index('end') !=0:
            sn=self.serialNumber.get()
        else:
            sn = None
            self.err.set("Please enter a serial number.")
            return self
        #the next line of code is executed everytime the submit button is pressed and the if statements above
        #have not been triggered to stop the program by including a "return self" line.
        #first, I use a with statement to insert the user inputs into a tempory table that will be destroyed momentarily.
        #I then insert into the licenses table the serialNumber, productkey and staff_id (which references the staff table)
        #finally, it returns the license id associated with the new row or updated old row.
        insert_snpk = \
        """
        WITH inputs as (SELECT TRIM(LOWER(%s)) as sn, TRIM(LOWER(%s)) as pk, (SELECT s.staff_id FROM staff s where s.name = %s) as s_id)
        INSERT INTO licenses(
            serialNumber,productKey,staff_id,entry_time)
        VALUES(
            (SELECT sn from inputs),
            (SELECT pk from inputs),
            (SELECT s_id from inputs),
            NOW())
        ON CONFLICT (serialnumber) DO UPDATE
            SET productkey = (select pk from inputs),
            staff_id = (SELECT s_id from inputs)
        RETURNING license_id
        ;
        """
        back=None
        try:
            back = self.insertToDB(insert_snpk,sn,pk,staff)
            #set err to display the row effected by the insert operation above
            #or the error message
            self.err.set("success! "+ str(back))
            #check if a value is input for the serial number
            self._clear_form()
            self.last_SN.set(sn)
            self.last_PK.set(last_pk)
            self.last_license_id=back[0]
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            self.err.set(error)
        finally:
            if back is not None:
                print(back,' <<- row addressed')
            else:
                print('Database connection or SQL execution script fail.')
            return self

    def retrieve_last_entry(self,event):
        #this method is activated when the retrieve button is clicked.
        #first, it clears the form,
        self._clear_form()
        #second, it inserts into the serial number entry, the value cashed as the last_SN variable.
        #it does this by getting the value and inserting into the beginning of the entry (place 0)
        self.serialNumber.insert(0,self.last_SN.get())
        #third, it gets the last_pk which is a hyphen-delimited string displayed on the apps GUI (graphical user interface)
        #and returns this value as a list of strings where the hyphens designate where one sting ends and the other begins.
        pk = self.last_PK.get().split('-')
        #here we insert the list of PK entries into the PK entries
        #see the PK_Entries class "insert" method
        self.PK.insert(pk)
        self.last_entry_update=True
    def _clear_form(self):
        #this function clears the single SN and all the PK entries
        if self.serialNumber.index('end') !=0:
            self.serialNumber.delete(0,'end')
        #see the PK_Entries class for the implimentation of this method.
        self.PK.clear_entries()

class UpdateVsSubmission(tk.Frame):
    #this object is the checker of the incorrect submit click. will pop up when submit is clicked after a form repopulation
    #its pretty lame, but could be a place holder/idea for something else if you've any ideas!
    #it serves as a good example of a frame object, which is used for  pop ups and for subsets of other frames, like the PK entries frame.
    def __init__(self,parent,*args,**kwargs):
        tk.Frame.__init__(self,parent)
        tk.Label(parent,text='It appears you repopulated the form with the last submission').pack()
        tk.Label(parent,text='Note that I proceeded to update the PK if the SN was the same as a previous submission').pack()
def main():
    #when you run the script, actually only this stuff below runs. Everything above was definitions. Within definitions you instantiate other things you've defined,
    #but its all just definitions! Up until the stuff below.
    #this first line is basic for all tkinter GUI creation. this "root" becomes "parent" in the classes defined above.
    root = tk.Tk()
    #here we set the top banner of the app. We can also mess with the geometry, etc. of the GUI by other root.[some stuff]
    root.title("Log Licenses")
    #here we instantiate the SNPK class (which itself instantiates the other classes and so on, so forth)
    #ini_section is the section that has the DB info in the .ini file
    app = SNPK(root,ini_section='appendage')
    #this just runs the GUI. And we're off!
    app.mainloop()
if __name__ == "__main__":
    main()
