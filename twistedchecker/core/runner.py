# -*- test-case-name: twistedchecker.test.test_runner -*-
import sys
import os

from pylint.lint import PyLinter

class Runner():
    """
    Run and control the checking process.
    """
    outputStream = None

    def setOutput(self,stream):
        """
        Set the stream to output result of checking.
        @param stream: output stream, defaultly it should be stdout
        """
        self.outputStream = stream

    def displayHelp(self):
        """
        Output help message of twistedchecker.
        """
        print >> self.outputStream if self.outputStream else sys.stderr ,"""
                 HELP INFOMATION
                 """

    def run(self,args):
        """
        Setup the environment, and run pylint
        """
        linter = PyLinter(())
        # register standard checkers
        linter.load_default_plugins()
        # read configuration
        linter.read_config_file()
        # set output stream
        if self.outputStream:
            linter.reporter.set_output(self.outputStream)
        try:
            args = linter.load_command_line_configuration(args)
        except SystemExit, exc:
            if exc.code == 2: # bad options
                exc.code = 32
            raise
        if not args:
            self.displayHelp()
        # insert current working directory to the python path to have a correct
        # behaviour

        sys.path.insert(0, os.getcwd())
        linter.check(args)
