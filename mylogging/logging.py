import logging

class MyLogging:
    
    def __init__(self, logger_name: str= None, logfile_name: str= 'errors.log'):
        # create a custom logger
        self.logger = logging.getLogger(logger_name)
        self._configure_logger(logfile_name)
    
    def _configure_logger(self, logfile_name):
        # create handlers
        f_handler = logging.FileHandler(logfile_name)
        f_handler.setLevel(logging.ERROR)
        # TODO: should we use email handler as well?
        
        # create formatters and add it to handlers
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
        f_handler.setFormatter(f_format)
        
        # add handlers to the logger
        self.logger.addHandler(f_handler)
        

