import database_handler as db
import time
from global_variables import *
import onion_encryption_decryption
class onion_router:
    db_dir = ONION_ROUTERS_DB_DIR
    #router_name, ip, port, public_key_dir
    def __init__(self, router_details):
        #services <---> array of (name , ip,port, communication_type) - the router is the ren point of the services
        self.router_name = router_details["router_name"]
        self.ip = router_details["ip"]
        self.load = 0
        self.is_available = True
        self.port = router_details["port"]
        self.last_seen = time.time()
        self.public_key_dir = router_details["public_key_dir"]
        self.is_exist_in_database = False
        if self.is_exist_in_database:
            self.service = (db.get_data(onion_router.db_dir,"SELECT service_str from onion_routers WHERE router_name = %s"%(self.router_name,)))
            #print 'updating data for %s router'%(self.router_name,)
            VB.print_data(db.set_data(onion_router.db_dir, '''UPDATE onion_routers SET ip = \'%s\', port = \'%s\', is_available = \'%s\', last_seen = \'%s\', service_str =  \'%s\'\
                                        WHERE router_name = \'%s\''''%(self.ip, self.port, int(self.is_available),self.last_seen, self.router_name, self.services_to_str(self.services))), VB.GENERAL_DATA)
        else:
            #print 'new router added to the database'
            self.services = None
            VB.print_data(db.set_data(onion_router.db_dir, '''INSERT INTO onion_routers(router_name, ip, port, load, is_available,last_seen,public_key_dir, service_str)\
                                    VALUES(?,?,?,?,?,?,?,?)''', args = (self.router_name, self.ip, self.port, self.load, int(self.is_available), str(self.last_seen), self.public_key_dir ,self.services_to_str(self.services))), VB.GENERAL_DATA)
            
    def __is_router_exist(router_name):
        """
        return true if the router is written in the routers database and false if not
        """
        #print '[Checking if %s in the routers database]'%(router_name,)
        routers =  db.get_data(onion_router.db_dir,'''SELECT * from onion_routers''')
        for router in routers:
            if router[1] == router_name:
                return True
        return False
    def get_name(self):
        return self.router_name
    def get_load_level(self):
        return self.load   
    def refresh_last_seen(self, load):
        self.last_seen = time.time()
        return db.set_data(onion_router.db_dir, str('''UPDATE onion_routers SET last_seen = \'%s\', load = \'%s\' WHERE router_name = \'%s\' '''%( str(self.last_seen), load,self.router_name)))
    def get_router_data(self):
        return {
            "router name" : self.router_name,
            "ip" : self.ip,
            "port": self.port,
            "public key" : self.get_public_key()
        }
    def close_router(self):
        self.is_available = 0
        return db.set_data(onion_router.db_dir, str('''UPDATE onion_routers SET last_seen = \'%s\', is_available = '0' WHERE router_name = \'%s\' '''%( str(self.last_seen), self.router_name)))
    def get_ip(self):
        return self.ip
    def add_service(self, service_details):
        self.services.append(service_details)
        db.set_data(onion_router.db_dir, "UPDATE onion_routers SET service_str = \'%s'\ WHERE router_name = \'%s\'"%(self.services_to_str(services), self.router_name))       
    def services_to_str(self,services):
        """
        convert the service array to string in order to save it in the database
        """
        if services:
            return "%".join(map(lambda s: str(s.get_details()), services))
        return "None"
    def str_to_services(self,services_str):
        if services_str != "None":
            return map(lambda service_details: eval(service_details),services_str.split('%'))
        return []
    def get_router_services(self):
        return self.services
    def get_public_key(self):
        return onion_encryption_decryption.get_public_key(self.public_key_dir)