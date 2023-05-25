import logging,os,sys
from .config import config
def set_logger(logger: logging.Logger,check_level=False):
    log_config = config.get("log")
    if not log_config:
        return logger
    __log_level = logging._nameToLevel[log_config.get('level', 'DEBUG')] 
    if check_level:
        return logger.setLevel(__log_level)
    __log_file = log_config.get('file', None)

    debug = config.get("debug", False)
    logger.name = logger.name or log_config.get("name", 'iRails')
    if __log_file:
        __log_file = os.path.abspath(__log_file)

    log_format = log_config.get(
        "msgfmt", "%(asctime)s %(name)s:%(levelname)s:%(message)s")
    datefmt = log_config.get("datefmt", "%Y-%M-%d %H:%M:%S")
    file_handler = None
    if __log_file:
        if debug:
            try:
                os.remove(__log_file)
            except:
                pass

        file_handler = logging.FileHandler(__log_file, mode='a')
        file_handler.setLevel(__log_level)
        file_handler.setFormatter(logging.Formatter(
            fmt=log_format, datefmt=datefmt))
        if not file_handler in logger.handlers:
            logger.addHandler(file_handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(__log_level)
    handler.setFormatter(logging.Formatter(fmt=log_format, datefmt=datefmt))
    if not handler in logger.handlers:
        logger.addHandler(handler) 
    _log.setLevel(__log_level)
_log =   logging.getLogger()
_log.setLevel(logging._nameToLevel['DEBUG'])

set_logger(_log)
_log.info("initing log.")