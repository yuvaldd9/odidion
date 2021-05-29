import database_handler as db
from global_variables import *
def choose_ren_point():
    """
    returns the ren point to the new service
    """

    online_routers = (db.get_data(ONION_ROUTERS_DB_DIR, "SELECT router_name, ip, load from onion_routers WHERE is_available = 1"))
    online_routers = sorted(online_routers, key = lambda details: details[2])
    
    chosen_ren = online_routers[0]
    return {"ren_name" : chosen_ren[0],
            "ren_ip" : chosen_ren[1]
           }
