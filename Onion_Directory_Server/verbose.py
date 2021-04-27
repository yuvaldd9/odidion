import os


class Verbose():
    VERBOSE_CHANGES = 0
    CLIENTS = 1
    REGISTER = 1
    KEEP_ALIVE = 3
    GENERAL_DATA = 3
    ERRORS = 0
    COMM_UPDATES = 2
    
    verbose_level = 0

    def __init__(self, name):
        self.name = name
        self.log_file_dir = "%s\\%s"%(os.getcwd(), "%s_log.txt"%(name,))
        
        f = open(self.log_file_dir, 'w') 
        f.close()
    def get_log_dir(self):
        return self.log_file_dir
    def print_data(self, data ,log_level): 

        if log_level <= Verbose.verbose_level:
            print data

        with open(self.log_file_dir, 'a') as log_file:
            log_file.write("%s | %s | %s\n\r"%(self.name, log_level ,data))


    def set_level(self, verbose_level):
        Verbose.verbose_level = verbose_level
        self.print_data(Verbose.VERBOSE_CHANGES, "VERBOSE LEVEL CHANGED TO: %s"%(verbose_level,))