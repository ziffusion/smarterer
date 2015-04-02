import os, sys; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import re
import functools
import logging
import logging.handlers

from utils import config

##############################################################################
#
##############################################################################

class Logger(logging.getLoggerClass()):

    ### root logger
    logger = logging.getLogger()

    ### level
    logger.setLevel(config.log.level)

    ### format
    format = logging.Formatter(config.log.format + " : %(message)s")

    ### propagation
    logger.propagate = False

    ### handler: console
    handler = logging.StreamHandler()
    handler.setLevel(config.log.level)
    handler.setFormatter(format)

    logger.addHandler(handler)

    ### handler: file
    filename = os.path.join(config.path.logs, "system.log")

    if config.log.logrotate:
        handler = logging.handlers.WatchedFileHandler(filename)
    else:
        handler = logging.handlers.TimedRotatingFileHandler(filename, when="midnight", backupCount=config.log.backups)

    handler.setLevel(config.log.level)
    handler.setFormatter(format)

    logger.addHandler(handler)

##############################################################################
#
##############################################################################

logging.setLoggerClass(Logger)

##############################################################################
#
##############################################################################

log = logging.getLogger(config.log.name)
