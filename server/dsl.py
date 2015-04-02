import os, sys; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pyparsing as pp

from utils import log, config

##############################################################################
#
##############################################################################

class Dsl(object):

    def __init__(self):

        #########################################

        rhs_op_cmp = (
            pp.oneOf("== !=") +
            pp.oneOf("+ - * /")
        )

        rhs_op_in = (
            "||" +
            pp.Group(pp.OneOrMore(pp.oneOf("+ - * /")))
        )

        expr_op = pp.Group(
            "op" +
            (rhs_op_cmp | rhs_op_in)
        )

        rhs_num_cmp = (
            pp.oneOf("== != > >= < <=") +
            pp.Word(pp.nums)
        )

        rhs_num_in = (
            "||" +
            pp.Group(pp.OneOrMore(pp.Word(pp.nums)))
        )

        expr_num = pp.Group(
            pp.oneOf("n0 n1 n2") +
            (rhs_num_cmp | rhs_num_in)
        )

        expr = (expr_op | expr_num)

        self.grammar_where = expr + pp.ZeroOrMore(pp.Suppress("&&") + expr) + pp.LineEnd()

        #########################################

        col = pp.OneOrMore(pp.oneOf("op n0 n1 n2"))

        self.grammar_sort = col + pp.LineEnd()

    def where(self, text):
        return self.grammar_where.parseString(text)

    def sort(self, text):
        return self.grammar_sort.parseString(text)

##############################################################################
#
##############################################################################

dsl = Dsl()
