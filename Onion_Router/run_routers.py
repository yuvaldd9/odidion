import os
import thread

def run_router(router_details):
    os.system('cmd /k \"%s\"')%('C:\Users\yuval\Desktop\odidion\odidion\Onion_Router\onion_router.py %s %s')%(router_details[0], router_details[1])

def main():
    for router_details in [('r1', '50001'),('r2', '50002'),('r3', '50003')]:
        thread.start_new_thread(run_router, (router_details,))
if __name__ == '__main__':
    main()
