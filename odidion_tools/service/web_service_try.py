from service_tools import Service

web_dir = r"C:\Users\yuval\Desktop\odidion\odidion\odidion_tools\service\website\my_first_flask.py"
s = Service(web_dir)

if s.bind_and_set_service('WEB122', "10.0.0.7", 50021):
    print 'binded'
    s.register_service()
    print 'registered'

    for id_key, data in s.recieve_from_clients():
        print id_key, data
