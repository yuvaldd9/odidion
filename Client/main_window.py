from Tkinter import *
import client
import thread
class main_window:

    def _run(self):
        self.root.mainloop()
    def connected_to_network(self):
        self.client_handle.ask_to_service(self.url_entry.get())

    def _handle_comm(self):
        self.client_handle.DATA_TO_SEND.append(self.msg_enrty.get())
        for recieved_data in self.client_handle.session():
            self.data_recieved_label[Text] = recieved_data
        


        
    def __init__(self):
        self.root = Tk()
        self.in_session = False
        self.client_handle = client.client()
    
        self.welocme_label = Label(self.root, text = "WELCOME ERAN")
        self.url_entry = Entry(self.root, text = "URL HERE")
        self.connect_button = Button(self.root, text = "Connect To Service", command = self.connected_to_network)
        self.send_button = Button(self.root, text = "send", command = self._handle_comm)
        self.msg_enrty = Entry(self.root, text = "DATA TO SEND HERE")
        self.data_recieved_label = Label(self.root, text = "DATA HERE")

        self.welocme_label.pack()
        self.url_entry.pack()
        self.connect_button.pack()
        self.send_button.pack()
        self.msg_enrty.pack()
        self.data_recieved_label.pack()
        
        self._run()

    def _run(self):
        self.root.mainloop()
    def connected_to_network(self):
        self.client_handle.ask_to_service(self.url_entry.get())
    def _handle_session(self,i):
        for recieved_data in self.client_handle.session():
            print recieved_data
            if recieved_data == -1:
                break
            else:
                self.data_recieved_label['text'] = str(recieved_data)
    def _handle_comm(self):
        if not self.in_session:
            thread.start_new_thread(self._handle_session,(None, ) )
            self.in_session = True
        self.client_handle.DATA_TO_SEND.append(self.msg_enrty.get())
        
        


        
