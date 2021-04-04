import verbose 

#onion routing vars - Start
LOAD_LEVEL = 0
ROUTING_PROCESSES = {} #(src_ip, dst_ip, comm_type)
SERVICES = {} # {service_name : {ip, port, communication_type}} dict of  dictionaries

#onion routing vars - Start
SERIAL_NUM_SERVICES = 0
ROUTER_NAME = None #cmd input
CLIENTS_PORT = None #cmd input
VERBOSE_LEVEL = None #cmd input
ROUTER_IP = "10.0.0.7"#'192.168.1.22' #'192.168.43.207' #"10.0.0.7"
SERVICES_DB_DIR = None

DIR_SERVER_IP = "10.0.0.7"#'192.168.1.22' #'192.168.43.207' #"10.0.0.7"
DIR_SERVER_PORT = 50010
BUFSIZ = 1024
DIR_SERVER_ADDR = (DIR_SERVER_IP, DIR_SERVER_PORT)

VB = verbose.Verbose()