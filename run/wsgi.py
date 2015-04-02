import os, sys; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import server.endpoints_admin
import server.endpoints_app
import server.endpoints_test
 
from server.webapp import Webapp

application = Webapp.flask  ### for mod_wsgi

##############################################################################
#
##############################################################################

if __name__ == "__main__":
    Webapp.run()
