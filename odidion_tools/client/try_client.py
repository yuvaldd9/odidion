import client_tools
import os


def handle_data(data):
    f = open(r"C:\Users\yuval\Desktop\odidion\odidion\odidion_tools\client\rrr.txt", 'w')
    f.write(data)

c = client_tools.client("Yuval2")

c.ask_to_service("Service411")
s = raw_input('-->')

c.send(s)
for data in c.session():
    handle_data(data)
    s = raw_input('-->')
    c.send(s)

