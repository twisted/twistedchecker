import os
import sys

from pylint.interfaces import IReporter
from pylint.reporters.text import TextReporter
import twistedchecker


class LimitedReporter(TextReporter):
    """
    A reporter only used by unit tests.
    """
    __implements__ = IReporter
    messagesAllowed = None
    extension = 'txt'
    pathMessageCache = os.path.join(twistedchecker.abspath,
                                    "configuration", "messages.cache")

    def __init__(self, messagesAllowed, output=sys.stdout):
        """
        Initiate the the limited reporter.
        Load a list of allowed messages.

        @param output: output stream
        """
        TextReporter.__init__(self, output)
        self.messagesAllowed = messagesAllowed


    def handle_message(self, msg):
        """
        Manage message of different type and in the context of path.
        """
        if msg.msg_id in self.messagesAllowed:
            super(LimitedReporter, self).handle_message(msg)
