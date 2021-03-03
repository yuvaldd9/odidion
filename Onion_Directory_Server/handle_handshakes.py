from json_codes import *
from service import *
from global_variables import *
from onion_router_class import *
import keep_alive_handler
import json
import onion_routing
import onion_encryption_decryption
import client_req_handler
import time 
import jwt

def handle_client(json_msg):
    topics = {
        CLIENT_REQ : client_req_handler.get_service
    }
    return topics[json_msg["main_topic"]](json_msg["args"]["service_name"])

def handle_service(json_msg):
    topics = {
        SERVICE_REGISTER : register_service
    }
    return topics[json_msg["main_topic"]](json_msg["args"])
    """
        handle client, service communication

        print 'handling comm -> ', addr
        #is_service = False


        while 1:
            data = clientsock.recv(BUFSIZ)
            print "data:", data
            if not data:
                print "ending communication with",addr
                break
            elif data[0:4] == 'req:':
                print 'req'
                print data[4:]
                msg = str(get_service(data[4:]))
                print len(msg)
                clientsock.send(msg)
                print 'sentttt'
            elif data == SERVICE_SYN_MSG:
                print 'register service'
                handshake_state["syn"] = True
                clientsock.send("details pls")
                handshake_state["syn-ack"] = True
                #service_process_flag += 1
            elif data[:6] == "details" and handshake_state["syn-ack"]:
                print 'in add service'
                service_details = (data.split(':')) #details:service name:real ip:clients port:communication type(0-UDP 1-TCP):public_key
                msg = add_service(service_details[1:])
                is_service = False
                service_process_flag = 0
                clientsock.send(msg)
                handshake_state["ack"]
                break
            else:
                #until there will be more options to the protocol
                break
        clientsock.close()
    """

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

    VB.print_data( '[Adding Onion Router:%s:To The System]'%(json_msg["router_name"],), VB.REGISTER)

    last_seen = time.time() 
    public_key_dir = onion_encryption_decryption.save_pukey(json_msg["router_name"], json_msg["public_key"])
    onion_router_details = json_msg
    onion_router_details["public_key_dir"] = public_key_dir  
    new_router = onion_router(onion_router_details)
    CONNECTED_ROUTERS[json_msg["router_name"]] = (new_router)
    #LAST_SEEN[router_name] = last_seen
    return ONION_ROUTER_REGISTER, STATE_SUCCEED, None

def register_service(details_dict):

    VB.print_data( '[Adding new Service:%s:To The System]'%(details_dict["service_name"],), VB.REGISTER)
    public_key_dir = onion_encryption_decryption.save_pukey(details_dict["service_name"], details_dict["public_key"])
    service_details = details_dict
    service_details["public_key_dir"] = public_key_dir

    ren_details = onion_routing.choose_ren_point()

    new_service = service(service_details, ren_details, SERVICES_DB_DIR)
    SERVICES_UPDATES[ren_details["ren_name"]] = new_service
    return SERVICE_REGISTER, STATE_SUCCEED, None




