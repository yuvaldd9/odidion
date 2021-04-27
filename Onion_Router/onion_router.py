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
import global_variables

def create_databases():
    """
    create the databases if there are not exist
    {service_name, ip, port, communication_type}
    """
    if not os.path.exists(global_variables.SERVICES_DB_DIR):
        return db.connect_dataBase(global_variables.SERVICES_DB_DIR, '''CREATE TABLE services( id INTEGER PRIMARY KEY, service_name TEXT,\
                                                                ip TEXT, port TEXT ,communication_type TEXT)''')
    return False
                            
#DATABASE - END
#server - router - communication - START
def connect_to_network(server_sock):
    """
    handling the connection handshake between the dir server and the router
    """
    onion_router_details = {
        "router_name" : global_variables.ROUTER_NAME,
        "ip" : global_variables.ROUTER_IP,
        "public_key" : PUBLIC_KEY,
        "port" : global_variables.CLIENTS_PORT
    }
    connect_req = json_handler.create_json(json_handler.ONION_ROUTER_REGISTER, onion_router_details)
    server_sock.send(connect_req)
    while 1:
        data = server_sock.recv(global_variables.BUFSIZ)
        if not data:
            global_variables.VB.print_data("ending communication with the server", global_variables.VB.ERRORS)
            break
        data = json.loads(data)
        if data["state"] == json_handler.STATE_SUCCEED:
            return True
        elif data["state"] == json_handler.STATE_FAILED:
            print data
            return False
        else:
            server_sock.send(connect_req)
    return False


def add_service(service_details):

    upload_done = db.set_data(global_variables.SERVICES_DB_DIR, '''INSERT INTO services(service_name, ip, port, communication_type) VALUES(?,?,?,?)''',\
            args= (service_details["service_name"], service_details["service_ip"], service_details["service_port"], service_details["service_communication_type"]))
    if upload_done:
        global_variables.VB.print_data("SERVICE UPLOADED SUCCESSFULLY", global_variables.VB.GENERAL_DATA)
        global_variables.SERVICES[global_variables.SERIAL_NUM_SERVICES] = (service_details)
        global_variables.LOAD_LEVEL += 1
        
        return global_variables.SERIAL_NUM_SERVICES
    return False
def delete_service(service_details):
    return db.set_data(global_variables.SERVICES_DB_DIR,'''DELETE FROM services WHERE service_name = \'%s\''''%(service_details["service_name"]))
def handle_keep_alive(server_sock):
    """
    handle the keep alive connection between the server
    """
    #print server_sock.stillconnected()
    keep_alive_details = {
        "load" : global_variables.LOAD_LEVEL,
        "router_name" : global_variables.ROUTER_NAME
    }
    while 1:
        try:        

            msg = json_handler.create_json(json_handler.ONION_ROUTER_KEEP_ALIVE, keep_alive_details)
            global_variables.VB.print_data(msg, global_variables.VB.KEEP_ALIVE)
            server_sock.send(msg)
            d = server_sock.recv(global_variables.BUFSIZ)

            data = json_handler.recieve_json(d)
            

            global_variables.VB.print_data("RECIEVED KEEP ALIVE MSG", global_variables.VB.KEEP_ALIVE)
            print data
            if not data:
                break
            elif "new_service" in data["args"].keys():
                keep_alive_details["service_added"] = (add_service(data["args"]["new_service"]))#need to create handle for errors.
                keep_alive_details["load"] = global_variables.LOAD_LEVEL
                global_variables.SERIAL_NUM_SERVICES += 1
            elif "delete_service" in data["args"].keys():
                #TODO
                keep_alive_details["service_deleted"] = delete_service(data["args"]["delete_service"])
                
            else:
                if "service_added" in keep_alive_details.keys():
                    del keep_alive_details["service_added"]
                elif "delete_service" in keep_alive_details.keys():
                     del keep_alive_details["service_deleted"]

            time.sleep(5)
        except Exception as e:
            global_variables.VB.print_data(e, global_variables.VB.ERRORS)
            break

