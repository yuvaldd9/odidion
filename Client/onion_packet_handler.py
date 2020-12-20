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
    pkt_2_to_ren = generate_packet(routers['2'], routers['3'], communication_type, action, service_public_key)
    pkt_1_to_2 = generate_packet(routers['1'], routers['2'], communication_type, pkt_2_to_ren)
    pkt_client_to_1 = IP(src = UDP_ADDR[0], dst = routers['1']["router_ip"])/UDP(dport = routers['1']["router_port"])/Raw(load = pkt_1_to_2)
    
    """pkt_1_to_ren = generate_packet(routers['2'], routers['3'], communication_type, action, service_public_key)
    pkt_client_to_1 = IP(src = UDP_ADDR[0], dst = routers['2']["router_ip"])/UDP(dport = routers['2']["router_port"])/Raw(load = pkt_1_to_ren)"""
    #sport = UDP_ADDR[1] , sport = src_router[2]
    return pkt_client_to_1

def generate_packet(src_router, dest_router, communication_type, data, service_public_key = None):
    """
    returns the packet according to the routers

    service_public_key != None only in the first(last) packet
    """
    sym_key = onion_encryption_decryption.generate_sym_key()
    if service_public_key:
        
        enc_sym_key = onion_encryption_decryption.RSA_Encryption(sym_key, service_public_key)
        enc_data_service = onion_encryption_decryption.sym_encryption(data, sym_key)
        msg = enc_sym_key + enc_data_service
        data = msg
    
    l3_ip = IP(src = src_router["router_ip"], dst = dest_router["router_ip"])
    l4_UDP = UDP(dport = dest_router["router_port"])
    pkt = bytes(l3_ip/l4_UDP/Raw(load = data))

    return onion_encryption_decryption.encrypt_pkt(pkt, communication_type, sym_key, src_router["router_public_key"])





