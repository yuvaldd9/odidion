import time
from service_tools import Service

web_dir = r"C:\Users\yuval\Desktop\odidion\odidion\odidion_tools\service\website\my_first_flask.py"
s = Service()#web_dir)

if s.bind_and_set_service('W1',"10.0.0.10", 50023):
    print 'binded'
    if s.register_service():
        print 'registered'
        """time.sleep(7)
        print 'cliosee'
        s.disconnect_network()
        """
        for id_key, data in s.recieve_from_clients():
            print id_key, data
    else:
        print 'lose'