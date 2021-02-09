class verbose:
    """
    0 - Important - only the recieved data
    1 - Updates about sessions and recieved data
    2 - Everything"""

    #general codes
    RECIEVED_DATA = 0
    PKTS_DATA = 1
    SESSION_DATA = 2
    GENERAL_DATA = 3
    ERRORS = 4
    @staticmethod
    def print_data(data, data_topic, verbose_level):
        """
        Checks For The Right Output"""

        levels = {
            0 : [verbose.RECIEVED_DATA, verbose.ERRORS],
            1 : [verbose.RECIEVED_DATA, verbose.SESSION_DATA, verbose.ERRORS],
            2 : [verbose.RECIEVED_DATA, verbose.SESSION_DATA, verbose.PKTS_DATA, verbose.ERRORS],
            3 : [verbose.RECIEVED_DATA, verbose.SESSION_DATA, verbose.PKTS_DATA, verbose.GENERAL_DATA, verbose.ERRORS]
        }

        if data_topic in levels[verbose_level]:
            print data


