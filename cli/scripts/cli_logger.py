import logging
import os

class CLILogger:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    YELLOW = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    TICK = "\u2714"
    CROSS = "\u2718"
    INFO = "\u24D8"
    WARNING = "\u26A0"

    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        LOG_FILENAME = os.getenv('MY_LOGS')
        if not LOG_FILENAME:
            MY_HOME = os.getenv("MY_HOME")
            LOG_FILENAME = os.path.join(MY_HOME, "data", "logs","cli_log.out")

        # Define and add console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        file_handler = logging.FileHandler(LOG_FILENAME)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def error(self, message):
        self.logger.error(f"{self.FAIL}{self.CROSS} {message}{self.ENDC}")

    def warning(self, message):
        self.logger.warning(f"{self.YELLOW}{self.WARNING} {message}{self.ENDC}")

    def debug(self, message):
        self.logger.debug(f"{message}")

    def alert(self, message):
        self.logger.info(f"{self.OKBLUE}{self.INFO} {message}{self.ENDC}")

    def success(self, message):
        self.logger.info(f"{self.OKGREEN}{self.TICK} {message}{self.ENDC}")

    def info(self, message):
        self.logger.info(f"{message}")