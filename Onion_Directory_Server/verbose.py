
import os
class verbose:
    """
    0 - Important - only the recieved data
    1 - Updates about sessions and recieved data
    2 - Everything"""
    
    VERBOSE_LEVEL = 0

    #general codes
    CLIENTS = 1
    REGISTER = 2
    KEEP_ALIVE = 3
    GENERAL_DATA = 4
    ERRORS = 5
    COMM_UPDATES = 6

    LOG_FILE_DIR = "%s\\%s"%(os.getcwd(), "log.txt")

    @staticmethod
    def log(data):
        if os.path.exists(verbose.LOG_FILE_DIR):
            mode = 'a'
        else:
            mode = 'w'
        with open(verbose.LOG_FILE_DIR,mode) as log_file:
            log_file.write("%s\n\r"%(data,))

    @staticmethod
    def set_level(level):
        verbose.VERBOSE_LEVEL = level
        verbose.log("VERBOSE LEVEL CHANGED TO: %s"%(level,))
    @staticmethod
    def print_data(data, data_topic):
        """
        Checks For The Right Output"""
        levels = {
            0 : [verbose.COMM_UPDATES, verbose.REGISTER, verbose.ERRORS],
            1 : [verbose.COMM_UPDATES, verbose.REGISTER, verbose.KEEP_ALIVE, verbose.ERRORS],
            2 : [verbose.COMM_UPDATES, verbose.REGISTER, verbose.KEEP_ALIVE, verbose.GENERAL_DATA, verbose.ERRORS],
            3 : [verbose.COMM_UPDATES, verbose.REGISTER, verbose.KEEP_ALIVE, verbose.GENERAL_DATA, verbose.CLIENTS, verbose.ERRORS]
        }
        verbose.log(data)
        if data_topic in levels[verbose.VERBOSE_LEVEL]:
            print data