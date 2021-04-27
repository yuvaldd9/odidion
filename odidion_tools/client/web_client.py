import client_tools

c = client_tools.Client("Yuval2", True)
try:
    c.ask_to_service("WEB1234")
except:
    print error



