import os, sys; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

from utils import log, config

##############################################################################
#
##############################################################################

class Test(unittest.TestCase):

    def setUp(self):
        config._debug = True

    def tearDown(self):
        pass

    def test_access(self):
        log.debug("ports.http={0}".format(config.ports.http))
