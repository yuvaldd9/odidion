import os

cmd = 'py -2 C:\Users\yuval\Desktop\odidion\odidion\Onion_Router\onion_router.py %s %s %s'%('r3', '50003', '2')
os_cmd = 'cmd /k \"%s\"'%(cmd,)

os.chdir("C:\Users\yuval\Desktop\odidion\odidion\Onion_Router")
os.system(os_cmd)
    

    
