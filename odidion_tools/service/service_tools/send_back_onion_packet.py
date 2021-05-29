import onion_encryption_decryption 
from scapy.all import *
import sys , os
import json_handler

if sys.stdout != sys.__stdout__:
    sys.stdout = sys.__stdout__

scapy_sock = conf.L3socket()

def divide_data(data):
    json_generator = json_handler.create_reply_json  #json_handler.web_header_json if is_web_header else 
    len_of_data = 45
    repeat_times = len(data)/len_of_data
    data_parts = []
    is_trail = 0

    for i in xrange(repeat_times):
        data_parts.append(json_generator(data[i*len_of_data:(i+1)*len_of_data], i))
    if data[(repeat_times)*len_of_data:]:
        is_trail = 1
        data_parts.append(json_generator(data[(repeat_times)*len_of_data:], repeat_times))
    data_parts.append(json_handler.create_reply_json(repeat_times + is_trail, 'End'))

    return data_parts

def generate_packet(id_key, client_public_key, back_ip, back_port, data):
    if not data:
        data = 'DATA RECIEVED'
    messages = divide_data(data)
    sym_key = onion_encryption_decryption.generate_sym_key()
    for data in messages:
        msg = id_key+':'+ onion_encryption_decryption.RSA_Encryption(sym_key, client_public_key) \
            + onion_encryption_decryption.sym_encryption(data, sym_key)
        pkt = IP(dst = back_ip, tos = 2)/UDP(dport = back_port)/Raw(load = msg)
        scapy_sock.send(pkt)
