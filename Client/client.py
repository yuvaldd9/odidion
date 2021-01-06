import socket
from scapy.all import *
import onion_packet_handler
import sys , os
import json_handler
import random
import time
import onion_encryption_decryption
import hashlib

if sys.stdout != sys.__stdout__:
    sys.stdout = sys.__stdout__



#Encryption Decryption - END
#handle onion-routing - START

def handle_packet(onion_pkt):
    udp_data = onion_pkt[UDP].payload.build()
    print udp_data
    #try:

    print '----RECIEVED PACKET---'
    seperator_index = udp_data.index(':')
    id_key = udp_data[:seperator_index]
    key_comm_header = udp_data[seperator_index+1:seperator_index +1+ onion_encryption_decryption.KEYS_LEN]
    dec_sym_key = onion_encryption_decryption.RSA_Decryption(key_comm_header,PRIVATE_KEY)
    
    encrypted_pkt = bytes(udp_data[seperator_index +1+ onion_encryption_decryption.KEYS_LEN:])
    
    print (onion_encryption_decryption.sym_decryption(encrypted_pkt,dec_sym_key))


def manage_communication(UDP_ADDR ,COMMUNICATION_DETAILS):
    """
    manage the part of the client in the onion routing process
    """
    global ID_KEY
    service_public_key = COMMUNICATION_DETAILS["service_public_key"]
    communication_type = COMMUNICATION_DETAILS["communication_type"]
    routers = COMMUNICATION_DETAILS["routers"]


    #action = raw_input('[SYSTEM - ROUTING] what is the action with this site? --->')
    s = ""
    for i in xrange(50):
        s += str(i)
    action = divide_data(s)#temp for Testing
    print (action)
    for part in action:

        pkt = onion_packet_handler.create_onion_packet(routers, service_public_key, communication_type, part, UDP_ADDR, str(COMMUNICATION_DETAILS["serial_number"]), ID_KEY)
        #pkt = IP(dst = "www.google.com")/UDP(dport = 50001)/"aaa"
        new_pkt = IP(pkt.build())
        #new_pkt.hexdump()
        ##hexdump(new_pkt)
        print len(new_pkt[UDP].payload)
        #send(pkt)
        send(new_pkt)
        time.sleep(0.2)
    return True

def divide_data(data):
    global PUBLIC_KEY
    data = data +"%$%$" + PUBLIC_KEY
    len_of_data = 15
    repeat_times = len(data)/len_of_data
    data_parts = []
    for i in xrange(repeat_times):
        data_parts.append(json_handler.create_service_json(data[i*len_of_data:(i+1)*len_of_data], i))
    if data[(repeat_times)*len_of_data:]:
        data_parts.append(json_handler.create_service_json(data[(repeat_times)*len_of_data:], repeat_times))
    data_parts.append(json_handler.create_service_json(repeat_times+1, 'End'))

    return data_parts

def packet_trace(routers):
    """
    track the packet
    1st router - sends check to the client.
    2nd router - sends check to 1st.
    3rd router - sends check to 2nd.
    """
    pass
#handle onion-routing - END

#communication with the server - START


PUBLIC_KEY, PRIVATE_KEY  =  onion_encryption_decryption.generate_keys((os.getcwd()), 'my')
ID_KEY  = hashlib.md5(PUBLIC_KEY).digest()



UDP_IP = '10.0.0.3'#'192.168.1.22' #'192.168.43.207' #'10.0.0.5'
UDP_PORT = 50100
UDP_ADDR = (UDP_IP, UDP_PORT)

DIR_SERVER_IP = '10.0.0.3'#'192.168.1.22' #'192.168.43.207' #'10.0.0.5'
DIR_SERVER_PORT = 50010
BUFSIZ = 4096 
DIR_SERVER_ADDR = (DIR_SERVER_IP, DIR_SERVER_PORT)

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.connect(DIR_SERVER_ADDR)
has_done = False


while 1:
    onion_url = "S112"#raw_input("please enter the url->")
    print ('req:%s'%(onion_url,))
    server_sock.send(json_handler.create_json(onion_url))

    while not has_done:
        
        data = json_handler.recieve_json(server_sock.recv(BUFSIZ))      
        if data["state"] == json_handler.STATE_FAILED: 
            print 'Check your url'
            break
        elif data["state"] == json_handler.STATE_SEND_AGAIN:
            server_sock.send(json_handler.create_json(onion_url))
            pass

        if manage_communication(UDP_ADDR, data["args"]):
            print 'done'
            sniff(filter = "udp", prn = handle_packet , count = 0)
        else:
            print 'faoled'

#communication with the server - END

