from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from cryptography.fernet import Fernet
import binascii
import sys , os


if sys.stdout != sys.__stdout__:
    sys.stdout = sys.__stdout__

KEYS_LEN = 192

def generate_keys(MAIN_DIR, name):

    PRIVATE_KEY_DIR = "%s\keys\%s_private_key_%s.pem"%(MAIN_DIR,name,"PRIVATE_KEY",)
    PUBLIC_KEY_DIR = "%s\keys\%s_public_key_%s.pem"%(MAIN_DIR,name,"PUBLIC_KEY",)
    
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
        private_key_file.write(PUBLIC_KEY)
        private_key_file.close()

    return (keyPair.publickey().export_key(), keyPair.export_key())

def RSA_Decryption(hex_pkt, public_key):
    decryptor = PKCS1_OAEP.new(str_to_RSAKey(public_key))
    decrypted_Packet = decryptor.decrypt((hex_pkt))

    return decrypted_Packet
def RSA_Encryption(data, private_key):
    pubKey = str_to_RSAKey(private_key)
    encryptor = PKCS1_OAEP.new(pubKey)
    encrypted = encryptor.encrypt(data)
    return encrypted

def sym_decryption(data, sym_key):
    f1 = Fernet(sym_key)
    return (f1.decrypt(data))

def sym_encryption(data, sym_key):
    f1 = Fernet(sym_key)
    return f1.encrypt((data))

def generate_sym_key():
    return Fernet.generate_key()

def str_to_RSAKey(key_str):
    return RSA.importKey(key_str)

def save_pukey(name, public_key):
    pukey_dir = "%s\keys\%s.pem"%(os.getcwd(), name)
    try:
        public_key_file = open((pukey_dir),'wb')
        public_key_file.write(public_key)
        public_key_file.close()
        return pukey_dir
    except:
        return ''

def get_public_key(key_path):
    try:
        with open(key_path, 'r') as f:
            key = f.read()
        return key
    except:
        return '' 