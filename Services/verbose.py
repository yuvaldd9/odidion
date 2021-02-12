class verbose:
    """
    0 - Important - only the recieved data
    1 - Updates about sessions and recieved data
    2 - Everything"""

    #print level
    VERBOSE_LEVEL = 0
    
    #general codes
    RECIEVED_DATA = 0
    PKTS_DATA = 1
    SESSION_DATA = 2
    GENERAL_DATA = 3
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
    def print_data(data, data_topic):
        """
        Checks For The Right Output"""

        levels = {
            0 : [verbose.RECIEVED_DATA]
            1 : [verbose.RECIEVED_DATA, verbose.SESSION_DATA]
            2 : [verbose.RECIEVED_DATA, verbose.SESSION_DATA, verbose.PKTS_DATA]
            3 : [verbose.RECIEVED_DATA, verbose.SESSION_DATA, verbose.PKTS_DATA, verbose.GENERAL_DATA]
        }
        verbose.log(data)
        if data_topic in levels[verbose.VERBOSE_LEVEL]:
            print data


