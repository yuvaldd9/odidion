import socket
from scapy.all import *
import onion_packet_handler
import sys , os
import json_handler

if sys.stdout != sys.__stdout__:
    sys.stdout = sys.__stdout__



#Encryption Decryption - END
#handle onion-routing - START
def manage_communication(UDP_ADDR ,COMMUNICATION_DETAILS):
    """
    manage the part of the client in the onion routing process
    """
    service_public_key = COMMUNICATION_DETAILS["service_public_key"]
    communication_type = COMMUNICATION_DETAILS["communication_type"]
    routers = COMMUNICATION_DETAILS["routers"]


    #action = raw_input('[SYSTEM - ROUTING] what is the action with this site? --->')
    action = "Hello World"#temp for POC
    
    pkt = onion_packet_handler.create_onion_packet(routers, service_public_key, communication_type, action, UDP_ADDR)
    #pkt = IP(dst = "www.google.com")/UDP(dport = 50001)/"aaa"
    new_pkt = IP(pkt.build())
    #new_pkt.hexdump()
    hexdump(new_pkt)
    print len(new_pkt[UDP].payload)
    #send(pkt)
    send(new_pkt)

    return True


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
    onion_url = "POC SERVICE - ERAN IS SUCH A KING"#raw_input("please enter the url->")
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
        else:
            print 'faoled'

#communication with the server - END
