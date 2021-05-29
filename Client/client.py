import socket
from scapy.all import *
import onion_packet_handler
import sys , os
import json_handler
import random
import time
import onion_encryption_decryption
import hashlib

"""

if sys.stdout != sys.__stdout__:
    sys.stdout = sys.__stdout__

"""

#Encryption Decryption - END
#handle onion-routing - START
class client:
    TIMEOUT = False
    DATA_FROM_SERVICE = ""
    DATA_TO_SEND = ['TEMP']
    PUBLIC_KEY, PRIVATE_KEY  =  onion_encryption_decryption.generate_keys((os.getcwd()), 'my')
    ID_KEY  = hashlib.md5(PUBLIC_KEY).digest()

    CURRENT_PKTS = {}#serial_num : pkt
    COMMUNICATION_DETAILS = {}
    UDP_IP = '10.0.0.6'#'192.168.1.22' #'192.168.43.207' #"10.0.0.5"
    UDP_PORT = 50100
    UDP_ADDR = (UDP_IP, UDP_PORT)

    FIRST_TIME = True

    DIR_SERVER_IP = '10.0.0.6'#'192.168.1.22' #'192.168.43.207' #"10.0.0.5"
    DIR_SERVER_PORT = 50010
    BUFSIZ = 4096 
    DIR_SERVER_ADDR = (DIR_SERVER_IP, DIR_SERVER_PORT)

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.connect(DIR_SERVER_ADDR)

    def __init__(self):
        pass

    @staticmethod
    def _handle_packet(onion_pkt):
        global DATA_FROM_SERVICE
        global TIMEOUT

        udp_data = onion_pkt[UDP].payload.build()
        
        if onion_pkt[0][2].dport == client.UDP_PORT:
            onion_pkt[0].display()
            
            seperator_index = udp_data.index(':')
            id_key = udp_data[:seperator_index]
            key_comm_header = udp_data[seperator_index+1:seperator_index +1+ onion_encryption_decryption.KEYS_LEN]
            dec_sym_key = onion_encryption_decryption.RSA_Decryption(key_comm_header,client.PRIVATE_KEY)
            
            encrypted_pkt = bytes(udp_data[seperator_index +1+ onion_encryption_decryption.KEYS_LEN:])
            
            recv_data = (onion_encryption_decryption.sym_decryption(encrypted_pkt,dec_sym_key))
            
            if recv_data[:3] != 'ACK':
                return False
            else:
                client.DATA_FROM_SERVICE = recv_data[3:]
                return True
        if time.time() > client.TIMEOUT:
                client.DATA_FROM_SERVICE = None
                return True
            
        
    @staticmethod
    def send_packets(data_parts, routers, service_public_key, communication_type, UDP_ADDR, serial_num, ID_KEY):
        for part in data_parts.itervalues():
                pkt = onion_packet_handler.create_onion_packet(routers, service_public_key, communication_type, part,\
                                                                UDP_ADDR, serial_num, ID_KEY)
                new_pkt = IP(pkt.build())
                #CURRENT_PKTS[index] = new_pkt
                send(new_pkt)
                time.sleep(0)
        


    @staticmethod
    def manage_communication():
        """
        manage the part of the client in the onion routing process
        """
        
        service_public_key = client.COMMUNICATION_DETAILS["service_public_key"]
        communication_type = client.COMMUNICATION_DETAILS["communication_type"]
        routers = client.COMMUNICATION_DETAILS["routers"]

    
        #action = raw_input('[SYSTEM - ROUTING] what is the action with this site? --->')
        
        while client.DATA_TO_SEND[0] != 'END COMM':
            print 'waiting..'
            while 1:
                try:
                    s = client.DATA_TO_SEND[1]
                    break
                except:
                    pass
            data_parts = client._divide_data(s, client.FIRST_TIME)
            client.DATA_TO_SEND.pop(1)
            client.FIRST_TIME = False
            client.send_packets(data_parts, routers, service_public_key, communication_type,\
                                client.UDP_ADDR, str(client.COMMUNICATION_DETAILS["serial_number"]), client.ID_KEY)
            client.TIMEOUT = time.time() + 10
            sniff(filter = "udp", stop_filter = client._handle_packet)
            if not client.DATA_FROM_SERVICE:
                print 'WE LOST HIM'
                break
            yield client.DATA_FROM_SERVICE
            
    @staticmethod
    def _divide_data(data, is_first_time):
        if is_first_time:
            data = data +"%$%$" + client.PUBLIC_KEY
        len_of_data = 15
        repeat_times = len(data)/len_of_data
        data_parts = {}
        for i in xrange(repeat_times):
            data_parts[i] =(json_handler.create_service_json(data[i*len_of_data:(i+1)*len_of_data], i))
        if data[(repeat_times)*len_of_data:]:
            data_parts[repeat_times] = (json_handler.create_service_json(data[(repeat_times)*len_of_data:], repeat_times))
        data_parts[repeat_times+1] = (json_handler.create_service_json(repeat_times+1, 'End'))

        return data_parts


    #handle onion-routing - END

    #communication with the server - START
    @staticmethod
    def ask_to_service(onion_url):
        #onion_url = get_data_func()#"S6"#raw_input("please enter the url->")
        print ('req:%s'%(onion_url,))
        while 1:
            client.server_sock.send(json_handler.create_json(onion_url))
            data = json_handler.recieve_json(client.server_sock.recv(client.BUFSIZ))   
            print data   
            if data["state"] == json_handler.STATE_FAILED: 
                print 'Check your url'
                break
            elif data["state"] == json_handler.STATE_SEND_AGAIN:
                client.server_sock.send(json_handler.create_json(onion_url))
                pass
            else:
                client.COMMUNICATION_DETAILS = data["args"]
                break
    @staticmethod
    def session():
        for data in client.manage_communication():
            yield data
            #manage_communication(UDP_ADDR, data["args"])
        client.FIRST_TIME = True
        yield -1

        #communication with the server - END

