
#  Copyright 2022-2024 PGEDGE  All rights reserved. #

import os
import sys

MY_LOGS = util.getreqenv("MY_LOGS")
LOG_FILENAME = f"{MY_LOGS}/cli_log.out"


class ConsoleLogger(object):
    """
        Class to redirect the stdout to logfile
    """
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open(LOG_FILENAME, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass

