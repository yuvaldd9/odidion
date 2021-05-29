import json
from json_codes import *

def create_json(service_name):
    """

    returns the relevant json according to the topic of the message 
    
    {
        "type" : ONION_ROUTER_MSG_TYPE
        "main_topic" : topic
        "args" : args
    }
    """
    
    return json.dumps({
        "type" : CLIENT_MSG_TYPE,
        "main_topic" : CLIENT_REQ,
        "args" : {"service_name": service_name}
    })
def recieve_json(json_data):
    return json.loads(json_data)

def create_service_json(data, serial_num):
    return json.dumps({
        "sn" : serial_num,
        "d" : data,
    })