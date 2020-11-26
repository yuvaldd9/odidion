from json_codes import *
from service import *
from global_variables import *
import keep_alive_handler
import json
import onion_routing
import onion_encryption_decryption

def handle_client(json_msg):
    topics = {
        CLIENT_REQ : client_req_handler.get_service()
    }
    return topics[json["main_topic"]](json_msg["args"]["service_name"])

def handle_service(json_msg):
    topics = {
        SERVICE_REGISTER : register_service() 
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

    print '[Adding Onion Router:%s:To The System]'%(json_msg["args"]["router_name"],)

    last_seen = time.time() 
    public_key_dir = onion_encryption_decryption.save_pukey(router_name, public_key)
    onion_router_details = dict(json_msg["args"])
    onion_router_details["public_key"] = public_key_dir  
    new_router = onion_router(onion_router_details)
    CONNECTED_ROUTERS[json_msg["args"]["router_name"]] = (new_router)
    #LAST_SEEN[router_name] = last_seen
    return (ONION_ROUTER_REGISTER, STATE_SUCCEED)

def register_service(details_dict):
    ren_details = onion_routing.choose_ren_point()
    new_service = service(details_dict, ren_details, SERVICES_DB_DIR)
    SERVICES_UPDATES[ren_details["router_name"]] = new_service.get_details()
    return (SERVICE_REGISTER, STATE_SUCCEED)




