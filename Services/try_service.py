from service_tools import Service
import json

def handle_data(data):
    dirs = {
        'king' : r"C:\Users\yuval\Desktop\odidion\odidion\odidion_tools\service\Files\king.jpg",
        'money' : r"C:\Users\yuval\Desktop\odidion\odidion\odidion_tools\service\Files\money.jpg",
        'nature' : r"C:\Users\yuval\Desktop\odidion\odidion\odidion_tools\service\Files\nature.jpg",
        'trump' : r"C:\Users\yuval\Desktop\odidion\odidion\odidion_tools\service\Files\trump.jpg"
    }
    with open(dirs[data["Pic Name"]], 'rb') as f:
        a =  f.read()
    print type(a)
    return a
s = Service()
if s.bind_and_set_service('S1',"10.0.0.10", 50021):
    print 'binded'
    s.register_service()
    print 'registered'

    for id_key, data in s.recieve_from_clients():
        print id_key, data
        data = eval(data)
        s.send_to_client(id_key, handle_data(data["ARGS"]))
