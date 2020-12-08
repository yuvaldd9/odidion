import json
from json_codes import *

def create_json(json_code , state, args = None):
    msg = {
        "code" : json_code,
        "state" : state,
        "args" : args  
    }
    return json.dumps(msg)
