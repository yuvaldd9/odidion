import time 
import keep_alive_handler
import handle_service_funcs
import onion_encryption_decryption
import client_req_handler
import database_handler as db

from json_codes import *
from global_variables import *
from onion_router_class import *

def handle_client(json_msg):
    topics = {
        CLIENT_REQ : client_req_handler.get_service
    }
    return topics[json_msg["main_topic"]](json_msg["args"]["service_name"])

def handle_service(json_msg):
    topics = {
        SERVICE_REGISTER : handle_service_funcs.register_service,
        SERVICE_DISCONNECT : handle_service_funcs.disconnect_service
    }
    return topics[json_msg["main_topic"]](json_msg["args"])


def handle_router(json_msg):
    topics = {
        ONION_ROUTER_REGISTER : register_router, 
        ONION_ROUTER_KEEP_ALIVE : keep_alive_handler.recieve_keep_alive
    }
    return topics[json_msg["main_topic"]](json_msg["args"])

def register_router(json_msg):
    """
    {
        "code":
        "state":
        "args":
            {
                "router_name":
                "clients_port":
                "public_key":
                "ip" : 
            }
    }
    """
    if db.check_if_value_exist(ONION_ROUTERS_DB_DIR, 'onion_routers', 'router_name', json_msg["router_name"]):
        return ONION_ROUTER_REGISTER, STATE_FAILED, {"reason" : 'SERVICE NAME TAKEN'}
    VB.print_data( '[Adding Onion Router:%s:To The System]'%(json_msg["router_name"],), VB.REGISTER)

    last_seen = time.time() 
    public_key_dir = onion_encryption_decryption.save_pukey(json_msg["router_name"], json_msg["public_key"])
    onion_router_details = json_msg
    onion_router_details["public_key_dir"] = public_key_dir  
    new_router = onion_router(onion_router_details)
    CONNECTED_ROUTERS[json_msg["router_name"]] = (new_router)
    return ONION_ROUTER_REGISTER, STATE_SUCCEED, None





