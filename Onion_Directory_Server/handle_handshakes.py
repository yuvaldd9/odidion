import re

SERVICE_SYN_MSG = 'register service'
def handle_client_service(clientsock, addr):
    """
    handle client, service communication
    """
    print 'handling comm -> ', addr
    #is_service = False
    handshake_state = {
        "syn" : False,
        "syn-ack" : False,
        "ack" : False
    }

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

def 