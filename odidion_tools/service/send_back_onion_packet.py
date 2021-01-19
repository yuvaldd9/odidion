import onion_encryption_decryption 
from scapy.all import *
import sys , os


if sys.stdout != sys.__stdout__:
    sys.stdout = sys.__stdout__


def generate_packet(id_key, client_public_key, back_ip, back_port, data):

    print type(back_ip)

    sym_key = onion_encryption_decryption.generate_sym_key()
    msg = id_key+':'+ onion_encryption_decryption.RSA_Encryption(sym_key, client_public_key) \
        + onion_encryption_decryption.sym_encryption(data, sym_key)
    pkt = IP(dst = back_ip, tos = 2)/UDP(dport = back_port)/Raw(load = msg)
    pkt.show()
    send(pkt)
