from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from cryptography.fernet import Fernet
import binascii
import sys , os


if sys.stdout != sys.__stdout__:
    sys.stdout = sys.__stdout__

KEYS_LEN = 192#256#384

def generate_keys(MAIN_DIR, name):
    """
    create/ load the keys of the router

    returns (PUBLIC_KEY, PRIVATE_KEY, keyPair)
    """
    
     
    PRIVATE_KEY_DIR = "%s\keys\%s_private_key_%s.pem"%(MAIN_DIR,name,"PRIVATE_KEY",)
    PUBLIC_KEY_DIR = "%s\keys\%s_public_key_%s.pem"%(MAIN_DIR,name,"PUBLIC_KEY",)
    print PUBLIC_KEY_DIR
    if os.path.exists(repr(PRIVATE_KEY_DIR)) and os.path.exists(PUBLIC_KEY_DIR):
        PRIVATE_KEY = RSA.importKey(open(repr(PRIVATE_KEY_DIR) , 'rb')).export_key()
        PUBLIC_KEY = RSA.importKey(open(repr(PUBLIC_KEY_DIR), 'rb')).export_key()
    else:
        keyPair = RSA.generate(256*6)

        PUBLIC_KEY = keyPair.publickey().export_key()
        PRIVATE_KEY = keyPair.exportKey()

        public_key_file = open((PUBLIC_KEY_DIR),'wb')
        public_key_file.write(PUBLIC_KEY)
        public_key_file.close()
        
        private_key_file = open((PRIVATE_KEY_DIR),'wb')
        private_key_file.write(PRIVATE_KEY)
        private_key_file.close()
        


    return (PUBLIC_KEY, PRIVATE_KEY)

def RSA_Decryption(hex_pkt, PRIVATE_KEY):
    """
    get the encrypted part of the packet and decrypt it.
    """
    #print len(hex_pkt), type(hex_pkt),'\nPKT: ', hex_pkt,"\n", len(bytes((hex_pkt))),'\n',bytes((hex_pkt))
    decryptor = PKCS1_OAEP.new(str_to_RSAKey(PRIVATE_KEY))
    decrypted_Packet = decryptor.decrypt((hex_pkt))

    return decrypted_Packet
def RSA_Encryption(data, public_key):
    """
    returns the encrypted data according to the public key
    """
    
    pubKey = str_to_RSAKey(public_key)
    encryptor = PKCS1_OAEP.new(pubKey)
    encrypted = encryptor.encrypt(data)
    return encrypted
def sym_decryption(data, sym_key):
    f1 = Fernet(sym_key)
    return (f1.decrypt(data))

def sym_encryption(data, sym_key):
    f1 = Fernet(sym_key)
    return f1.encrypt((data))

#Encryption Decryption - START
def generate_sym_key():
    """
    returns the sym-key - FERNET - str length = 44
    """
    return Fernet.generate_key()
def str_to_RSAKey(key_str):
    return RSA.importKey(key_str)

def encrypt_pkt(pkt, communication_type, sym_key, public_key):
    """
    Encrypt the packet

    sym_key = string(FERNET KEY - generate_sym_key())

    return (public_key)sym_key+(sym_key)pkt
    """
    global KEYS_LEN

    encrypted_pkt = sym_encryption((pkt), sym_key)
    encrypted_key_comm_header = RSA_Encryption(bytes(sym_key + str(communication_type)), public_key)
    return   encrypted_key_comm_header + encrypted_pkt

def decrypt_data_service(data, PRIVATE_KEY):
    #print type(data)
    #print "UDP LOAD:\n",data
    
    global KEYS_LEN
    try:
        key_comm_header = data[:KEYS_LEN]
        dec_sym_key = RSA_Decryption(key_comm_header,PRIVATE_KEY)
        encrypted_data = (data[KEYS_LEN:])

        #print '---length of encrypted sym key      ', len(key_comm_header)
        return sym_decryption(encrypted_data,dec_sym_key)
    except:
        return "FAILED IN DECRYPTION"