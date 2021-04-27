from .service_tools import Service as s 
import json

def handle_data(data):
    with open(r"C:\Users\yuval\Desktop\odidion\odidion\odidion_tools\service\Files\service_data.txt", 'a') as f:
        f.write(data+'\n')
    return ''


with open(r"C:\Users\yuval\Desktop\odidion\odidion\odidion_tools\service\Files\service_data.txt", 'a') as f:
    f.write("CLIENTS MESSAGES\n")

if s.bind_and_set_service('S0', "192.168.1.26", 50022):
    print 'binded'
    s.register_service()
    print 'registered'

    for id_key, data in s.recieve_from_clients():
        print id_key, data
        s.send_to_client(id_key, handle_data(data))
