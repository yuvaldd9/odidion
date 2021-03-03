import client_tools
import os
import json

def handle_data(data):
    print data
    return True


c = client_tools.client("Yuval2")

c.ask_to_service("S0")
s = raw_input('-->')
c.send(s)
for data in c.session():
    print len(data)
    if handle_data(data):
        s = raw_input('-->')
        c.send(s)

