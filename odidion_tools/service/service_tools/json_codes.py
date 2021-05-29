#msg_type:
CLIENT_MSG_TYPE = "client"
ONION_ROUTER_MSG_TYPE = "onion_router"
SERVICE_MSG_TYPE = "service"

#main_topic
CLIENT_REQ = "request_service"

ONION_ROUTER_REGISTER = "register"
ONION_ROUTER_KEEP_ALIVE = "keep_alive"

SERVICE_REGISTER = "register"
SERVICE_DISCONNECT = "disconnect"

#response_states
STATE_SEND_AGAIN = "send_again"
STATE_FAILED = "failed"
STATE_SUCCEED = "succeed"
STATE_KEEP_ALIVE = "keep_alive"