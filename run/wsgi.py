import os, sys; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import server.endpoints
from server.webapp import webapp

##############################################################################
#
##############################################################################

if __name__ == "__main__":
    webapp.run()
