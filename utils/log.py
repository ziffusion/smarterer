import os, sys; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import re
import functools
import logging
import logging.handlers

from utils import config, Context

##############################################################################
#
##############################################################################

class Logger(logging.getLoggerClass()):

    #########################################
    ### allow setting global context for logs
    ### context is added to all logs automatically

    def context_push(self, context):
        self.context.stack.append(context)
        self.context_set()

    def context_pop(self):
        self.context.stack.pop()
        self.context_set()

    def context_clear(self):
        self.context.stack = []
        self.context_set()

    def context_set(self, context=None):
        if context:
            self.context.stack = [ context ]
        context = " ".join(self.context.stack)
        self.context.text = "[{0}] ".format(context) if context else ""

    #########################################
    ### tracing decorator

    def trace(self, prefix=None):
        def decorator(func):
            text = "{0} : {1}".format(prefix, func.__name__) if prefix else func.__name__
            extra = {"_func" : func}
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                self.debug("ENTER : " + text, extra=extra)
                try:
                    ret = func(*args, **kwargs)
                    self.debug("EXIT : " + text, extra=extra)
                    return ret
                except Exception as ee:
                    self.debug("EXCEPT : " + text, extra=extra)
                    exc_info = sys.exc_info()
                    raise exc_info[0], exc_info[1], exc_info[2]
            return wrapper
        return decorator

    #########################################

    class Filter(logging.Filter):

        re_fix_module = re.compile(".*\.")

        def __init__(self, context):
            self.context = context

        def filter(self, record):
            ### fixup module and funcName for logs from wrapper functions
            ### they pass in _func in extra
            if hasattr(record, "_func"):
                record.module = self.re_fix_module.sub("", record._func.__module__)
                record.funcName = record._func.__name__
            record.context = self.context.text
            return True

    #########################################

    class LogContext(Context):

        def __init__(self):
            self.stack = []
            self.text = ""

    #########################################

    def __init__(self, name):

        ### parent
        super(self.__class__, self).__init__(name)

        ### context
        self.context = self.LogContext()

        ### filter
        self.addFilter(self.Filter(self.context))

    #########################################
    ### add handlers to the root logger only

    ### root logger
    logger = logging.getLogger()

    ### level
    logger.setLevel(config.log.level)

    ### format
    format = logging.Formatter(config.log.format + " : %(context)s%(message)s")

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
