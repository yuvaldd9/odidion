from scapy.all import *
import socket
import thread
import sys , os
import time
import database_handler as db
import onion_encryption_decryption
import json_handler
import json
import re
import verbose 


def create_databases():
    """
    create the databases if there are not exist
    {service_name, ip, port, communication_type}
    """
    global SERVICES_DB_DIR
    if not os.path.exists(SERVICES_DB_DIR):
        return db.connect_dataBase(SERVICES_DB_DIR, '''CREATE TABLE services( id INTEGER PRIMARY KEY, service_name TEXT,\
                                                                ip TEXT, port TEXT ,communication_type TEXT)''')
    return False
                            
#DATABASE - END
#server - router - communication - START
def connect_to_network(server_sock):
    """
    handling the connection handshake between the dir server and the router
    """
    global ROUTER_NAME, PUBLIC_KEY, CLIENTS_PORT
    onion_router_details = {
        "router_name" : ROUTER_NAME,
        "ip" : DIR_SERVER_IP,
        "public_key" : PUBLIC_KEY,
        "port" : CLIENTS_PORT
    }
    connect_req = json_handler.create_json(json_handler.ONION_ROUTER_REGISTER, onion_router_details)
    server_sock.send(connect_req)
    while 1:
        data = server_sock.recv(BUFSIZ)
        if not data:
            VB.print_data("ending communication with the server", VB.ERRORS, verbose_level)
            break
        data = json.loads(data)
        if data["state"] == json_handler.STATE_SUCCEED:
            return True
        elif data["state"] == json_handler.STATE_FAILED:
            return False
        else:
            server_sock.send(connect_req)
    return False


def add_service(service_details):
    global SERVICES_DB_DIR 
    global SERVICES
    global SERIAL_NUM_SERVICES

    upload_done = db.set_data(SERVICES_DB_DIR, '''INSERT INTO services(service_name, ip, port, communication_type) VALUES(?,?,?,?)''',\
            args= (service_details["service_name"], service_details["service_ip"], service_details["service_port"], service_details["service_communication_type"]))
    if upload_done:
        VB.print_data("SERVICE UPLOADED SUCCESSFULLY", VB.GENERAL_DATA, VERBOSE_LEVEL)

    SERVICES[SERIAL_NUM_SERVICES] = (service_details)#list only for eran's even derach
    return SERIAL_NUM_SERVICES

def handle_keep_alive(server_sock):
    """
    handle the keep alive connection between the server
    """
    #print server_sock.stillconnected()
    global LOAD_LEVEL, ROUTER_NAME, SERIAL_NUM_SERVICES
    keep_alive_details = {
        "load" : LOAD_LEVEL,
        "router_name" : ROUTER_NAME
    }
    while 1:
        try:        

            msg = json_handler.create_json(json_handler.ONION_ROUTER_KEEP_ALIVE, keep_alive_details)

            server_sock.send(msg)
            d = server_sock.recv(BUFSIZ)

            data = json_handler.recieve_json(d)
            

            VB.print_data("RECIEVED KEEP ALIVE MSG", VB.SESSION_DATA, VERBOSE_LEVEL)

            if not data:
                break
            elif "new_service" in data["args"].keys():
                keep_alive_details["service_added"] = (add_service(data["args"]["new_service"]))
                SERIAL_NUM_SERVICES += 1
            else:
                if "service_added" in keep_alive_details.keys():
                    del keep_alive_details["service_added"]

            time.sleep(5)
        except Exception as e:
            VB.print_data(e, VB.ERRORS, VERBOSE_LEVEL)
            break

def send_to_service(data, src, sport):
    global ROUTING_PROCESSES

    service_details = data.split(':',2)
    service_name, id_key, service_data = int(service_details[0]), service_details[1], service_details[2]
    
    ROUTING_PROCESSES[id_key] = {
                'ip' : src,
                'port' : sport
            }
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', CLIENTS_PORT))
    sock.sendto(service_data, (SERVICES[service_name]["service_ip"], int(SERVICES[service_name]["service_port"])))
    
    
