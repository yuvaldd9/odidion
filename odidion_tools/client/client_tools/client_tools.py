import socket
import requests
import random
import time
import hashlib
import sys
import os
import threading, thread
import webbrowser
import json_handler
import onion_encryption_decryption
import onion_packet_handler

from scapy.all import *

class ClientErrors(Exception):
    pass

class Client():
    def __init__(self, client_name, is_web_client=False, reqs_port=51000):
        self._running = threading.Event()

        self.timeout = None
        self.client_name = client_name
        self.splitted_data = {}
        self.data_from_service = ""
        self.data_to_send = []
        self.counter_waiting_data = 0
        self.communication_details = {}
        self.first_time = True

        #client details
        self.udp_ip ="10.0.0.10"#'192.168.1.22' #'192.168.43.207' #"10.0.0.5"
        self.udp_port = 50102
        self.sniff_filter = "udp port %s"%(self.udp_port, ) 
        self.udp_addr = (self.udp_ip, self.udp_port)
        
        #directory server socket details
        self.dir_server_ip = "10.0.0.10"#'192.168.0.100'#'192.168.1.22' #'192.168.43.207' #"10.0.0.5"
        self.dir_server_port = 50010
        self.bufsiz = 4096
        self.dir_server_addr = (self.dir_server_ip, self.dir_server_port)    

        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.connect(self.dir_server_addr)

        self.public_key, self.private_key  =  onion_encryption_decryption.generate_keys((os.getcwd()), self.client_name)
        self.id_key = hashlib.md5(self.private_key).digest()

        self.is_web_client = is_web_client

        self.scapy_sock = conf.L3socket()
        #self.sent_key_semaphore = threading.Semaphore(1)

        if self.is_web_client:
            self._running.set()
            self.reqs_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.reqs_port = reqs_port
            self.reqs_sock.bind(('', self.reqs_port))
            self.reqs_url = 'http://localhost:%s/'%(self.reqs_port,)
            print self.reqs_url
            self.reqs_sock.listen(2)
            threading.Thread(target=self._handle_web_reqs).start()

    def _handle_web_reqs(self):
        print '----handle web----'
        while 1:
            sock, addr = self.reqs_sock.accept()
            
            thread.start_new_thread(self.convertor_thread, (sock,))        
        self._running.clear()
            
    def convertor_thread(self, sock):
        thread.start_new_thread(self.convertor_reciever, (sock,))
        while 1:
            req = sock.recv(self.bufsiz)
            if req:
                self.data_to_send.append(req)
            else:
                break
        
            

    def convertor_reciever(self, sock):
        #self.sent_key_semaphore.acquire()
        for data in self.manage_communication():
            #data += r'\r\n\r\n'
            try:
                sock.send(data)
                self.data_from_service = ''
            except:
                self.data_from_service = ''
                break

    def _handle_packet(self, onion_pkt):
        
        udp_data = onion_pkt[UDP].payload.build()

        try:

            seperator_index = udp_data.index(':')
            
            key_comm_header = udp_data[seperator_index + 1 : seperator_index + onion_encryption_decryption.KEYS_LEN + 1]
            dec_sym_key = onion_encryption_decryption.RSA_Decryption(key_comm_header,self.private_key)
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
        except:
            self.data_from_service = None
            return True
            
    def connect_data(self):
        reply = ""
        for i in xrange(self.splitted_data['End']):
            self.data_from_service += (self.splitted_data[i])
        self.splitted_data = {}
        print self.data_from_service
        return True

    def send_packets(self, data_parts):

        service_public_key = self.communication_details["service_public_key"]
        communication_type = self.communication_details["communication_type"]
        routers = self.communication_details["routers"]
        service_serial_num = str(self.communication_details["serial_number"])

        for i, part in enumerate(data_parts):
            pkt = onion_packet_handler.create_onion_packet(routers, service_public_key, communication_type, part,\
                                                            self.udp_addr, service_serial_num, self.id_key)
            new_pkt = IP(pkt.build())
            self.scapy_sock.send(new_pkt)

  

    def send(self, data):
        """
        ALERT! : Web Clients has to pass the http request text here! 
        """
        self.data_to_send.append(data)

    def send_req(self, method):
        req = requests.get(self.reqs_url)
        return req
  
    def wait_for_data(self):
        while 1:
            try:
                s = self.data_to_send.pop()
                if s != '-1':
                    yield s
                else:
                    break
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
            recieved_msg = False
            if s == -1:
                break
            print 'waiting..'
            data_parts = self._divide_data(s)
            while not recieved_msg:
                self.send_packets(data_parts)
                self.timeout = time.time() + 120
                sniff(filter = self.sniff_filter, stop_filter = self._handle_packet)            
                print '-hoiii----'
                if not self.data_from_service:
                    print 'wtfffff'
                    break
                elif self.data_from_service != "!{SEND AGAIN}!":
                    print 'good'
                    recieved_msg = True
                    
            yield (self.data_from_service)
    

    def _divide_data(self, data):
        
        len_of_data = 30
        repeat_times = len(data)/len_of_data
        data_parts = []
        trail_counter = 0 

        for i in xrange(repeat_times):
            data_parts.append(json_handler.create_service_json(data[i*len_of_data:(i+1)*len_of_data], i))
        
        if data[(repeat_times)*len_of_data:]:
            data_parts.append(json_handler.create_service_json(data[(repeat_times)*len_of_data:], repeat_times))
            trail_counter = 1
        
        data_parts.append(json_handler.create_service_json(repeat_times + trail_counter, 'End'))
        
        return data_parts

    def ask_to_service(self, onion_url):
        
        while 1:
            self.server_sock.send(json_handler.create_json(onion_url))
            data = json_handler.recieve_json(self.server_sock.recv(self.bufsiz))   
            if data["state"] == json_handler.STATE_FAILED: 
                raise ClientErrors('Check your url')
                break
            elif data["state"] == json_handler.STATE_SEND_AGAIN:
                self.server_sock.send(json_handler.create_json(onion_url))
                pass
            else:
                self.communication_details = data["args"]
                print self.communication_details
                break
        self.server_sock.close()


        if self.send_key_to_service():
            #self.sent_key_semaphore.release()
            self.data_from_service = ''
            self.splitted_data = {}
            print 'yep'
            if self.is_web_client:
                webbrowser.open(self.reqs_url)
            return True
        return False
            

    
    def send_key_to_service(self):
        """
        blocking -> sends through the network the public key.
        """
        data_parts = self._divide_data(self.public_key)
        recieved_msg = False
        for attempt in xrange(3):
            self.send_packets(data_parts)
            self.timeout = time.time() + 120
            sniff(filter = self.sniff_filter, stop_filter = self._handle_packet) 
            if not self.data_from_service:
                print 'key was not recieved'
            elif self.data_from_service == "[RECIEVED KEY]":
                print 'key recieved'
                self.data_from_service = ''
                self.splitted_data = {}
                return True
        return False

    def session(self):
        for data in self.manage_communication():
            yield data
            self.splitted_data = {}
            self.data_from_service = ''
            
        yield -1
