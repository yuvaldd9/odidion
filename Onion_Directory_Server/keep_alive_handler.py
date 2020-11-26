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
def refresh_router(router_name, load_level):
    """
    refresh the data structures of the server - last seens
    """
    print '[%s sent Live Nofitication]'%(router_name)
    print '[UPDATE LEVEL_LOAD]'
    return (db.set_data(ONION_ROUTERS_DB_DIR, '''UPDATE onion_routers SET load = \'%s\', last_seen = \'%s\' WHERE router_name =\'%s\''''%(load_level,time.time(), router_name)))
    
def recieve_keep_alive(json):
    
    if refresh_router(json["args"]["router_name"], int(json["args"]["load"])):
        return response_keep_alive(json["args"]["router_name"])
    return (ONION_ROUTER_KEEP_ALIVE, STATE_FAILED)
    
    
def response_keep_alive(router_name):
    return (ONION_ROUTER_KEEP_ALIVE, STATE_KEEP_ALIVE, (SERVICES_UPDATES[router_name]))