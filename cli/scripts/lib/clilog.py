####################################################################
########       Copyright (c) 2013-2020 BigSQL           ############
####################################################################

import os
import sys
import platform
import logging
import logging.handlers

## Our own library files ##########################################
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

this_platform_system = str(platform.system())
platform_lib_path = os.path.join(os.path.dirname(__file__), 'lib', this_platform_system)
if os.path.exists(platform_lib_path):
  if platform_lib_path not in sys.path:
    sys.path.append(platform_lib_path)

# Custom Logging
COMMAND = 15
DEBUG2 = 9


# Custom loglevel functions
def debug2(self, message, *args, **kws):
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(DEBUG2):
        self._log(DEBUG2, message, args, **kws)


def command(self, message, *args, **kws):
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(COMMAND):
        self._log(COMMAND, message, args, **kws)

####################################################################
########                    MAINLINE                      ##########
####################################################################
try:
    LOG_FILENAME = os.getenv('MY_LOGS')
    if not LOG_FILENAME:
      MY_HOME = os.getenv("MY_HOME")
      LOG_FILENAME = os.path.join(MY_HOME,"logs","cli_log.out")
    LOG_DIRECTORY = os.path.split(LOG_FILENAME)[0]
    LOG_LEVEL = int(os.getenv('MY_DEBUG_LEVEL', '-1'))

    if LOG_LEVEL is None or LOG_LEVEL == -1:
      LOG_LEVEL = COMMAND

    if not os.path.isdir(LOG_DIRECTORY):
      os.mkdir(LOG_DIRECTORY)

    # Set up a specific logger with our desired output level
    my_logger = logging.getLogger('cli_logger')

    logging.addLevelName(COMMAND, "COMMAND")
    logging.Logger.command = command

    logging.addLevelName(DEBUG2, "DEBUG2")
    logging.Logger.debug2 = debug2

    my_logger.setLevel(LOG_LEVEL)

    # Add the log message handler to the logger
    handler = logging.handlers.RotatingFileHandler(
                  LOG_FILENAME, maxBytes=10*1024*1024, backupCount=5)

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] : %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')

    handler.setFormatter(formatter)
    my_logger.addHandler(handler)


except (IOError, OSError) as err:
    print(str(err))
    if err.errno in (errno.EACCES, errno.EPERM):
      print("You must run as administrator/root.")
    exit()

