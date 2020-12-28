"""
Author: Yuval Didi

Directory Server

Manage the onion routers and the services in the net.

load levels: according to the num of the client
"""
from global_variables import *
from json_codes import *
import keep_alive_handler
import handle_handshakes
import database_handler as db
from socket import *
import thread
import time
from onion_router_class import *
import os
import random
import json
import json_odidion_support
#create/ connect to the databases - START
#onion_db -> the ip, name, load of any onion router in the net
#services_db -> manage the services, url,ren ip....
def create_databases():
    """
    create the databases if there are not exist
    """
    print '[Creating / Connecting to the Databases]'
    global ONION_ROUTERS_DB_DIR, SERVICES_DB_DIR
    if not os.path.exists(ONION_ROUTERS_DB_DIR):
        db.connect_dataBase(ONION_ROUTERS_DB_DIR, '''CREATE TABLE onion_routers(\
                                                                id INTEGER PRIMARY KEY, router_name TEXT,\
                                                                ip TEXT, port INTEGER ,load INTEGER, is_available INTEGER, last_seen TEXT,
                                                                public_key_dir TEXT, service_str INTEGER)''')
    if  not os.path.exists(SERVICES_DB_DIR):
        db.connect_dataBase(SERVICES_DB_DIR, '''CREATE TABLE services(id INTEGER PRIMARY KEY, service_name TEXT,
                                                service_port TEXT ,ip TEXT, ren_ip TEXT, ren_name TEXT, communication_type INTEGER, public_key_dir TEXT, serial_number TEXT)''')
    return True
#create/ connect to the databases - end


#handle database - START
def closed_router(router_name):
    """
    this func updates the database
    and delete from the dynamic variables
    the router
    """
    global LAST_SEEN
    global CONNECTED_ROUTERS

    del LAST_SEEN[router_name]
    CONNECTED_ROUTERS[router_name][0].close_router()
    del CONNECTED_ROUTERS[router_name]
    print '[DATA UPDATE] delted and update %s details'%(router_name,)

def is_router_exist(router_name):
    """
    return true if the router is written in the routers database and false if not
    """
    print '[Checking if %s in the routers database]'%(router_name,)
    global ONION_ROUTERS_DB
    routers =  db.get_data(ONION_ROUTERS_DB_DIR,'''SELECT * from onion_routers''')
    for router in routers:
        if router[1] == router_name:
            return True
    return False

def add_connected_router(router_name, routersock, addr, clients_port,public_key):
    """
    the server adds the router to his list, 
    the handshake progress is done!
    """
    global LAST_SEEN
    global CONNECTED_ROUTERS
    global ONION_ROUTERS_DB_DIR

    print '[Adding Onion Router:%s:To The System]'%(router_name,)

    last_seen = time.time() 
    public_key_dir = save_pukey(router_name, public_key)   
    new_router = onion_router(router_name ,addr[0], clients_port, ONION_ROUTERS_DB_DIR, public_key_dir, last_seen,is_router_exist(router_name))
    CONNECTED_ROUTERS[router_name] = (new_router, routersock)
    LAST_SEEN[router_name] = last_seen
    public_key_dir = save_pukey(router_name, public_key)

def refresh_router(router_name, load_level):
    """
    refresh the data structures of the server - last seens
    """
    print '[%s sent Live Nofitication]'%(router_name)
    print '[UPDATE LEVEL_LOAD] %s'%(db.set_data(ONION_ROUTERS_DB_DIR, '''UPDATE onion_routers SET load = %s, '''%(load_level)))
    last_seen = time.time()
    LAST_SEEN[router_name] = last_seen
    CONNECTED_ROUTERS[router_name][0].refresh_last_seen(last_seen)
    
def get_service(service_name):
    """
    returns the service details(ip) and the relavent routers
    """
    global SERVICES_DB_DIR

    service_details = db.get_data(SERVICES_DB_DIR, '''SELECT ren_ip, ren_name, communication_type, public_key_dir from services WHERE service_name = \'%s\''''%service_name)[0]

    service_data = {}
    service_public_key = get_public_key(service_details[3])
    if not service_public_key:
          return {}
    service_data["service_public_key"] = service_public_key.encode('utf-8')
    service_data["communication_type"] = service_details[2]
    service_data["routers"] = choose_routers(service_details[1])
    
    print service_data
    print '---LOVELy---'

    return service_data

