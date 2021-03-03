import onion_encryption_decryption 
from scapy.all import *
import sys , os
import json_handler

if sys.stdout != sys.__stdout__:
    sys.stdout = sys.__stdout__

def divide_data(data):
    len_of_data = 128
    repeat_times = len(data)/len_of_data
    data_parts = []
    for i in xrange(repeat_times):
        data_parts.append(json_handler.create_reply_json(data[i*len_of_data:(i+1)*len_of_data], i))
    if data[(repeat_times)*len_of_data:]:
        data_parts.append(json_handler.create_reply_json(data[(repeat_times)*len_of_data:], repeat_times))
    data_parts.append(json_handler.create_reply_json(repeat_times+1, 'End'))

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
        send(pkt)
