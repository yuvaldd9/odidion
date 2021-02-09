import os
import json
import onion_encryption_decryption 
import send_back_onion_packet
import json_handler
from socket import *
from collections import defaultdict

class service:
    UDP_IP = None#'10.0.0.6'#'192.168.1.22' #'192.168.43.207' #'10.0.0.5'
    UDP_PORT = None#50018
    BUFSIZ = None

    DIR_SERVER_IP =  '10.0.0.7'#'192.168.1.22' #'192.168.43.207' #'10.0.0.5'
    DIR_SERVER_PORT = 50010
    DIR_SERVER_ADDR = (DIR_SERVER_IP,DIR_SERVER_PORT)

    DIR_SERVER_SOCKET = socket(AF_INET, SOCK_STREAM)
    DIR_SERVER_SOCKET.connect(DIR_SERVER_ADDR)

    sock = socket(AF_INET,SOCK_DGRAM)

    PUBLIC_KEY = None
    PRIVATE_KEY = None
    SERVICE_NAME = None
    
    BACK_ID_DICT = {} #id_key : 
    CLIENTS_KEYS = {} # id_key : public key
    SENT_KEY = defaultdict(bool) # id_key : expect to key?
    CLIENTS_SEND_AGAIN_REQS = defaultdict(list) # id_key : [numbers...]
        
    def __init__(self):
        pass
    
    @staticmethod
    def bind_and_set_service(service_name, ip, port, bufsiz = 1024 ):
        #try:
        service.UDP_IP = ip
        service.UDP_PORT = port
        service.BUFSIZ = bufsiz
        service.SERVICE_NAME = service_name
        service.PUBLIC_KEY, service.PRIVATE_KEY  =  onion_encryption_decryption.generate_keys((os.getcwd()), service.SERVICE_NAME)
        service.sock.bind((ip, port))
        print service.UDP_IP,   service.UDP_PORT, service.BUFSIZ,service.SERVICE_NAME
        return True
        #except:
        return False


    @staticmethod
    def register_service():
        """
        handle the first communication with the dir_server
        comm_type: - 0-UDP 1-TCp
        """
        service_details = {
            "service_name" : service.SERVICE_NAME,
            "ip" : service.UDP_IP,
            "port" : service.UDP_PORT,
            "communication_type" : 0,#only udp yet
            "public_key" : service.PUBLIC_KEY
        }

        state_handler = {
            json_handler.STATE_SUCCEED: True,
            json_handler.STATE_SEND_AGAIN: lambda sock,register_json: service.DIR_SERVER_SOCKET.send(register_json),
            json_handler.STATE_FAILED: False
        }
        register_json = json_handler.create_json(json_handler.SERVICE_REGISTER,service_details)
        service.DIR_SERVER_SOCKET.send(register_json)
        
        while 1:
            data = json_handler.recieve_json(service.DIR_SERVER_SOCKET.recv(service.BUFSIZ))
            if not data:
                return False
            elif data["state"] != json_handler.STATE_SEND_AGAIN:
                service.DIR_SERVER_SOCKET.close()
                return state_handler[data["state"]]
            state_handler[data["state"]](service.DIR_SERVER_SOCKET, register_json)
        
    @staticmethod
    def connect_data(id_key, dict_data_parts, parts):
        data = ""
        for i in xrange(parts):
            try:
                print dict_data_parts[i]["data"]
                data += dict_data_parts[i]["data"]
            except:
                CLIENTS_SEND_AGAIN_REQS[id_key].append(i)
                data += "[NULL - %s]"%(i,)

        if service.CLIENTS_SEND_AGAIN_REQS[id_key] != []:
            return None
        return data
    @staticmethod
    def recieving_data():
        global BACK_ID_DICT
        global CLIENTS_KEYS 
        global CLIENTS_SEND_AGAIN_REQS

        messages = defaultdict(dict)
        while True:
            data, addr = service.sock.recvfrom(60000) # buffer size is 1024 bytes
            dec_json = onion_encryption_decryption.decrypt_data_service(data, service.PRIVATE_KEY)
            seperator = dec_json.index(':')
            id_key = dec_json[:seperator]
            
            service.BACK_ID_DICT [id_key] = {
                'ip' : addr[0],
                'port' : addr[1]
            }
            
            msg = json.loads(dec_json[seperator+1:])

            if msg["serial_num"] != "End":
                messages[id_key][msg["serial_num"]] = (msg)
            else:
                client_details = service.connect_data(id_key,messages[id_key], int(msg["data"]))
                
                if not client_details:
                    send_back_onion_packet.generate_packet(id_key, service.CLIENTS_KEYS[id_key],\
                            service.BACK_ID_DICT[id_key]['ip'], service.BACK_ID_DICT[id_key]['port'],\
                            str(service.CLIENTS_SEND_AGAIN_REQS[id_key]))
                else:
                    if not service.SENT_KEY[id_key]:
                        client_details = client_details.split('%$%$')
                        service.CLIENTS_KEYS[id_key] = client_details[1]
                        data = client_details[0]
                        service.SENT_KEY[id_key] = True
                    else:
                        data = client_details
                    del messages[id_key]
                    yield id_key, data
    @staticmethod
    def recieve_from_clients():            
        for id_key, data in service.recieving_data():
            yield id_key,data
    @staticmethod
    def send_to_client(id_key, data_to_send):
        send_back_onion_packet.generate_packet(id_key, service.CLIENTS_KEYS[id_key],\
                        service.BACK_ID_DICT[id_key]['ip'], service.BACK_ID_DICT[id_key]['port'], bytes(data_to_send))

