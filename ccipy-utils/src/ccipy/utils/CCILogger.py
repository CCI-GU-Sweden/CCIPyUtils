import inspect
import logging
import os
import sys
from pathlib import Path


class CustomFormatter(logging.Formatter):

    green ="\x1b[32m" 
    grey = "\x1b[38m"
    yellow = "\x1b[33m"
    red = "\x1b[31m"
    magenta = "\x1b[35m"
    bold_red = "\x1b[31m"
    reset = "\x1b[0m"
    #format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    form = '%(process)d: %(asctime)s -%(levelname)s-: %(message)s'
    dbg_form = '%(process)d:[%(module)s]-%(asctime)s -%(levelname)s-: %(message)s'

    FORMATS = {
        logging.DEBUG: magenta + dbg_form + reset,
        logging.INFO: green + form + reset,
        logging.WARNING: yellow + form + reset,
        logging.ERROR: red + form + reset,
        logging.CRITICAL: bold_red + form + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        if record.levelno == logging.DEBUG:
            record.module = self.get_calling_module(record)
        formatter = logging.Formatter(log_fmt,datefmt='%Y%m%d %H:%M:%S')
        return formatter.format(record)

    def get_calling_module(self, record):
        
        frame = inspect.currentframe()
        while frame:
            co = frame.f_code
            filename = os.path.basename(co.co_filename)
            if filename not in ('logging/__init__.py', 'logger.py') and "logging/__init__.py" not in co.co_filename:  # skip logging infra and your logger module
                break
            frame = frame.f_back
        if frame:
            module = os.path.splitext(os.path.basename(frame.f_code.co_filename))[0]
        else:
            module = record.module

        return module


class CCILogger:

    from typing import Optional

    _logger: Optional[logging.Logger] = None

    @classmethod
    def _setup_logger(cls, log_file_name: str, app_name: str, level=logging.DEBUG):

        #check logfile existance
        if not Path(log_file_name).is_file():
            Path(log_file_name).parent.mkdir(parents=True, exist_ok=True)
            Path(log_file_name).touch()
            
        logging.getLogger(app_name)
        fmtStr = '%(process)d: %(asctime)s -%(levelname)s-: %(message)s'
        
        logging.basicConfig(filename=log_file_name, level=level,
                            format=fmtStr)
        localLogger = logging.StreamHandler(sys.stdout)
        llFmt = CustomFormatter()
        localLogger.setFormatter(llFmt)
        localLogger.setLevel(level)
        logging.getLogger(app_name).addHandler(localLogger)
            
        str_level = logging.getLevelName(level)
        cls.info(f"Logger set up with level: {str_level}")
        
        cls._logger = logging.getLogger(app_name)

    @classmethod
    def log(cls, level: str, msg: str):
        if level == "info":
            cls.info(msg)
        elif level == "debug" or level == "dbg":
            cls.debug(msg)
        elif level == "warning" or level == "warn":
            cls.warning(msg)
        elif level == "error" or level == "err":
            cls.error(msg)
        else:
            cls.info(msg)
          
    @classmethod
    def info(cls, msg: str):
        cls.logger().info(msg)
    
    @classmethod
    def warning(cls, msg: str):
        cls.logger().warning(msg)

    @classmethod
    def error(cls, msg: str):
        cls.logger().error(msg)

    @classmethod
    def debug(cls, msg: str):
        cls.logger().debug(msg)

    @classmethod
    def logger(cls):
        if cls._logger is not None:
            return cls._logger
        else:
            raise Exception("Logger not initialized, call 'setup_logger' first")
