import os
import json
import onion_encryption_decryption 
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
    
def connect_data(dict_data_parts, parts):
    data = ""
    for i in xrange(parts):
        try:
            data += dict_data_parts[i]["data"]
        except:
            data += "[NULL]"
    return data
def recieving_data():
    messages = defaultdict(dict)
    while True:
        data, addr = sock.recvfrom(60000) # buffer size is 1024 bytes
        dec_json = onion_encryption_decryption.decrypt_data_service(data, PRIVATE_KEY)
        msg = json.loads(dec_json)
        if msg["serial_num"] != "End":
            messages[msg["jwt"]][msg["serial_num"]] = (msg)
        else:
            data = connect_data(messages[msg["jwt"]], int(msg["data"]))
            del messages[msg["jwt"]]
            yield data
UDP_IP = '10.0.0.3'#'192.168.1.22' #'192.168.43.207' #'10.0.0.5'
UDP_PORT = 50005
BUFSIZ = 1024


DIR_SERVER_IP =  '10.0.0.3'#'192.168.1.22' #'192.168.43.207' #'10.0.0.5'
DIR_SERVER_PORT = 50010
DIR_SERVER_ADDR = (DIR_SERVER_IP,DIR_SERVER_PORT)

DIR_SERVER_SOCKET = socket(AF_INET, SOCK_STREAM)
DIR_SERVER_SOCKET.connect(DIR_SERVER_ADDR)


SERVICE_NAME = "HAPPY TEACHER DAY ERAN, THANKS"
sock = socket(AF_INET,SOCK_DGRAM)
UDP_ADDR = (UDP_IP, UDP_PORT)
sock.bind(UDP_ADDR)
PUBLIC_KEY, PRIVATE_KEY  =  onion_encryption_decryption.generate_keys((os.getcwd()), SERVICE_NAME) 
if register_service(DIR_SERVER_SOCKET, UDP_ADDR, 0):
    for data in recieving_data():
        print("received message: %s" % data)
        
        
else:
    print "Error Occured"