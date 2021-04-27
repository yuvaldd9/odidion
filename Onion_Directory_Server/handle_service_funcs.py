import onion_routing
import onion_encryption_decryption
import database_handler as db

from service import *
from global_variables import *
from json_codes import *

def register_service(details_dict):

    
    if db.check_if_value_exist(SERVICES_DB_DIR, 'services', 'service_name', details_dict["service_name"]):
        return SERVICE_REGISTER, STATE_FAILED, {"reason" : 'SERVICE NAME TAKEN'}

    VB.print_data( '[Adding new Service:%s:To The System]'%(details_dict["service_name"],), VB.REGISTER)
    
    
    
    public_key_dir = onion_encryption_decryption.save_pukey(details_dict["service_name"], details_dict["public_key"])
    service_details = details_dict
    service_details["public_key_dir"] = public_key_dir
    ren_details = onion_routing.choose_ren_point()
    new_service = service(service_details, ren_details, SERVICES_DB_DIR)
    SERVICES[service_details["service_name"]] = new_service
    SERVICES_UPDATES[ren_details["ren_name"]] = (SERVICE_REGISTER,new_service)
    print SERVICES_UPDATES
    return SERVICE_REGISTER, STATE_SUCCEED, None

def disconnect_service(details_dict):
    if db.check_if_value_exist(SERVICES_DB_DIR, 'services', 'service_name', details_dict["service_name"]):
        return SERVICE_DISCONNECT, STATE_FAILED, None
    print details_dict
    service_name = details_dict["service_name"]
    service_obj = SERVICES[service_name]
    real_special_key = db.get_data(SERVICES_DB_DIR, 'SELECT special_key from services')
    if real_special_key == details_dict["special_key"]:
        VB.print_data( '[Disconnecting Service:%s]'%(service_name,), VB.REGISTER)
        ren_details = service_obj.get_ren_name()
        SERVICES_UPDATES[ren_details] = (SERVICE_DISCONNECT, service_obj)
        return SERVICE_DISCONNECT, STATE_SUCCEED, None
    else:
        return SERVICE_DISCONNECT, STATE_FAILED, None
