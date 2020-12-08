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
from global_variables import *
from json_codes import *
import database_handler as db
import time

def refresh_router(router_name, load_level):
    """
    refresh the data structures of the server - last seens
    """
    print '[%s sent Live Nofitication]'%(router_name)
    print '[UPDATE LEVEL_LOAD]'
    #return (db.set_data(ONION_ROUTERS_DB_DIR, '''UPDATE onion_routers SET load = \'%s\', last_seen = \'%s\' WHERE router_name =\'%s\''''%(load_level,time.time(), router_name)))
    return CONNECTED_ROUTERS[router_name].refresh_last_seen(load_level)
def recieve_keep_alive(json):
    print 'IN RECIEVE KEEP', json["router_name"]
    #return response_keep_alive(json["router_name"])
    if refresh_router(json["router_name"], int(json["load"])):
        if "service_added" in json.keys():
            print '----------------------------deletinggggg-------------------------------'
            #CONNECTED_ROUTERS[json["router_name"]].add_service(SERVICES_UPDATES[json["router_name"]].get_details())
            del SERVICES_UPDATES[json["router_name"]]
        return response_keep_alive(json["router_name"])
    return (ONION_ROUTER_KEEP_ALIVE, STATE_FAILED)
    
    
def response_keep_alive(router_name):
    print "IN RESPONSE KEEP ALIVE", router_name
    return (ONION_ROUTER_KEEP_ALIVE, STATE_KEEP_ALIVE, {"Your Name is": router_name} if not router_name in SERVICES_UPDATES.keys() else ({'new_service':SERVICES_UPDATES[router_name]}))