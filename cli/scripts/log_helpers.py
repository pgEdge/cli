import logging
import logging.handlers
import os

class bcolours:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    YELLOW = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class characters:
    TICK = "\u2714"
    CROSS = "\u2718"
    INFO = "\u24D8"
    WARNING = "\u26A0"



class CustomFormatter(logging.Formatter):
    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG2: bcolours.OKBLUE + self.fmt + bcolours.ENDC,
            logging.DEBUG: bcolours.OKCYAN + self.fmt + bcolours.ENDC,
            loggin.COMMAND: self.fmt,
            logging.INFO: self.fmt,
            logging.SUCESS: bcolours.OKGREEN + characters.TICK + " " + self.fmt + bcolours.ENDC,
            logging.WARNING: bcolours.YELLOW + characters.WARNING + " " + self.fmt + bcolours.ENDC,
            logging.ERROR: bcolours.FAIL + characters.CROSS + " " + self.fmt + bcolours.ENDC,
            logging.CRITICAL: bcolours.FAIL + self.fmt + bcolours.ENDC
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

# Custom Logging
COMMAND = 15
SUCESS = 21
DEBUG = 10
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

def sucess(self, message, *args, **kws):
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(SUCESS):
        self._log(SUCESS, message, args, **kws)

logging.addLevelName(COMMAND, "COMMAND")
logging.Logger.command = command

logging.addLevelName(DEBUG2, "DEBUG2")
logging.Logger.debug2 = debug2

logging.addLevelName(SUCESS, "SUCESS")
logging.Logger.sucess = sucess

my_logger = logging.getLogger()
LOG_FILENAME = os.getenv('MY_LOGS')
if not LOG_FILENAME:
   MY_HOME = os.getenv("MY_HOME")
   LOG_FILENAME = os.path.join(MY_HOME,"logs","cli_log.out")
LOG_DIRECTORY = os.path.split(LOG_FILENAME)[0]

handler = logging.handlers.RotatingFileHandler(
                  LOG_FILENAME, maxBytes=10*1024*1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] : %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
my_logger.addHandler(handler)

# Console Logger
fmt = '%(message)s'
stdout_handler = logging.StreamHandler()
stdout_handler.setLevel(16)
stdout_handler.setFormatter(CustomFormatter(fmt))
my_logger.addHandler(stdout_handler)