def send_to_service(data, src, sport):
    service_details = data.split(':',2)
    service_name, id_key, service_data = int(service_details[0]), service_details[1], service_details[2]
    
    global_variables.ROUTING_PROCESSES[id_key] = {
                'ip' : src,
                'port' : sport
            }
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', global_variables.CLIENTS_PORT))
    sock.sendto(service_data, (global_variables.SERVICES[service_name]["service_ip"], int(global_variables.SERVICES[service_name]["service_port"])))
    
    
def handle_packet(onion_pkt):
    seperator = ':'
    try:
        udp_data = onion_pkt[UDP].payload.build()
    
        pkt_purpose = onion_pkt[0][IP].tos
        if pkt_purpose == 0:
            
            global_variables.VB.print_data('----RECIEVED PACKET TO NEXT NODE----', global_variables.VB.PKTS_DATA)
            
            seperator_index = udp_data.index(seperator)
            id_key = udp_data[:seperator_index]
            key_comm_header = udp_data[seperator_index+1:seperator_index +1+ onion_encryption_decryption.KEYS_LEN]
            dec_sym_key = onion_encryption_decryption.RSA_Decryption(key_comm_header,PRIVATE_KEY)[:-1]# the slicing may change because the len analyzing(in the future)
            comm_type = dec_sym_key[len(dec_sym_key)-1:] #for the comm handler(after the poc)
            
            encrypted_pkt = bytes(udp_data[seperator_index +1+ onion_encryption_decryption.KEYS_LEN:])
            
            next_pkt = IP(onion_encryption_decryption.sym_decryption(encrypted_pkt,dec_sym_key))

        
            global_variables.ROUTING_PROCESSES[id_key] = {
                'ip' : onion_pkt[0][IP].src,
                'port' : onion_pkt[0][UDP].sport
            }
            scapy_sock.send(next_pkt)


            #except Exception as e:
        elif pkt_purpose == 1:
            global_variables.VB.print_data('----RECIEVED PACKET TO SERVICE----', global_variables.VB.PKTS_DATA)
            
            encrypted_data = bytes(udp_data[onion_encryption_decryption.KEYS_LEN:])
            send_to_service(udp_data, onion_pkt[0][1].src, onion_pkt[0][1].sport)
        
        elif pkt_purpose == 2:
            global_variables.VB.print_data('----RECIEVED PACKET TO CLIENT----', global_variables.VB.PKTS_DATA)
            
            seperator_index = udp_data.index(seperator)
            id_key = udp_data[:seperator_index]

            client_data = bytes(udp_data[seperator_index +1:])
            
            next_pkt = IP(dst = global_variables.ROUTING_PROCESSES[id_key]['ip'], tos = 2)\
                            /UDP(dport = global_variables.ROUTING_PROCESSES[id_key]['port'])/Raw(load = id_key + ':' + client_data)

            scapy_sock.send(next_pkt)
            
    except:
        pass
            




#onion routing vars - Start

global_variables.ROUTER_NAME = sys.argv[1] #cmd input
global_variables.CLIENTS_PORT = int(sys.argv[2]) #cmd input
global_variables.VB.set_name(global_variables.ROUTER_NAME)
global_variables.VB.set_level( int(sys.argv[3])) #cmd input


global_variables.SERVICES_DB_DIR = "%s\%s_services.db"%(os.getcwd(), global_variables.ROUTER_NAME)


#CURR_COMMUNICATION = [] #tcp connections (prev_ip, next_ip)

#Encryption Decryption Global Vars - Start
PUBLIC_KEY, PRIVATE_KEY  =  onion_encryption_decryption.generate_keys((os.getcwd()), global_variables.ROUTER_NAME) 

#Encryption Decryption Global Vars - END
#server - router - communication - END

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.connect(global_variables.DIR_SERVER_ADDR)

scapy_sock = conf.L3socket()

if create_databases():
    global_variables.VB.print_data('DATABASES CONNECTED', global_variables.VB.GENERAL_DATA)

if connect_to_network(server_sock):#"blocking - handle the handshake"
    thread.start_new_thread(handle_keep_alive,(server_sock,))
    while 1:
        sniff(filter = "udp dst port %s"%(global_variables.CLIENTS_PORT), prn = handle_packet , count = 0)
else:
    global_variables.VB.print_data('[failed to connect the server]', global_variables.VB.ERRORS)
    server_sock.close()
    
#server - router - communication - END
