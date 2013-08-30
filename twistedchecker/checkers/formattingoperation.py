import sys
import re
import ast

from logilab import astng
from logilab.common.ureports import Table
from logilab.astng import are_exclusive
from logilab.astng import node_classes

from pylint.interfaces import IASTNGChecker
from pylint.reporters import diff_string
from pylint.checkers.string_format import StringFormatChecker


class FormattingOperationChecker(StringFormatChecker):
    """
    When string formatting operations are used like formatString % values,
    we should always use a tuple for non-mapping values.
    """
    msgs = {
     'W9501': ('String formatting operations should always use a tuple'
               ' for non-mapping values',
               'Checking string formatting operations.'),
    }
    __implements__ = IASTNGChecker
    name = 'formattingoperation'
    options = ()

    def visit_binop(self, node):
        """
        Called when if a binary operation is found.
        Only check for string formatting operations.

        @param node: currently checking node
        """
        if node.op != "%":
            return
        pattern = node.left.as_string()
        valueString = node.right.as_string()

        try:
            # Split on %, then check if the left side is a number, in which
            # case it is obviously a modulo operation, and can be ignored
            # This only works if the number is on the left side, since then
            # it is def. not a formatting operation. If it's a variable,
            # well, that could be anything. Naive, but should catch at least
            # a few false positives.
            for item in pattern.split("%"):
                patternParsed = type(ast.literal_eval(item))
                if patternParsed in [float, int]:
                    return
        except:
            # If it can't parse it, it's obviously not a number
            pass

        # If the pattern has things like %(foo)s,
        # then the values can't be a tuple, so don't check for it.
        if "%(" not in pattern:
            tupleUsed = valueString.startswith('(')
            if not tupleUsed:
                self.add_message('W9501', node=node)
