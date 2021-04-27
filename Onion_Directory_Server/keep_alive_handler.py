"""
keep alive - json:
{
    "type" : "onion_router"
    "main_topic" : "keep_alive"
    "args" :
        {
            "router_name" : router_name
            "load" : load_level
        }
}

response:

{
    "state" : "keep_alive"
    "args" :
        {
            "new_services":
                {
                    services_details....
                }
        }
}
"""
import database_handler as db
import onion_routing
import time

from global_variables import *
from json_codes import *
from service import *


def refresh_router(router_name, load_level):
    """
    refresh the data structures of the server - last seens
    """
    VB.print_data('[%s sent Live Nofitication]'%(router_name,) , VB.KEEP_ALIVE)
    #return (db.set_data(ONION_ROUTERS_DB_DIR, '''UPDATE onion_routers SET load = \'%s\', last_seen = \'%s\' WHERE router_name =\'%s\''''%(load_level,time.time(), router_name)))
    return CONNECTED_ROUTERS[router_name].refresh_last_seen(load_level)

def recieve_keep_alive(json):
    print json
    if refresh_router(json["router_name"], int(json["load"])):
        if "service_added" in json.keys():
            print 'added'
            SERVICES_UPDATES[json["router_name"]][1].add_serial_number(json["service_added"])
            del SERVICES_UPDATES[json["router_name"]]
        elif "service_deleted" in json.keys():
            print 'deleted'
            del SERVICES_UPDATES[json["router_name"]]

        return response_keep_alive(json["router_name"])
    return (ONION_ROUTER_KEEP_ALIVE, STATE_FAILED)
    
    
def response_keep_alive(router_name):

    if not router_name in SERVICES_UPDATES.keys():
        json_args = {"Your Name is": router_name}
    else:
        
        service_details = SERVICES_UPDATES[router_name][1].get_details()
        response_op = {
            SERVICE_REGISTER : {'new_service' : service_details},
            SERVICE_DISCONNECT : {'delete_service' : service_details}
        }
        
        json_args = response_op[SERVICES_UPDATES[router_name][0]]
    
    return (ONION_ROUTER_KEEP_ALIVE, STATE_KEEP_ALIVE, json_args)


def check_avaiable_routers(routers):
    """
    set the unavaiable routers as offline
    returns the online routers
    """
    offline = filter(lambda router_details:  time.time() - float(router_details[5]) > 100,\
                                routers)
    online = list(set(routers) - set(offline))
    offline_names = map(lambda router_details:  router_details[0], offline)

    for router_name in offline_names:
        CONNECTED_ROUTERS[router_name].close_router()
        router_services = CONNECTED_ROUTERS[router_name].get_router_services()
        for service_name, service_details in router_services.items():
            ren_details = onion_routing.choose_ren_point()
            changed_service = service(service_details, ren_details, SERVICES_DB_DIR)
            SERVICES_UPDATES[ren_details["ren_name"]] = changed_service
        del CONNECTED_ROUTERS[router_name]
    
    return online

