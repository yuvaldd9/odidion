import database_handler as db


class onion_router:
    
    def __init__(self, router_name, ip, port,db_dir, public_key_dir ,last_seen, is_exist_in_database, services = None):
        #services <---> array of (name , ip,port, communication_type) - the router is the ren point of the services
        self.router_name = router_name
        self.ip = ip
        self.load = 0
        self.is_available = True
        self.port = port
        self.last_seen = last_seen
        self.db_dir = db_dir
        self.services = services
        self.public_key_dir = public_key_dir
        if is_exist_in_database:
            self.service = (db.get_data(self.db_dir,"SELECT service_str from onion_routers WHERE router_name = %s"%(self.router_name,)))
            print 'updating data for %s router'%(self.router_name,)
            print db.set_data(self.db_dir, '''UPDATE onion_routers SET ip = \'%s\', port = \'%s\', is_available = \'%s\', last_seen = \'%s\', service_str =  \'%s\'\
                                        WHERE router_name = \'%s\''''%(self.ip, self.port, int(self.is_available),self.last_seen, self.router_name, self.services_to_str(self.services)))
        else:
            print 'new router added to the database'
            print db.set_data(self.db_dir, '''INSERT INTO onion_routers(router_name, ip, port, load, is_available,last_seen,public_key_dir, service_str)\
                                    VALUES(?,?,?,?,?,?,?,?)''', args = (self.router_name, self.ip, self.port, self.load, int(self.is_available), str(self.last_seen), self.public_key_dir ,self.services_to_str(self.services)))
    def get_name(self):
        return self.router_name
    def get_load_level(self):
        return self.load   
    def refresh_last_seen(self, time):
        self.last_seen = time
        return db.set_data(self.db_dir, str('''UPDATE onion_routers SET last_seen = \'%s\' WHERE router_name = \'%s\' '''%( str(self.last_seen), self.router_name)))
    def get_router_data(self):
        return {
            "router name" : self.router_name,
            "ip" : self.ip,
            "port": self.port,
            "public key" : self.get_public_key()
        }
    def close_router(self):
        self.is_available = 0
        return db.set_data(self.db_dir, str('''UPDATE onion_routers SET last_seen = \'%s\', is_available = '0' WHERE router_name = \'%s\' '''%( str(self.last_seen), self.router_name)))
    def get_ip(self):
        return self.ip
    def add_service(self, service_details):
        self.services.append(service_details)
        db.set_data(self.db_dir, "UPDATE onion_routers SET service_str = \'%s'\ WHERE router_name = \'%s\'"%(self.services_to_str(services), self.router_name))       
    def services_to_str(self,services):
        """
        convert the service array to string in order to save it in the database
        """
        if services:
            return "%".join(map(lambda s: (repr(s)), services))
        return "None"
    def str_to_services(self,services_str):
        if services_str != "None":
            return map(lambda service_details: tuple(service_details),services_str.split('%'))
        return []
    def get_router_services(self):
        return self.services
class service:
    def __init__(self, service_name, ip, ren_ip, ren_name, port, communication_type,public_key_dir, db_dir, is_new):
        #communication type = UDP = 0 or TCP = 1
        self.service_name = service_name
        self.ip = ip
        self.ren_ip = ren_ip
        self.port = port 
        self.public_key_dir = public_key_dir
        self.db_dir = db_dir
        self.communication_type = communication_type
        self.ren_name = ren_name
        if is_new:
            print "[SERVICES] adding the service to database"
            print db.set_data(self.db_dir, '''INSERT INTO services(service_name , service_port ,ip, ren_ip , ren_name, communication_type ,public_key_dir) VALUES(?,?,?,?,?,?,?)'''
                            , args = (self.service_name, self.port, self.ip, self.ren_ip, self.ren_name ,self.communication_type,self.public_key_dir))
        else:
            print 'updating data for %s router'%(self.service_name,)
            print db.set_data(self.db_dir, '''UPDATE services SET ip = \'%s\', port = \'%s\', communication_type = \'%s\, ren_ip =  \'%s\'
                                        WHERE router_name = \'%s\'\
                                        '''%(self.ip, self.port, self.communication_type, self.ren_ip, self.ren_name))
    def __repr__(self):
        """
        (name , ip,port, communication_type)
        """
        return str((self.service_name, self.ip, self.port, self.communication_type))
