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
import os, sys
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
    VB.print_data('[Creating / Connecting to the Databases]', VB.GENERAL_DATA)
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



#handle communication - START
def handle_communication(sock, addr):
    global HANDLE_JSON, BUFSIZ

    create_json = json_odidion_support.create_json
    #try:
    while 1:
        data = sock.recv(BUFSIZ)
        if not data:
            VB.print_data( str(("ending communication with",addr)), VB.COMM_UPDATES)
            break
        VB.print_data(  "Recieved Message From %s"%(addr,), VB.COMM_UPDATES)
        recieved_msg = eval(json.dumps(json.loads(data)))
        json_code , state, args = HANDLE_JSON[recieved_msg["type"]](recieved_msg)
        response = create_json(json_code , state, args)
        
        sock.send(response)
    #except: 
    #   VB.print_data(  "[handle communication] - Error occured!, VB.ERRORS)"
        
   


#handle communication - END

create_databases()

HANDLE_JSON = {
    ONION_ROUTER_MSG_TYPE : handle_handshakes.handle_router,
    SERVICE_MSG_TYPE : handle_handshakes.handle_service,
    CLIENT_MSG_TYPE : handle_handshakes.handle_client
}
#communications:

VB.set_level(int(sys.argv[1]))

BUFSIZ = 4096
HOST = '10.0.0.7'#'192.168.1.22' #'192.168.43.207' #'10.0.0.5'

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
    VB.print_data('[waiting for connection from clients\ new registers]', VB.GENERAL_DATA)
    clientsock, addr = main_sock.accept()
    VB.print_data(str((addr,clientsock, '[connected]')), VB.GENERAL_DATA)
    thread.start_new_thread(handle_communication, (clientsock, addr))