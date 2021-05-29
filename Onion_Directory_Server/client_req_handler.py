import database_handler as db
import onion_encryption_decryption 
import keep_alive_handler

from global_variables import *
from json_codes import *

def get_service(service_name):
    """
    returns the service details(ip) and the relavent routers
    """
    try:
        service_details = db.get_data(SERVICES_DB_DIR, '''SELECT ren_ip, ren_name, special_key, public_key_dir, serial_number from services WHERE service_name = \'%s\''''%service_name)[0]
        #service_data = {'serial_number':service_details[4]}
        service_data = {}
        service_public_key = onion_encryption_decryption.get_public_key(service_details[3])
        service_data["service_public_key"] = service_public_key.encode('utf-8')
        service_data["communication_type"] = 0
        service_data["routers"], service_data["serial_number"] = choose_routers(service_name)#service_details[1]) 
        VB.print_data("Sent Details About %s"%(service_name,), VB.CLIENTS)
        print service_data
        return CLIENT_REQ, STATE_SUCCEED, service_data
    except:
        return CLIENT_REQ, STATE_FAILED, None

def choose_routers(service_name):
    """
    this func return the current most available routers
    return an array of the objects.
    """
    
    routers = db.get_data(ONION_ROUTERS_DB_DIR, '''SELECT router_name, ip, port, load, public_key_dir, last_seen from onion_routers''')
    
    routers = keep_alive_handler.check_avaiable_routers(routers)

    service_details = db.get_data(SERVICES_DB_DIR, '''SELECT ren_name, serial_number from services WHERE service_name = \'%s\''''%service_name)[0]
    
    ren_name = service_details[0]
    serial_number = service_details[1]

    clients_routers = {'3' : filter(lambda details: details[0] == ren_name, routers)[0]}
    routers.remove(clients_routers['3'])

    most_availables_routers = sorted(routers, key = lambda details: details[3])
    clients_routers['1'] = most_availables_routers[0]
    clients_routers['2'] = most_availables_routers[1]

    for key in clients_routers.keys():
        clients_routers[key] = {
                                    "router_name" : clients_routers[key][0].encode('utf-8'),
                                    "router_ip" : clients_routers[key][1].encode('utf-8'),
                                    "router_port" : clients_routers[key][2],
                                    "router_public_key" : onion_encryption_decryption.get_public_key(clients_routers[key][4].encode('utf-8'))
                                }
    return clients_routers, serial_number