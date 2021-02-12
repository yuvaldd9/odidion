import json
from json_codes import *

def create_json(topic, args):
    """

    returns the relevant json according to the topic of the message 
    
    {
        "type" : SERVICE_MSG_TYPE
        "main_topic" : topic
        "args" : args
    }
    """
    
    return json.dumps({
        "type" : SERVICE_MSG_TYPE,
        "main_topic" : topic,
        "args" : args
    })

def create_reply_json(data_sent, serial_num):
    return json.dumps({
        "serial_num" : serial_num,
        "data" : data_sent
    })

def recieve_json(json_data):
    try:
        return json.loads(json_data)
    except:
        return None