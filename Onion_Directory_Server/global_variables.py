import verbose

ONION_ROUTERS_DB_DIR = r"C:\Users\yuval\Desktop\odidion\odidion\Onion_Directory_Server\onion_routers.db"
SERVICES_DB_DIR =  r"C:\Users\yuval\Desktop\odidion\odidion\Onion_Directory_Server\services.db"

CONNECTED_ROUTERS = {} #dict of router objects - router_name : (router obj, sock, last seen(keep alive))
PENDING_ROUTERS = {} #dict of the socks of the pending routers - sock:0/1 - 0 - tcp connected | 1 - waiting for k
LAST_SEEN = {} #dict of the routers last seen - last keep alive update 
SERVICES_ROUTERS = {} # "service name" : "router name" 
SERVICES = {} # service name : service object
SERVICES_UPDATES = {} #router name : the new service.

VB = verbose.verbose()
