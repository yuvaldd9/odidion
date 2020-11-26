import json
from json_codes import *

def create_json(topic, service_name):
    """

    returns the relevant json according to the topic of the message 
    
    {
        "type" : ONION_ROUTER_MSG_TYPE
        "main_topic" : topic
        "args" : args
    }
    """
    
    return json.dump({
        "type" : CLIENT_MSG_TYPE
        "main_topic" : CLIENT_REQ
        "args" : {"service_service": service_name}
    })
def recieve_json(json_data):
    return json.load(json_data)