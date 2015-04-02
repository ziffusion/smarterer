import logging

"""
MODEL: see utils.config
"""

##############################################################################
#
##############################################################################

include = ["system-hostname.py", "system-custom.py"]

##############################################################################
#
##############################################################################

path.data = os.path.join(path.root, 'data')

path.logs = os.path.join(path.root, 'logs')

path.run = os.path.join(path.root, 'run')

path.www = Section()

path.www.static = os.path.join(os.path.join(path.root, 'www'), 'static')

path.www.templates = os.path.join(os.path.join(path.root, 'www'), 'templates')

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

db = Section()

db.path = "/tmp/smarterer.db"

db.uri = "sqlite:///" + db.path

db.data = "data.csv"

##############################################################################
#
##############################################################################

app = Section()

app.limit = 100

##############################################################################
#
##############################################################################

log = Section()

log.name = "smarterer"

log.level = logging.DEBUG

log.format = "%(asctime)s %(levelname)8s %(module)24s %(funcName)24s %(lineno)4s"

log.logrotate = False

log.backups = 3
