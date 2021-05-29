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
    return str({
        "serial_num" : serial_num,
        "data" : data_sent
    })
    
    """json.dumps({
        "serial_num" : serial_num,
        "data" : data_sent
    }, encoding='latin1')"""
def recieve_json(json_data):
    try:
        return json.loads(json_data)
    except:
        return None

"""def web_header_json(data, _):
    return str({
        "serial_num" : 'WEB REPLIES',
        "data" : data
    })"""