def choose_routers(ren_name):
    """
    this func return the current most available routers
    return an array of the objects.
    """
    global ONION_ROUTERS_DB_DIR
    routers = db.get_data(ONION_ROUTERS_DB_DIR, '''SELECT router_name, ip, port, load, public_key_dir from onion_routers''')
    print routers

    clients_routers = {'3' : filter(lambda details: details[0] == ren_name, routers)[0]}
    routers.remove(clients_routers['3'])

    most_availables_routers = sorted(routers, key = lambda details: details[3])
    clients_routers['1'] = most_availables_routers[0]
    clients_routers['2'] = most_availables_routers[1]

    for key in clients_routers.keys():
        clients_routers[key] = (clients_routers[key][0].encode('utf-8'), clients_routers[key][1].encode('utf-8'),\
                                         clients_routers[key][2], get_public_key(clients_routers[key][4].encode('utf-8')))


    print clients_routers
    return clients_routers
    



def choose_ren_point():
    """
    returns the ren point to the new service
    """
    global CONNECTED_ROUTERS
    return CONNECTED_ROUTERS[random.choice((CONNECTED_ROUTERS.keys()))][0] #temp solution

def save_pukey(name, public_key):
    """
    SAVES THe public key to .pem file
    """
    
    pukey_dir = "%s\keys\%s.pem"%(os.getcwd(), name)
    try:
        public_key_file = open((pukey_dir),'wb')
        public_key_file.write(public_key)
        public_key_file.close()
        return pukey_dir
    except:
        return ''
    
def get_public_key(key_path):
    print 'taking the f key'
    try:
        with open(key_path, 'r') as f:
            key = f.read()
        return key
    except:
        return '' 

def add_service(service_details):
    """
    adds the services to the databases
    service_details = name, ip, port, type, public key
    """
    global SERVICES_DB_DIR
    global SERVICES_UPDATES
    ren_obj = choose_ren_point()
    details = {
        "service_name" : service_details[0],
        "ip" : service_details[1],
        "port" : service_details[2],
        "communication_type" : service_details[3],
        "public_key_dir" : save_pukey(service_details[0], service_details[4]),
        "ren_ip" : ren_obj.get_ip(),
        "ren_name" : ren_obj.get_name()
    }

    print details
    new_service = service(details["service_name"], details["ip"], details["ren_ip"], details["ren_name"] ,details["port"], details["communication_type"]\
                                , details["public_key_dir"], SERVICES_DB_DIR, True) #is new is temp solution for the POC 
    SERVICES_UPDATES[ren_obj.get_name()] = repr(new_service)#in the keep alive protocol the relevant routers will get the updates
    """
    check if the service is exist in the database
    """
    return "k"
    


#handle database - END

#handle communication - START
def handle_communication(sock, addr):
    global HANDLE_JSON, BUFSIZ

    create_json = json_odidion_support.create_json
    try:
        while 1:
            data = sock.recv(BUFSIZ)
            if not data:
                print "ending communication with",addr
                break
            print '------------',addr,'--------------'
            print data
            print '------------',addr,'--------------'
            recieved_msg = eval(json.dumps(json.loads(data)))
            #print (recieved_msg)
            json_code , state, args = HANDLE_JSON[recieved_msg["type"]](recieved_msg)
            response = create_json(json_code , state, args)
            #print response
            
            sock.send(response)
    except: 
        print "[handle communication] - Error occured!"
        
   


#handle communication - END

create_databases()

HANDLE_JSON = {
    ONION_ROUTER_MSG_TYPE : handle_handshakes.handle_router,
    SERVICE_MSG_TYPE : handle_handshakes.handle_service,
    CLIENT_MSG_TYPE : handle_handshakes.handle_client
}
#communications:

BUFSIZ = 4096
HOST = '10.0.0.3'#'192.168.1.22' #'192.168.43.207' #'10.0.0.5'

PORT = 50010
ADDR = (HOST, PORT)
main_sock = socket(AF_INET, SOCK_STREAM)
main_sock.bind(ADDR)
main_sock.listen(2)

#for the clients
while True:
    """
    this loop is waiting both for clients and service(because of the lack of communication with the directory server)
    """
    print '[waiting for connection from clients\ new registers]'
    clientsock, addr = main_sock.accept()
    print addr,clientsock, '[connected]'
    thread.start_new_thread(handle_communication, (clientsock, addr))