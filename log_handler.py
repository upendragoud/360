import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os

class CustomLogRecord(logging.LogRecord):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the module attribute
        self.custom_module = self.pathname.split(os.path.sep)[-2]  # This grabs the directory name that the module is in

def custom_logger_factory(*args, **kwargs):
    return CustomLogRecord(*args, **kwargs)

logging.setLogRecordFactory(custom_logger_factory)

def get_logger():
    logger = logging.getLogger('maturity_spectrum_360')
    logger.setLevel(logging.DEBUG)

    if not os.path.exists('log'):
        os.makedirs('log')

    file_handler = RotatingFileHandler(os.path.join('log', 'application.log'), maxBytes=10 * 1024 * 1024, backupCount=1)
    time_handler = TimedRotatingFileHandler(os.path.join('log', 'application.log'), when='midnight')
    formatter = logging.Formatter('%(asctime)s - %(name)s - [%(custom_module)s] - %(module)s.%(funcName)s() - %(levelname)s - %(message)s')

    file_handler.setFormatter(formatter)
    time_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(time_handler)

    return logger
