import database_handler as db
import json
from global_variables import *

class service:
    db_dir = SERVICES_DB_DIR
    def __init__(self, service_details ,ren_details,is_new = True):
        #communication type = UDP = 0 or TCP = 1
        
        self.service_name = service_details["service_name"]
        self.ip = service_details["ip"]
        self.port = service_details["port"] 
        self.public_key_dir = service_details["public_key_dir"]
        self.communication_type = service_details["communication_type"]
        self.serial_number = 0

        self.ren_name = ren_details["ren_name"]
        self.ren_ip = ren_details["ren_ip"]

        
        if is_new:
            VB.print_data( "[SERVICES] adding the service to database", VB.GENERAL_DATA)
            VB.print_data(db.set_data(service.db_dir, '''INSERT INTO services(service_name , service_port ,ip, ren_ip , ren_name, communication_type ,public_key_dir, serial_number) VALUES(?,?,?,?,?,?,?,?)'''
                            , args = (self.service_name, self.port, self.ip, self.ren_ip, self.ren_name ,self.communication_type,self.public_key_dir, self.serial_number)), VB.GENERAL_DATA)
        else:
            VB.print_data('updating data for %s router'%(self.service_name,), VB.GENERAL_DATA)
            VB.print_data(db.set_data(service.db_dir, '''UPDATE services SET ip = \'%s\', port = \'%s\', communication_type = \'%s\, ren_ip =  \'%s\'
                                        WHERE service_name = \'%s\'\
                                        '''%(self.ip, self.port, self.communication_type, self.ren_ip, self.ren_name, self.service_name)), VB.GENERAL_DATA)
    def add_serial_number(self, serial_num):
        self.serial_number = serial_num
        VB.print_data(db.set_data(service.db_dir, '''UPDATE services SET serial_number = \'%s\' WHERE service_name = \'%s\''''%(self.serial_number, self.service_name)), VB.GENERAL_DATA)

    def get_details(self):
        """
        (name , ip,port, communication_type)
        """
        return {
            "service_name" : self.service_name,
            "service_port" : self.port,
            "service_ip" : self.ip,
            "service_communication_type" : self.communication_type,
            "serial_number" : self.serial_number
        }
    def get_name(self):
        return self.service_name