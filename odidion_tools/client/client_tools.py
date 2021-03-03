import socket
from scapy.all import *
import onion_packet_handler
import sys , os
import json_handler
import random
import time
import onion_encryption_decryption
import hashlib


class Client():

    

    def __init__(self, client_name):
        self.timeout = None
        self.client_name = client_name
        self.splitted_data = {}
        self.data_from_service = ""
        self.data_to_send = []
        self.communication_details = {}
        self.first_time = True

        #client details
        self.udp_ip = '10.0.0.7'#'192.168.1.22' #'192.168.43.207' #'10.0.0.5'
        self.udp_port = 50102
        self.udp_addr = (self.udp_ip, self.udp_port)
        
        #directory server socket details
        self.dir_server_ip =  '10.0.0.7'#'192.168.0.100'#'192.168.1.22' #'192.168.43.207' #'10.0.0.5'
        self.dir_server_port = 50010
        self.bufsiz = 4096
        self.dir_server_addr = (self.dir_server_ip, self.dir_server_port)    

        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.connect(DIR_SERVER_ADDR)

        self.public_key, self.public_key  =  onion_encryption_decryption.generate_keys((os.getcwd()), self.client_name)
        self.id_key = hashlib.md5(self.public_key).digest()

    def _handle_packet(self, onion_pkt):
        
        udp_data = onion_pkt[UDP].payload.build()

        if onion_pkt[0][2].dport == self.udp_port:

            seperator_index = udp_data.index(':')
            
            key_comm_header = udp_data[seperator_index + 1 : seperator_index + onion_encryption_decryption.KEYS_LEN + 1]
            dec_sym_key = onion_encryption_decryption.RSA_Decryption(key_comm_header,self.public_key)
            encrypted_pkt = bytes(udp_data[seperator_index + onion_encryption_decryption.KEYS_LEN + 1:])

            recv_data = json_handler.recieve_json(onion_encryption_decryption.sym_decryption(encrypted_pkt,dec_sym_key))
            
            
            if recv_data["serial_num"] != 'End':
                self.splitted_data[recv_data["serial_num"]] = (recv_data["data"])
            else:
                self.splitted_data[recv_data["serial_num"]] = int(recv_data["data"])
                return self.connect_data()

            if time.time() > self.timeout:
                self.data_from_service = None
                return True
        return False
            
    def connect_data(self):
        for i in xrange(self.splitted_data['End']):
            self.data_from_service += (self.splitted_data[i])
        return True

    def send_packets(self, data_parts):

        service_public_key = self.communication_details["service_public_key"]
        communication_type = self.communication_details["communication_type"]
        routers = self.communication_details["routers"]
        service_serial_num = str(self.communication_details["serial_number"])
        
        for part in data_parts:
                pkt = onion_packet_handler.create_onion_packet(routers, service_public_key, communication_type, part,\
                                                                self.udp_addr, service_serial_num, self.id_key)
                new_pkt = IP(pkt.build())
                send(new_pkt)
                time.sleep(0)

    def send(self, data):
        self.data_to_send.append(data)
  
    def wait_for_data(self):
        while 1:
            try:
                s = self.data_to_send[0]
                if s == '-1':
                    break
                yield s
            except:
                pass
        yield -1

    def manage_communication(self):
        """
        manage the part of the client in the onion routing process
        """
        
        service_public_key = self.communication_details["service_public_key"]
        communication_type = self.communication_details["communication_type"]
        routers = self.communication_details["routers"]

    
        #action = raw_input('[SYSTEM - ROUTING] what is the action with this site? --->')
        
        #while self.data_to_send[0] != 'END COMM':
        for s in self.wait_for_data():
            if s == -1:
                break
            print 'waiting..'
            data_parts = self._divide_data(s, self.first_time)
            self.data_to_send.pop()
            self.send_packets(data_parts)
            self.timeout = time.time() + 60
            sniff(filter = "udp", stop_filter = self._handle_packet)            
            if not self.data_from_service:
                print 'WE LOST HIM'
                break
            yield (self.data_from_service)
            
    def _divide_data(self, data, is_first_time):
        if is_first_time:
            data = data +"%$%$" + self.public_key

        len_of_data = 15
        repeat_times = len(data)/len_of_data
        data_parts = []
        
        for i in xrange(repeat_times):
            data_parts.append(json_handler.create_service_json(data[i*len_of_data:(i+1)*len_of_data], i))
        
        if data[(repeat_times)*len_of_data:]:
            data_parts.append(json_handler.create_service_json(data[(repeat_times)*len_of_data:], repeat_times))
        
        data_parts.append(json_handler.create_service_json(repeat_times+1, 'End'))

        return data_parts

    def ask_to_service(self, onion_url):
        while 1:
            self.server_sock.send(json_handler.create_json(onion_url))
            data = json_handler.recieve_json(self.server_sock.recv(self.bufsiz))   
            print data   
            if data["state"] == json_handler.STATE_FAILED: 
                print 'Check your url'
                break
            elif data["state"] == json_handler.STATE_SEND_AGAIN:
                self.server_sock.send(json_handler.create_json(onion_url))
                pass
            else:
                self.communication_details = data["args"]
                break
        self.server_sock.close()

    def session(self):
        for data in self.manage_communication():
            yield data
            self.first_time = False
            self.splitted_data = {}
            self.data_from_service = ""
            
        yield -1

