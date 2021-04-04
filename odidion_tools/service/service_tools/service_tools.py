import thread
import os
import json
import pickle

import onion_encryption_decryption 
import send_back_onion_packet
import json_handler

from collections import defaultdict
from socket import *


class Service():
    def __init__(self, web_path = False):

        self.udp_ip = None
        self.udp_port = None
        self.bufsiz = None

        self.dir_server_ip = "10.0.0.7"
        self.dir_server_port = 50010 
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
        
        self.messages = defaultdict(dict)
        if web_path:

            thread.start_new_thread(os.system,(web_path,))
            
            self.is_web_service = True
            self.flask_sock = socket(AF_INET, SOCK_STREAM)
            self.flask_sock.connect(('127.0.0.1', 5000)) # 5000 is the default port of flask
        else:
            self.is_web_service = False


    def bind_and_set_service(self, service_name, ip, port, bufsiz = 1024 ):
        try:
            self.udp_ip = ip
            self.udp_port = port
            self.bufsiz = bufsiz
            self.service_name = service_name
            self.public_key, self.private_key  =  onion_encryption_decryption.generate_keys((os.getcwd()), self.service_name)
            self.service_sock.bind((ip, port))
    
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
        

    def connect_data(self, id_key, parts):
        data = ""
        
        for i in xrange(parts):
            try:
                data += self.messages[id_key][i]["d"]
            except Exception as e:
                print(e)
                print i
                self.clients_send_again_regs[id_key].append(i)
                data += "[NULL - %s]"%(i,)
        
        if self.clients_send_again_regs[id_key] != []:
            return None
        
        return data

    def http_handle(self, id_key, req):
        replies = []
        self.flask_sock.send(req)
        while 1:
            data = self.flask_sock.recv(self.bufsiz)
            if not data:
                break
            replies.append(data)
        self.flask_sock.close()
        self.flask_sock = socket(AF_INET, SOCK_STREAM)
        self.flask_sock.connect(('127.0.0.1', 5000))
        if not replies:
            return 'request - failed'
        else:
            """self.send_to_client(id_key, str(len(replies)), True)
            for reply in replies:
                self.send_to_client(id_key, reply)"""
            self.send_to_client(id_key, ''.join(replies))
            return 'request - succeeded'
    
    def recieving_data(self):

        recieved_data_handle = self.http_handle if self.is_web_service else lambda _, data: data
        
        
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
            #msg = eval(dec_json[seperator+1:])
            if msg["sn"] != "End":
                self.messages[id_key][msg["sn"]] = (msg)
            else:
                client_details = self.connect_data(id_key, int(msg["d"]))
                print client_details

                if not client_details and self.sent_key[id_key]:
                    send_back_onion_packet.generate_packet(id_key, self.client_keys[id_key],\
                            self.back_id_dict[id_key]['ip'], self.back_id_dict[id_key]['port'],\
                            "!{SEND AGAIN}!")
                else:
                    if not self.sent_key[id_key] and client_details:
                        self.client_keys[id_key] = client_details
                        self.send_to_client(id_key, "[RECIEVED KEY]")

                    elif client_details:
                        data = client_details

                    del self.messages[id_key]

                    if self.sent_key[id_key]:
                        yield id_key, recieved_data_handle(id_key, data)
                    else:
                        self.sent_key[id_key] = True
                        yield id_key, "[RECIEVED KEY]"
    
    def recieve_from_clients(self):
        """
        only for not web services!
        """          
        for id_key, data in self.recieving_data():
            yield id_key,data
    
    
    def send_to_client(self, id_key, data_to_send, is_web_header = False):
        print '---generating back', data_to_send
        send_back_onion_packet.generate_packet(id_key, self.client_keys[id_key],\
                        self.back_id_dict[id_key]['ip'], self.back_id_dict[id_key]['port'], (data_to_send), is_web_header)

