import database_handler as db
from global_variables import *
import random
def choose_ren_point():
    """
    returns the ren point to the new service
    """
    #global CONNECTED_ROUTERS
    #return CONNECTED_ROUTERS[random.choice((CONNECTED_ROUTERS.keys()))][0]
    #(router obj, sock, last seen(keep alive))
    chosen_ren = random.choice(db.get_data(ONION_ROUTERS_DB_DIR, "SELECT router_name, ip from onion_routers WHERE is_available = 1"))
    return {"ren_name" : chosen_ren[0],
            "ren_ip" : chosen_ren[1]
           }
def choose_routers(ren_name):
    """
    this func return the current most available routers
    return an array of the objects.
    """
    global ONION_ROUTERS_DB_DIR
    routers = db.get_data(ONION_ROUTERS_DB_DIR, '''SELECT router_name, ip, port, load, public_key_dir from onion_routers''')
    print routers

    clients_routers = {'3' : filter(lambda details: details[0] == ren_name, routers)[0]}
    routers.remove(clients_routers['3'])

    most_availables_routers = sorted(routers, key = lambda details: details[3])
    clients_routers['1'] = most_availables_routers[0]
    clients_routers['2'] = most_availables_routers[1]

    for key in clients_routers.keys():
        clients_routers[key] = (clients_routers[key][0].encode('utf-8'), clients_routers[key][1].encode('utf-8'),\
                                         clients_routers[key][2], get_public_key(clients_routers[key][4].encode('utf-8')))


    print clients_routers
    return clients_routers