import database_handler as db
import json
from global_variables import *

class service:
    db_dir = SERVICES_DB_DIR
    def __init__(self, service_details ,ren_details, is_new = True):
        #communication type = UDP = 0 or TCP = 1
        
        self.service_name = service_details["service_name"]
        self.ip = service_details["ip"]
        self.port = service_details["port"] 
        self.public_key_dir = service_details["public_key_dir"]
        self.communication_type = service_details["communication_type"]
        
        self.ren_name = ren_details["ren_name"]
        self.ren_ip = ren_details["ren_ip"]

        
        if is_new:
            print "[SERVICES] adding the service to database"
            print db.set_data(service.db_dir, '''INSERT INTO services(service_name , service_port ,ip, ren_ip , ren_name, communication_type ,public_key_dir) VALUES(?,?,?,?,?,?,?)'''
                            , args = (self.service_name, self.port, self.ip, self.ren_ip, self.ren_name ,self.communication_type,self.public_key_dir))
        else:
            print 'updating data for %s router'%(self.service_name,)
            print db.set_data(service.db_dir, '''UPDATE services SET ip = \'%s\', port = \'%s\', communication_type = \'%s\, ren_ip =  \'%s\'
                                        WHERE service_name = \'%s\'\
                                        '''%(self.ip, self.port, self.communication_type, self.ren_ip, self.ren_name, self.service_name))
    def get_details(self):
        """
        (name , ip,port, communication_type)
        """
        return {
            "service_name" : self.service_name,
            "service_port" : self.port,
            "service_ip" : self.ip,
            "service_communication_type" : self.communication_type
        }
    def get_name(self):
        return self.service_name