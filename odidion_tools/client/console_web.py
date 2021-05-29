import client_tools
import thread


def start_web_session(web_name, port):
    try:
        c = client_tools.Client("Yuval2", True, port)
        c.ask_to_service(web_name)
    except:
        print 'ERROR OCCURED -->  ',web_name

if __name__ == '__main__':
    port = 51000
    while 1:
        web_name = raw_input('YOUR DESIRED WEB\n--->')
        thread.start_new_thread(start_web_session, (web_name, port))
        port += 1






