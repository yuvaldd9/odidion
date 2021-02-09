import client_tools

def handle_data(data):
    print data
    pass

c = client_tools.client("Yuval2")

c.ask_to_service("Service1")
s = raw_input('-->')

c.send(s)
for data in c.session():
    handle_data(data)
    s = raw_input('-->')
    c.send(s)

