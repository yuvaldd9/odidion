import os
import json
import onion_encryption_decryption 
import send_back_onion_packet
import json_handler
from socket import *
from collections import defaultdict


def register_service(sock, addr, comm_type):
    """
    handle the first communication with the dir_server
    comm_type: - 0-UDP 1-TCp
    """
    global PUBLIC_KEY
    global SERVICE_NAME
    
    service_details = {
        "service_name" : SERVICE_NAME,
        "ip" : addr[0],
        "port" : addr[1],
        "communication_type" : comm_type,
        "public_key" : PUBLIC_KEY
    }
    state_handler = {
        json_handler.STATE_SUCCEED: True,
        json_handler.STATE_SEND_AGAIN: lambda sock,register_json: sock.send(register_json),
        json_handler.STATE_FAILED: False
    }

    register_json = json_handler.create_json(json_handler.SERVICE_REGISTER,service_details)
    
    sock.send(register_json)
    while 1:
        data = json_handler.recieve_json(sock.recv(BUFSIZ))

        if not data:
            break
        elif data["state"] != json_handler.STATE_SEND_AGAIN:
            sock.close()
            
            return state_handler[data["state"]]
        state_handler[data["state"]]
    
def connect_data(id_key, dict_data_parts, parts):
    global CLIENTS_SEND_AGAIN_REQS
    data = ""
    for i in xrange(parts):
        try:
            print dict_data_parts[i]["data"]
            data += dict_data_parts[i]["data"]
        except:
            CLIENTS_SEND_AGAIN_REQS[id_key].append(i)
            data += "[NULL - %s]"%(i,)

    if CLIENTS_SEND_AGAIN_REQS[id_key] != []:
        print CLIENTS_SEND_AGAIN_REQS[id_key]
        return None
    return data
def recieving_data():
    global BACK_ID_DICT
    global CLIENTS_KEYS 
    global CLIENTS_SEND_AGAIN_REQS

    messages = defaultdict(dict)
    while True:
        data, addr = sock.recvfrom(60000) # buffer size is 1024 bytes
        dec_json = onion_encryption_decryption.decrypt_data_service(data, PRIVATE_KEY)
        seperator = dec_json.index(':')
        id_key = dec_json[:seperator]
        
        BACK_ID_DICT [id_key] = {
            'ip' : addr[0],
            'port' : addr[1]
        }
        
        msg = json.loads(dec_json[seperator+1:])

        if msg["serial_num"] != "End":
            messages[id_key][msg["serial_num"]] = (msg)
        else:
            client_details = connect_data(id_key,messages[id_key], int(msg["data"]))
            
            if not client_details:
                send_back_onion_packet.generate_packet(id_key, CLIENTS_KEYS[id_key],\
                        BACK_ID_DICT[id_key]['ip'], BACK_ID_DICT[id_key]['port'], str(CLIENTS_SEND_AGAIN_REQS[id_key]))
            else:
                if not SENT_KEY[id_key]:
                    client_details = client_details.split('%$%$', 1)
                    CLIENTS_KEYS[id_key] = client_details[1]
                    data = client_details[0]
                    SENT_KEY[id_key] = True
                else:
                    data = client_details
                send_back_onion_packet.generate_packet(id_key, CLIENTS_KEYS[id_key],\
                       BACK_ID_DICT[id_key]['ip'], BACK_ID_DICT[id_key]['port'], ('ACK'+str(int(data)+1)))
                del messages[id_key]
                yield id_key, data

            
UDP_IP = '10.0.0.6'#'192.168.1.22' #'192.168.43.207' #"192.168.1.26"
UDP_PORT = 50018
BUFSIZ = 1024


DIR_SERVER_IP =  '10.0.0.6'#'192.168.1.22' #'192.168.43.207' #"192.168.1.26"
DIR_SERVER_PORT = 50010
DIR_SERVER_ADDR = (DIR_SERVER_IP,DIR_SERVER_PORT)

DIR_SERVER_SOCKET = socket(AF_INET, SOCK_STREAM)
DIR_SERVER_SOCKET.connect(DIR_SERVER_ADDR)


SERVICE_NAME = "S6"
sock = socket(AF_INET,SOCK_DGRAM)
UDP_ADDR = (UDP_IP, UDP_PORT)
sock.bind(UDP_ADDR)
PUBLIC_KEY, PRIVATE_KEY  =  onion_encryption_decryption.generate_keys((os.getcwd()), SERVICE_NAME) 

BACK_ID_DICT = {} #id_key : 
CLIENTS_KEYS = {} # id_key : public key
SENT_KEY = defaultdict(bool) # id_key : expect to key?
CLIENTS_SEND_AGAIN_REQS = defaultdict(list) # id_key : [numbers...]


if register_service(DIR_SERVER_SOCKET, UDP_ADDR, 0):
    print 'connected', SERVICE_NAME
    for id_key, data in recieving_data():
        print("received message: %s" % data)
        print BACK_ID_DICT[id_key]
        
        
        
else:
    print "Error Occured"