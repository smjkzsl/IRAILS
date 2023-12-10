import logging,os
from .config import config
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(name)s] %(levelname)s:%(message)s")

def get_logger(name:str="",level=False)->logging.Logger:
    log_config = config.get("log")
    if not name:
        name = log_config.get("name")
    _loger = logging.getLogger(name=name)
    
    if not log_config:
        return _loger
    
    if not level:
        level = logging._nameToLevel[log_config.get('level', 'DEBUG')] 
    _log_file = log_config.get('file', None) 
    _loger.setLevel(level=level)
    log_format = log_config.get(
        "msgfmt", "%(asctime)s %(name)s:%(levelname)s:%(message)s")
    datefmt = log_config.get("datefmt", "%Y-%M-%d %H:%M:%S")
    if _log_file:
        _log_file = os.path.abspath(_log_file)  
        file_handler = logging.FileHandler(_log_file, mode='a')
        file_handler.setLevel(level=level)
        file_handler.setFormatter(logging.Formatter(
            fmt=log_format, datefmt=datefmt))
        if not file_handler in _loger.handlers:
            _loger.addHandler(file_handler)
            
    return _loger
 
 