import os


class Verbose():
    VERBOSE_CHANGES = 0
    RECIEVED_DATA = 1
    PKTS_DATA = 2
    SESSION_DATA = 3
    GENERAL_DATA = 4
    ERRORS = 0
    KEEP_ALIVE = 0
    verbose_level = 0

    def __init__(self, name = None):
        self.name = name
        if name:
            self.log_file_dir = "%s\\%s"%(os.getcwd(), "%s_log.txt"%(self.name,))
            self._create_log_file()
        else:
            self.log_file_dir = ''
    def print_data(self, data ,log_level):        
        pass
        """if log_level <= Verbose.verbose_level:
            print data

        with open(self.log_file_dir, 'a') as log_file:
            log_file.write("%s | %s | %s\n\r"%(self.name, log_level ,data))"""

    def set_name(self, new_name):
        """
        this func should be called once!
        """

        self.name = new_name
        self.log_file_dir = "%s\\%s"%(os.getcwd(), "%s_log.txt"%(self.name,))
        self._create_log_file()

    def _create_log_file(self):
        if not os.path.isfile(self.log_file_dir):
            f = open(self.log_file_dir, 'w') 
            f.close()

    def set_level(self, verbose_level):
        Verbose.verbose_level = verbose_level
        self.print_data(Verbose.VERBOSE_CHANGES, "VERBOSE LEVEL CHANGED TO: %s"%(verbose_level,))