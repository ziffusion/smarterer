"""
MODEL: see utils.config
"""

##############################################################################
#
##############################################################################

include = ["system-install.py", "system-hostname.py", "system-custom.py"]

##############################################################################
#
##############################################################################

ports = Section()

ports.http = 8080

ports.flash = 10843

##############################################################################
#
##############################################################################

server = Section()

server.debug = True

server.dump = True

server.secret = "3tZKw6D#wU@1THDy"

server.session = Section()

server.session.cookie = "session"

server.session.lifetime = 86400 # 24 hours

##############################################################################
#
##############################################################################

log = Section()

log.name = "smarterer"

log.level = logging.DEBUG

log.format = "%(asctime)s %(levelname)8s %(module)24s %(funcName)24s %(lineno)4s"

log.logrotate = True

log.backups = 3
