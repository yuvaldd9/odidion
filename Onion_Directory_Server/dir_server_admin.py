import os
import ttk
import sqlite3 as lite
from Tkinter import *

ONION_ROUTERS_DB_DIR = "%s\\%s"%(os.getcwd(), "onion_routers.db")
SERVICES_DB_DIR =  "%s\\%s"%(os.getcwd(), "services.db")
VERBOSE_LOG_DIR = "%s\\%s"%(os.getcwd(), "Directory_Server_log.txt")

class AdminView:
    def __init__(self, master):
        self._showing_id = None
        self.display_db = True
        self.conn = None
        self.cursor = None

        self.db_name = {
            SERVICES_DB_DIR : 'services',
            ONION_ROUTERS_DB_DIR : 'onion_routers'
        }

        self.view_dir = ONION_ROUTERS_DB_DIR #default
        self.master = master
        master.title("ADMIN VIEW")
        
        self.admin_label = Label(master, text='ADMIN VIEW')
        self.admin_label.pack(expand="YES", fill='both')

        self.routers_table_button = Button(master, text="Onion Routers", command=self._show_onion_table)
        self.routers_table_button.pack(expand="YES", fill='both',side=TOP)

        self.services_table_button = Button(master, text="Services", command=self._show_service_table)
        self.services_table_button.pack(expand="YES", fill='both', side=TOP)

        self.log_button = Button(master, text="Log", command=self._show_log)
        self.log_button.pack(expand="YES", fill='both', side=TOP)

        self.content_frame = Frame(master)
        self.content_frame.pack(expand="YES", fill='both')
        self._set_tree()
        self.show_table()

    def connect_to_db(self):
        self.conn = lite.connect(self.view_dir)
        self.cursor = self.conn.cursor()

    def _set_tree(self):
        if self.view_dir == ONION_ROUTERS_DB_DIR:
            self.tree = ttk.Treeview(self.content_frame, column=("c1", "c2", "c3","c4","c5","c6","c7","c8"), show='headings')
            self.tree.column("#1", anchor=CENTER, width=50)
            self.tree.heading("#1", text="ID")
            self.tree.column("#2", anchor=CENTER, width=75)
            self.tree.heading("#2", text="Router Name")
            self.tree.column("#3", anchor=CENTER, width=75)
            self.tree.heading("#3", text="IP")
            self.tree.column("#4", anchor=CENTER, width=50)
            self.tree.heading("#4", text="PORT")
            self.tree.column("#5", anchor=CENTER, width=20)
            self.tree.heading("#5", text="LOAD")
            self.tree.column("#6", anchor=CENTER, width=20)
            self.tree.heading("#6", text="IS AVAILABLE")
            self.tree.column("#7", anchor=CENTER, width=100)
            self.tree.heading("#7", text="LAST SEEN")
            self.tree.column("#8", anchor=CENTER, width=50)
            self.tree.heading("#8", text="PUBLIC KEY DIR")
        else:
            self.tree = ttk.Treeview(self.content_frame, column=("c1", "c2", "c3","c4","c5","c6","c7","c8", "c8"), show='headings')
            self.tree.column("#1", anchor=CENTER, width=20)
            self.tree.heading("#1", text="ID")
            self.tree.column("#2", anchor=CENTER, width=50)
            self.tree.heading("#2", text="Service Name")
            self.tree.column("#3", anchor=CENTER, width=50)
            self.tree.heading("#3", text="Service Port")
            self.tree.column("#4", anchor=CENTER, width=50)
            self.tree.heading("#4", text="IP")
            self.tree.column("#5", anchor=CENTER, width=50)
            self.tree.heading("#5", text="REN IP")
            self.tree.column("#6", anchor=CENTER, width=50)
            self.tree.heading("#6", text="REN IP")
            self.tree.column("#7", anchor=CENTER, width=50)
            self.tree.heading("#7", text="REN NANE")
            self.tree.column("#8", anchor=CENTER, width=50)
            self.tree.heading("#8", text="SPECIAL KEY")
            self.tree.column("#9", anchor=CENTER, width=100)
            self.tree.heading("#9", text="PUBLIC KEY DIR")
            self.tree.column("#9", anchor=CENTER, width=20)
            self.tree.heading("#9", text="SERIAL NUMBER")
        self.tree.pack(expand="YES", fill='both')

    def show_table(self):
        print '[showing table]', self.view_dir
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.connect_to_db()
        self.cursor.execute("SELECT * FROM %s"%(self.db_name.get(self.view_dir)))

        rows = self.cursor.fetchall()
        self._set_tree()
        for row in rows:
            self.tree.insert("", END, values=row)
        self.conn.close()
        self._showing_id = self.content_frame.after(5000, self.show_table)
    
    def show_log_file(self):
        print '[showing log]', self.view_dir
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.list = Listbox(self.content_frame)
        with open(self.view_dir, "r") as log_file:
            lines = log_file.readlines()
            for line in lines:
                self.list.insert(END, line)
        self.list.pack(expand="YES", fill='both')
        self._showing_id = self.content_frame.after(5000, self.show_log_file)
        
    def _show_onion_table(self):
        print 'onion button'
        if not self.display_db:
            self.content_frame.after_cancel(self._showing_id)
            self.display_db = TRUE

        self.view_dir = ONION_ROUTERS_DB_DIR
        self.show_table()
    
    def _show_service_table(self):
        print 'services button'
        if not self.display_db:
            self.content_frame.after_cancel(self._showing_id)
            self.display_db = TRUE
        self.view_dir = SERVICES_DB_DIR
        self.show_table()

    def _show_log(self):
        print 'log button'
        if self.display_db:
            self.content_frame.after_cancel(self._showing_id)
            self.display_db = FALSE
        self.view_dir = VERBOSE_LOG_DIR
        self.show_log_file()

if __name__ == '__main__':
    root = Tk()
    root.geometry("1500x500")
    root.resizable(False, False)
    admin = AdminView(root)
    root.mainloop()
