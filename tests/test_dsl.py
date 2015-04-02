import os, sys; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import pyparsing as pp

from utils import log, config
from server.dsl import dsl

##############################################################################
#
##############################################################################

class Test(unittest.TestCase):

    def setUp(self):
        config._debug = True

    def tearDown(self):
        pass

    def test_dsl(self):
        with self.assertRaises(pp.ParseException):
            exprs = dsl.where("opp || /+-*")

        with self.assertRaises(pp.ParseException):
            exprs = dsl.where("op ||| /+-*")

        with self.assertRaises(pp.ParseException):
            exprs = dsl.where("op || /+-*%")

        exprs = dsl.where("op || /+-*")
        exprs = dsl.where("op == +")
        exprs = dsl.where("op != +")
        exprs = dsl.where("n0 == 123")
        exprs = dsl.where("n0 != 123 && n2 > 24 && op == + && op || + - * && n0 || 12 13 14")

        exprs = dsl.sort("op")
        exprs = dsl.sort("op n0 n1")