def handle_packet(onion_pkt):
    global PRIVATE_KEY
    global ROUTING_PROCESSES
    global CLIENTS_PORT
    seperator = (':')
    if onion_pkt[0][2].dport == CLIENTS_PORT:
        udp_data = onion_pkt[UDP].payload.build()
        onion_pkt.display()
        #try:
        pkt_purpose = onion_pkt[0][IP].tos
        if pkt_purpose == 0:
            
            VB.print_data('----RECIEVED PACKET TO NEXT NODE----', VB.PKTS_DATA, VERBOSE_LEVEL)
            
            seperator_index = udp_data.index(seperator)
            id_key = udp_data[:seperator_index]
            key_comm_header = udp_data[seperator_index+1:seperator_index +1+ onion_encryption_decryption.KEYS_LEN]
            dec_sym_key = onion_encryption_decryption.RSA_Decryption(key_comm_header,PRIVATE_KEY)[:-1]# the slicing may change because the len analyzing(in the future)
            comm_type = dec_sym_key[len(dec_sym_key)-1:] #for the comm handler(after the poc)
            
            encrypted_pkt = bytes(udp_data[seperator_index +1+ onion_encryption_decryption.KEYS_LEN:])
            
            next_pkt = IP(onion_encryption_decryption.sym_decryption(encrypted_pkt,dec_sym_key))

           
            ROUTING_PROCESSES[id_key] = {
                'ip' : onion_pkt[0][IP].src,
                'port' : onion_pkt[0][UDP].sport
            }
            
            send(next_pkt)

            #except Exception as e:
        elif pkt_purpose == 1:
            VB.print_data('----RECIEVED PACKET TO SERVICE----', VB.PKTS_DATA, VERBOSE_LEVEL)
            
            encrypted_data = bytes(udp_data[onion_encryption_decryption.KEYS_LEN:])
            send_to_service(udp_data, onion_pkt[0][1].src, onion_pkt[0][1].sport)
        elif pkt_purpose == 2:
            VB.print_data('----RECIEVED PACKET TO CLIENT----', VB.PKTS_DATA, VERBOSE_LEVEL)
            
            seperator_index = udp_data.index(seperator)
            id_key = udp_data[:seperator_index]
            
            client_data = bytes(udp_data[seperator_index +1:])
            
            next_pkt = IP(dst = ROUTING_PROCESSES[id_key]['ip'], tos = 2)/UDP(dport = ROUTING_PROCESSES[id_key]['port'])/Raw(load = id_key + ':' + client_data)

            send(next_pkt)

            


#onion routing vars - Start
LOAD_LEVEL = 0
ROUTING_PROCESSES = {} #(src_ip, dst_ip, comm_type)
SERVICES = {} # {service_name : {ip, port, communication_type}} dict of  dictionaries

#onion routing vars - Start


SERIAL_NUM_SERVICES = 1
ROUTER_NAME = sys.argv[1] #cmd input
CLIENTS_PORT = int(sys.argv[2]) #cmd input
VERBOSE_LEVEL = int(sys.argv[3]) #cmd input
VB = verbose.verbose()

SERVICES_DB_DIR = "%s\%s_services.db"%(os.getcwd(), ROUTER_NAME)


#CURR_COMMUNICATION = [] #tcp connections (prev_ip, next_ip)

#Encryption Decryption Global Vars - Start
PUBLIC_KEY, PRIVATE_KEY  =  onion_encryption_decryption.generate_keys((os.getcwd()), ROUTER_NAME) 

#Encryption Decryption Global Vars - END
#server - router - communication - END
DIR_SERVER_IP = '10.0.0.7'#'192.168.1.22' #'192.168.43.207' #'10.0.0.5'
DIR_SERVER_PORT = 50010
BUFSIZ = 1024
DIR_SERVER_ADDR = (DIR_SERVER_IP, DIR_SERVER_PORT)
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.connect(DIR_SERVER_ADDR)

if create_databases():
    VB.print_data('DATABASES CONNECTED', VB.GENERAL_DATA, VERBOSE_LEVEL)

if connect_to_network(server_sock):#"blocking - handle the handshake"
    thread.start_new_thread(handle_keep_alive,(server_sock,))
    while 1:
        sniff(filter = "udp", prn = handle_packet , count = 0)
else:
    server_sock.close()
    VB.print_data('[failed to connect the server]', VB.ERRORS, VERBOSE_LEVEL)
#server - router - communication - END

#waiting and handling packets - START