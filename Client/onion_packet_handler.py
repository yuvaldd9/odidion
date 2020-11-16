import onion_encryption_decryption 
from scapy.all import *
import sys , os


if sys.stdout != sys.__stdout__:
    sys.stdout = sys.__stdout__

def create_onion_packet(routers, service_public_key, communication_type, action, UDP_ADDR):
    """
    build the packet according to the current
    routers, keys, ip and the action(GET/POST/SET)

    for the poc - action = the msg data

    routers = {
    '1' : (router_name, ip, port, public_key)
    .
    .
    .

    }
    """
    print routers
    """pkt_2_to_ren = generate_packet(routers['2'], routers['3'], communication_type, action, service_public_key)
    pkt_1_to_2 = generate_packet(routers['1'], routers['2'], communication_type, pkt_2_to_ren)
    pkt_client_to_1 = IP(src = UDP_ADDR[0], dst = routers['1'][1])/UDP(dport = routers['1'][2])/Raw(load = pkt_1_to_2)"""

    pkt_1_to_ren = generate_packet(routers['2'], routers['3'], communication_type, action, service_public_key)
    pkt_client_to_1 = IP(src = UDP_ADDR[0], dst = routers['2'][1])/UDP(dport = routers['2'][2])/Raw(load = pkt_1_to_ren)
    #sport = UDP_ADDR[1] , sport = src_router[2] ,
    return pkt_client_to_1

def generate_packet(src_router, dest_router, communication_type, data, service_public_key = None):
    """
    returns the packet according to the routers

    service_public_key != None only in the first(last) packet
    """
    print "-----start of %s to %s"%(src_router[0], dest_router[0])
    sym_key = onion_encryption_decryption.generate_sym_key()
    print "sym key type: ->   ", type(sym_key), "----",sym_key
    if service_public_key:
        ren_sym_key = onion_encryption_decryption.generate_sym_key()
        msg = onion_encryption_decryption.RSA_Encryption(data, service_public_key)
        data = msg
        """ren_pkt = bytes(IP()/UDP()/Raw(load = msg))
        data = onion_encryption_decryption.encrypt_pkt(ren_pkt, communication_type, ren_sym_key, dest_router[3])"""
    l3_ip = IP(src = src_router[1], dst = dest_router[1])
    l4_UDP = UDP(dport = dest_router[2])
    pkt = bytes(l3_ip/l4_UDP/Raw(load = data))
    print src_router[0], '\n',src_router[3]
    print "-----PACKET of %s to %s"%(src_router[0], dest_router[0])
    hexdump(pkt)
    return onion_encryption_decryption.encrypt_pkt(pkt, communication_type, sym_key, src_router[3])





