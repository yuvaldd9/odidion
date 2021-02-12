from service_tools import service as s 


def handle_data(data):
    try:
        i = int(data)
    except:
        i = 0
    return str(i + 1)


if s.bind_and_set_service('Service1', '192.168.0.100', 50021):
    print 'binded'
    s.register_service()
    print 'registered'

    for id_key, data in s.recieve_from_clients():
        print id_key, data
        s.send_to_client(id_key, handle_data(data))
