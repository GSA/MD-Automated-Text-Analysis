import logging
from logging.handlers import RotatingFileHandler

class MyLogging():
    
    def __init__(self, loggername: str, log_filename: str = 'MyLogs.log', level= logging.WARNING, addl_handlers: list = []):
        self.logger = logging.getLogger(loggername)
        # configure the default file handler   
        default_handler = RotatingFileHandler(log_filename, maxBytes=1000000, backupCount=3)
        formatter = logging.Formatter('*** %(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
        default_handler.setFormatter(formatter)
        self.logger.addHandler(default_handler)
        # add additional handlers
        for handler in addl_handlers:
            self.logger.addHandler(handler)
            
    