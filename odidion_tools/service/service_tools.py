import os
import json
import onion_encryption_decryption 
import send_back_onion_packet
import json_handler
from socket import *
from collections import defaultdict

class Service():
    UDP_IP = None#'10.0.0.6'#'192.168.1.22' #'192.168.43.207' #'10.0.0.5'
    UDP_PORT = None#50018
    BUFSIZ = None

    DIR_SERVER_IP = '10.0.0.7'#'192.168.1.22' #'192.168.43.207' #'10.0.0.5'
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
        self.udp_ip = None
        self.udp_port = None
        self.bufsiz = None

        self.dir_server_ip = None
        self.dir_server_port = None 
        self.dir_server_addr = (self.dir_server_ip, self.dir_server_port)

        self.dir_server_socket = socket(AF_INET, SOCK_STREAM)
        self.dir_server_socket.connect(self.dir_server_addr)

        self.service_sock = socket(AF_INET, SOCK_DGRAM)

        self.public_key = None
        self.private_key = None
        self.service_name = None

        self.back_id_dict = {}
        self.client_keys = {}
        self.sent_key = defaultdict(bool)
        self.clients_send_again_regs = defaultdict(list)
        

    def bind_and_set_service(self, service_name, ip, port, bufsiz = 1024 ):
        try:
            self.udp_ip = ip
            self.udp_port = port
            self.bufsiz = bufsiz
            self.service_name = service_name
            self.public_key, self.private_key  =  onion_encryption_decryption.generate_keys((os.getcwd()), self.service_name)
            self.service_sock.bind((ip, port))
            print self.udp_ip,   self.udp_port, self.bufsiz,self.service_name
            return True
        except:
            return False


    def register_service(self):
        """
        handle the first communication with the dir_server
        comm_type: - 0-UDP 1-TCp
        """
        service_details = {
            "service_name" : self.service_name,
            "ip" : self.udp_ip,
            "port" : self.udp_port,
            "communication_type" : 0,#only udp yet
            "public_key" : self.public_key
        }

        state_handler = {
            json_handler.STATE_SUCCEED: True,
            json_handler.STATE_SEND_AGAIN: lambda sock,register_json: self.dir_server_socket.send(register_json),
            json_handler.STATE_FAILED: False
        }
        register_json = json_handler.create_json(json_handler.SERVICE_REGISTER,service_details)
        self.dir_server_socket.send(register_json)
        
        while 1:
            data = json_handler.recieve_json(self.dir_server_socket.recv(self.bufsiz))
            if not data:
                return False
            elif data["state"] != json_handler.STATE_SEND_AGAIN:
                self.dir_server_socket.close()
                return state_handler[data["state"]]
            state_handler[data["state"]](self.dir_server_socket, register_json)
        

    def connect_data(self, id_key, dict_data_parts, parts):
        data = ""
        for i in xrange(parts):
            try:
                print dict_data_parts[i]["data"]
                data += dict_data_parts[i]["data"]
            except:
                self.clients_send_again_regs[id_key].append(i)
                data += "[NULL - %s]"%(i,)

        if self.clients_send_again_regs[id_key] != []:
            return None
        return data

    def recieving_data(self):

        messages = defaultdict(dict)
        while True:
            data, addr = self.service_sock.recvfrom(60000) # buffer size is 1024 bytes
            dec_json = onion_encryption_decryption.decrypt_data_service(data, self.private_key)
            seperator = dec_json.index(':')
            id_key = dec_json[:seperator]
            
            self.back_id_dict [id_key] = {
                'ip' : addr[0],
                'port' : addr[1]
            }
            
            msg = json.loads(dec_json[seperator+1:])

            if msg["serial_num"] != "End":
                messages[id_key][msg["serial_num"]] = (msg)
            else:
                client_details = self.connect_data(id_key, messages[id_key], int(msg["data"]))
        
                if not client_details:
                    send_back_onion_packet.generate_packet(id_key, self.client_keys[id_key],\
                            self.back_id_dict[id_key]['ip'], self.back_id_dict[id_key]['port'],\
                            str(self.clients_send_again_regs[id_key]))
                else:
                    if not self.sent_key[id_key]:
                        client_details = client_details.split('%$%$')
                        self.client_keys[id_key] = client_details[1]
                        data = client_details[0]
                        self.sent_key[id_key] = True
                    else:
                        data = client_details
                    del messages[id_key]
                    yield id_key, data
    
    def recieve_from_clients(self):            
        for id_key, data in self.recieving_data():
            yield id_key,data
    
    
    def send_to_client(self, id_key, data_to_send):
        send_back_onion_packet.generate_packet(id_key, self.client_keys[id_key],\
                        self.back_id_dict[id_key]['ip'], self.back_id_dict[id_key]['port'], (data_to_send))

