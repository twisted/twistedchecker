import os
import sys

from logilab.common.ureports import TextWriter
from logilab.common.textutils import colorize_ansi

from pylint.interfaces import IReporter
from pylint.reporters import BaseReporter

class TestReporter(BaseReporter):
    """
    A reporter only used by unit tests.
    """
    __implements__ = IReporter
    extension = 'txt'


    def __init__(self, output=sys.stdout):
        """
        Initiate the the base reporter.

        @param output: output stream
        """
        BaseReporter.__init__(self, output)
        self._modules = {}
        self.resultMessages = {}


    def add_message(self, msg_id, location, msg):
        """
        Manage message of different type and in the context of path.
        It will save result messages.

        @param msg_id: message id
        @param location: detailed location information
        @param msg: text add_message
        """
        module, obj, line, col_offset = location[1:]
        if module not in self._modules:
            if module:
                self.writeln('************* Module %s' % module)
                self._modules[module] = 1
            else:
                self.writeln('************* %s' % module)
        if obj:
            obj = ':%s' % obj
        if self.include_ids:
            sigle = msg_id
        else:
            sigle = msg_id[0]
        self.resultMessages["line:%s" % line] = msg_id
        self.writeln('%s:%3s,%s%s: %s' % (sigle, line, col_offset, obj, msg))


    def _display(self, layout):
        """
        Launch layouts display.

        @param layout: layout of display
        """
        print >> self.out
        TextWriter().format(layout, self.out)
