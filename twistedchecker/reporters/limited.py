import os
import sys
import operator
import pickle

from logilab.common.textutils import colorize_ansi
from pylint.interfaces import IReporter
from pylint.reporters import BaseReporter
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


    def __init__(self, output=sys.stdout):
        """
        Initiate the the limited reporter.
        Load a list of allowed messages. 

        @param output: output stream
        """
        TextReporter.__init__(self, output)
        self._loadAllowedMessages()
        

    def _updateMessageCache(self):
        """
        Update cache of messages when a new test is added.
        """
        pathTests = os.path.join(twistedchecker.abspath, "functionaltests")
        testfiles = reduce(operator.add,
                           [map(lambda f: os.path.join(pathDir, f), files)
                            for pathDir, _, files in os.walk(pathTests)]
                          )
        lastTestModified = max(map(os.path.getmtime,testfiles))
        lastCacheModified = (os.path.getmtime(self.pathMessageCache)
                             if os.path.exists(self.pathMessageCache)
                             else 0)
        if lastTestModified > lastCacheModified:
            # collect all message ids, and write into cache
            messagesAllowed = set()
            for testfile in testfiles:
                firstline = open(testfile).readline().strip()
                if (firstline.startswith("#") and "enable" in firstline
                                              and ":" in firstline):
                    messages = firstline.split(":")[1].strip().split(",")
                    messagesAllowed.update(messages)
            pickle.dump(messagesAllowed, open(self.pathMessageCache,"w"))


    def _loadAllowedMessages(self):
        """
        Load allowed messages from tests and cache in configuration folder.
        """
        self._updateMessageCache()
        self.messagesAllowed = pickle.load(open(self.pathMessageCache))


    def add_message(self, msg_id, location, msg):
        """
        Manage message of different type and in the context of path.
        """
        if msg_id in self.messagesAllowed:
            TextReporter.add_message(self, msg_id, location, msg)
