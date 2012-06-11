# -*- test-case-name: twistedchecker.test.test_runner -*-
import sys
import os

from pylint.lint import PyLinter

import twistedchecker


class Runner():
    """
    Run and control the checking process.
    """
    outputStream = None
    linter = None
    # Customized checkers.
    checkers = ("header.HeaderChecker",)

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
        self.registerCheckers()
        # set default output stream to stderr
        self.setOutput(sys.stderr)


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
        """
        for strChecker in self.checkers:
            modname, classname = strChecker.split(".")
            strModule = "twistedchecker.checkers.%s" % modname
            checker = getattr(__import__(strModule,
                                        fromlist=["twistedchecker.checkers"]),
                             classname)
            self.linter.register_checker(checker(self.linter))


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
