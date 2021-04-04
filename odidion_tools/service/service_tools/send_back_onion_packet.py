import onion_encryption_decryption 
from scapy.all import *
import sys , os
import json_handler

if sys.stdout != sys.__stdout__:
    sys.stdout = sys.__stdout__

scapy_sock = conf.L3socket()

def divide_data(data, is_web_header):
    json_generator = json_handler.web_header_json if is_web_header else json_handler.create_reply_json 
    print json_handler
    len_of_data = int(128*1.5)
    repeat_times = len(data)/len_of_data
    data_parts = []
    for i in xrange(repeat_times):
        data_parts.append(json_generator(data[i*len_of_data:(i+1)*len_of_data], i))
    if data[(repeat_times)*len_of_data:]:
        data_parts.append(json_generator(data[(repeat_times)*len_of_data:], repeat_times))
    if not is_web_header:
        data_parts.append(json_handler.create_reply_json(repeat_times+1, 'End'))

    return data_parts

def generate_packet(id_key, client_public_key, back_ip, back_port, data, is_web_header):
    if not data:
        data = 'DATA RECIEVED'
    messages = divide_data(data, is_web_header)
    sym_key = onion_encryption_decryption.generate_sym_key()
    for data in messages:
        msg = id_key+':'+ onion_encryption_decryption.RSA_Encryption(sym_key, client_public_key) \
            + onion_encryption_decryption.sym_encryption(data, sym_key)
        pkt = IP(dst = back_ip, tos = 2)/UDP(dport = back_port)/Raw(load = msg)
        scapy_sock.send(pkt)
