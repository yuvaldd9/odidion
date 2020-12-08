import json
from json_codes import *

def create_json(topic, args):
    """

    returns the relevant json according to the topic of the message 
    
    {
        "type" : ONION_ROUTER_MSG_TYPE
        "main_topic" : topic
        "args" : args
    }
    """
    return json.dumps({
        "type" : ONION_ROUTER_MSG_TYPE,
        "main_topic" : topic,
        "args" : args
    })
def recieve_json(json_data):
    try:
        return json.loads(json_data)
    except:
        return None