from socket import *
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import binascii
import onion_encryption_decryption 
import os


def register_service(sock, addr, comm_type):
    """
    handle the first communication with the dir_server
    comm_type: - 0-UDP 1-TCp
    """
    global PUBLIC_KEY
    global SERVICE_NAME


    process_flag = 0 # 0 - start, 1 - sent req , 2 - done
    was_connected = False
    sock.send('register service')
    while process_flag != 2:
        data = sock.recv(BUFSIZ)
        if not data:
            break
        elif data == "details pls":
            process_flag = 1
            #the message here is- details:name:ip:port:comm_type:public key
            sock.send("details:%s:%s:%s:%s:%s"%(SERVICE_NAME, addr[0], addr[1], 0, PUBLIC_KEY))
        elif data == "k" and process_flag == 1:
            process_flag = 2
            was_connected = True
        elif data == "Service Exist" and process_flag == 0:
            was_connected = True
        else:
            break
    sock.close()
    return was_connected


UDP_IP = '192.168.1.22' #'192.168.43.207' #'10.0.0.5'
UDP_PORT = 50005
BUFSIZ = 1024


DIR_SERVER_IP =  '192.168.1.22' #'192.168.43.207' #'10.0.0.5'
DIR_SERVER_PORT = 50010
DIR_SERVER_ADDR = (DIR_SERVER_IP,DIR_SERVER_PORT)

DIR_SERVER_SOCKET = socket(AF_INET, SOCK_STREAM)
DIR_SERVER_SOCKET.connect(DIR_SERVER_ADDR)


SERVICE_NAME = "POC SERVICE - ERAN IS SUCH A KING"
sock = socket(AF_INET,SOCK_DGRAM)
UDP_ADDR = (UDP_IP, UDP_PORT)
sock.bind(UDP_ADDR)
PUBLIC_KEY, PRIVATE_KEY  =  onion_encryption_decryption.generate_keys((os.getcwd()), SERVICE_NAME) 
if register_service(DIR_SERVER_SOCKET, UDP_ADDR, 0):

    while True:
        print 'waiting...'
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes

        print("received message: %s" % onion_encryption_decryption.RSA_Decryption(data, PRIVATE_KEY))
else:
    print "Error Occured"