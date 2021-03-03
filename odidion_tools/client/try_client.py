import client_tools
import os
import json

def handle_data(data, name):
    dir_pic = "C:\\Users\\yuval\\Desktop\\odidion\\odidion\\odidion_tools\\client\\Files\\"+ name + ".jpg"
    with open(dir_pic, 'wb') as f:
        f.write(data)
    return True

c = client_tools.client("Yuval2")

c.ask_to_service("S1")
s = raw_input('-->')
msg = str({
    "CODE" : "Ask For Photo",
    "ARGS" : {
        "Pic Name" : s
    }
})
print msg
c.send(msg)
for data in c.session():
    print len(data)
    if handle_data(data, s):
        s = raw_input('-->')
        msg = str({
        "CODE" : "Ask For Photo",
        "ARGS" : {
            "Pic Name" : s
            }
        })
        c.send(msg)

