# -*- test-case-name: twistedchecker.test.test_runner -*-
import sys
import os

from pylint.lint import PyLinter

import twistedchecker
from twistedchecker.reporters.limited import LimitedReporter

class Runner():
    """
    Run and control the checking process.
    """
    outputStream = None
    linter = None
    # Customized checkers.
    checkers = ("header.HeaderChecker",
                "modulename.ModuleNameChecker",
                "pep8format.PEP8Checker")
    allowedMessagesFromPylint = ("C0111",
                                 "C0103",
                                 "C0301",
                                 "W0311",
                                 "W0312")

    def __init__(self):
        """
        Initialize C{PyLinter} object, and load configuration file.
        """
        self.linter = PyLinter(())
        # register standard checkers.
        self.linter.load_default_plugins()
        # read configuration.
        pathConfig = os.path.join(twistedchecker.abspath,
                                  "configuration", "pylintrc")
        self.linter.read_config_file(pathConfig)
        # now we can load file config and command line, plugins (which can
        # provide options) have been registered.
        self.linter.load_config_file()
        allowedMessages = self.registerCheckers()
        # set default output stream to stderr
        self.setOutput(sys.stderr)
        # set default reporter to limited reporter
        self.setReporter(LimitedReporter(allowedMessages))


    def setOutput(self, stream):
        """
        Set the stream to output result of checking.

        @param stream: output stream, defaultly it should be stdout
        """
        self.outputStream = stream
        sys.stdout = stream


    def setReporter(self, reporter):
        """
        Set the reporter of pylint.

        @param reporter: reporter used to show messages
        """
        self.linter.set_reporter(reporter)


    def displayHelp(self):
        """
        Output help message of twistedchecker.
        """
        self.outputStream.write("""---\nHELP INFOMATION\n""")


    def registerCheckers(self):
        """
        Register all checkers of TwistedChecker to C{PyLinter}.

        @return: a list of allowed messages
        """
        allowedMessages = list(self.allowedMessagesFromPylint)
        for strChecker in self.checkers:
            modname, classname = strChecker.split(".")
            strModule = "twistedchecker.checkers.%s" % modname
            checker = getattr(__import__(strModule,
                                        fromlist=["twistedchecker.checkers"]),
                             classname)
            instanceChecker = checker(self.linter)
            allowedMessages += instanceChecker.msgs.keys()
            self.linter.register_checker(instanceChecker)

        self.restrictCheckers(allowedMessages)
        return set(allowedMessages)


    def unregisterChecker(self, checker):
        """
        Remove a checker from the list of registered checkers.

        @param checker: the checker to remove
        """
        self.linter._checkers[checker.name].remove(checker)
        if checker in self.linter._reports:
            del self.linter._reports[checker]
        if checker in self.linter.options_providers:
            self.linter.options_providers.remove(checker)


    def findUselessCheckers(self, allowedMessages):
        """
        Find checkers which generate no allowed messages.

        @param allowedMessages: allowed messages
        @return: useless checkers, remove them from pylint
        """
        uselessCheckers = []
        for checkerName in self.linter._checkers:
            for checker in list(self.linter._checkers[checkerName]):
                messagesOfChecker = set(checker.msgs)
                if not messagesOfChecker.intersection(allowedMessages):
                    uselessCheckers.append(checker)
        return uselessCheckers


    def restrictCheckers(self, allowedMessages):
        """
        Unregister useless checkers to speed up twistedchecker.

        @param allowedMessages: output messages allowed in twistedchecker
        """
        uselessCheckers = self.findUselessCheckers(allowedMessages)
        # Unregister these checkers
        for checker in uselessCheckers:
            self.unregisterChecker(checker)


    def run(self, args):
        """
        Setup the environment, and run pylint.

        @param args: arguments will be passed to pylint
        @type args: list of string
        """
        # set output stream.
        if self.outputStream:
            self.linter.reporter.set_output(self.outputStream)
        try:
            args = self.linter.load_command_line_configuration(args)
        except SystemExit, exc:
            if exc.code == 2:  # bad options
                exc.code = 32
            raise
        if not args:
            self.displayHelp()
        # insert current working directory to the python path to have a correct
        # behaviour.
        sys.path.insert(0, os.getcwd())
        self.linter.check(args)
