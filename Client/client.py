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

def handle_packet(onion_pkt):
    global CURRENT_PKTS
    global DATA_FROM_SERVICE
    global TIMEOUT

    udp_data = onion_pkt[UDP].payload.build()
    
    if onion_pkt[0][2].dport == UDP_PORT:
        onion_pkt[0].display()
        print '----RECIEVED PACKET---'
        seperator_index = udp_data.index(':')
        id_key = udp_data[:seperator_index]
        key_comm_header = udp_data[seperator_index+1:seperator_index +1+ onion_encryption_decryption.KEYS_LEN]
        dec_sym_key = onion_encryption_decryption.RSA_Decryption(key_comm_header,PRIVATE_KEY)
        
        encrypted_pkt = bytes(udp_data[seperator_index +1+ onion_encryption_decryption.KEYS_LEN:])
        
        recv_data = (onion_encryption_decryption.sym_decryption(encrypted_pkt,dec_sym_key))
        print recv_data, TIMEOUT, time.time()
        if recv_data[:3] != 'ACK':
            return False
        else:
            DATA_FROM_SERVICE = recv_data[3:]
            return True
    if time.time() > TIMEOUT:
            DATA_FROM_SERVICE = None
            return True
        
    

def send_packets(data_parts, routers, service_public_key, communication_type, UDP_ADDR, serial_num, ID_KEY):
    for part in data_parts.itervalues():
            pkt = onion_packet_handler.create_onion_packet(routers, service_public_key, communication_type, part,\
                                                            UDP_ADDR, serial_num, ID_KEY)
            new_pkt = IP(pkt.build())
            #CURRENT_PKTS[index] = new_pkt
            send(new_pkt)
            time.sleep(0)
    



def manage_communication(UDP_ADDR ,COMMUNICATION_DETAILS):
    """
    manage the part of the client in the onion routing process
    """
    global ID_KEY
    global CURRENT_PKTS
    global TIMEOUT
    global DATA_FROM_SERVICE
    #signal.signal(signal.SIGALRM, wait_for_acks)
    

    service_public_key = COMMUNICATION_DETAILS["service_public_key"]
    communication_type = COMMUNICATION_DETAILS["communication_type"]
    routers = COMMUNICATION_DETAILS["routers"]

    s = raw_input('--->')
    #action = raw_input('[SYSTEM - ROUTING] what is the action with this site? --->')
    data_parts = divide_data(s,True)
    print (data_parts)
    was_acked = False
    
    while s:

        send_packets(data_parts, routers, service_public_key, communication_type,\
                            UDP_ADDR, str(COMMUNICATION_DETAILS["serial_number"]), ID_KEY)
        TIMEOUT = time.time() + 3
        sniff(filter = "udp", stop_filter=handle_packet)
        print DATA_FROM_SERVICE
        if not DATA_FROM_SERVICE:
            print 'WE LOST HIM'
            break
        """while not was_acked:
            if time.time() >= timeout:
                print 'we lost him'
                break
            try:
                was_acked = wait_for_acks()
            except:
                print 'WHAT!?!?!?'
                send_packets(data_parts, routers, service_public_key, communication_type,\
                            UDP_ADDR, str(COMMUNICATION_DETAILS["serial_number"]), ID_KEY)
            if (was_acked):
                print was_acked
                print 'ACKED'"""
            
        s = raw_input('--->')
        data_parts = divide_data(s,False)
    return True

def divide_data(data, is_first_time):
    global PUBLIC_KEY
    if is_first_time:
        data = data +"%$%$" + PUBLIC_KEY
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

TIMEOUT = False
DATA_FROM_SERVICE = ""
PUBLIC_KEY, PRIVATE_KEY  =  onion_encryption_decryption.generate_keys((os.getcwd()), 'my')
ID_KEY  = hashlib.md5(PUBLIC_KEY).digest()

CURRENT_PKTS = {}#serial_num : pkt

UDP_IP = '10.0.0.6'#'192.168.1.22' #'192.168.43.207' #'10.0.0.5'
UDP_PORT = 50100
UDP_ADDR = (UDP_IP, UDP_PORT)

DIR_SERVER_IP = '10.0.0.6'#'192.168.1.22' #'192.168.43.207' #'10.0.0.5'
DIR_SERVER_PORT = 50010
BUFSIZ = 4096 
DIR_SERVER_ADDR = (DIR_SERVER_IP, DIR_SERVER_PORT)

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.connect(DIR_SERVER_ADDR)
has_done = False


while 1:
    onion_url = "S6"#raw_input("please enter the url->")
    print ('req:%s'%(onion_url,))
    server_sock.send(json_handler.create_json(onion_url))

    while not has_done:
        
        data = json_handler.recieve_json(server_sock.recv(BUFSIZ))   
        print data   
        if data["state"] == json_handler.STATE_FAILED: 
            print 'Check your url'
            break
        elif data["state"] == json_handler.STATE_SEND_AGAIN:
            server_sock.send(json_handler.create_json(onion_url))
            pass

        if manage_communication(UDP_ADDR, data["args"]):
            print 'done'
            #manage_communication(UDP_ADDR, data["args"])
        else:
            print 'faoled'

#communication with the server - END

