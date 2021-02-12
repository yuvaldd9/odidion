from service_tools import service as s 


def handle_data(data):
    dirs = {
        '1' : r"C:\Users\yuval\Desktop\didi_store\main_server.py"
    }
    with open(dirs['1'], 'rb') as f:
        a =  f.read()
    return a

if s.bind_and_set_service('Service411', '192.168.0.100', 50021):
    print 'binded'
    s.register_service()
    print 'registered'

    for id_key, data in s.recieve_from_clients():
        print id_key, data
        s.send_to_client(id_key, handle_data(data))
