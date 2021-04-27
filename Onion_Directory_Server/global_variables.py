import verbose
import os
"""ONION_ROUTERS_DB_DIR = r"C:\Users\yuval\Desktop\odidion\odidion\Onion_Directory_Server\onion_routers.db"
SERVICES_DB_DIR =  r"C:\Users\yuval\Desktop\odidion\odidion\Onion_Directory_Server\services.db"
"""

ONION_ROUTERS_DB_DIR = "%s\\%s"%(os.getcwd(), "onion_routers.db")
SERVICES_DB_DIR =  "%s\\%s"%(os.getcwd(), "services.db")

CONNECTED_ROUTERS = {} #dict of router objects - router_name : (router obj, sock, last seen(keep alive))
SERVICES_ROUTERS = {} # "service name" : "router name" 
SERVICES = {} # service name : service object
SERVICES_UPDATES = {} #router name : the new service.

VB = verbose.Verbose("Directory_Server")