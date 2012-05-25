# -*- test-case-name: twistedchecker.test.test_runner -*-
import sys
import os

from pylint.lint import PyLinter

import twistedchecker


class Runner():
    """
    Run and control the checking process.
    """
    outputStream = sys.stderr


    def setOutput(self, stream):
        """
        Set the stream to output result of checking.

        @param stream: output stream, defaultly it should be stdout
        """
        self.outputStream = stream


    def displayHelp(self):
        """
        Output help message of twistedchecker.
        """
        print >> self.outputStream, """---\nHELP INFOMATION"""


    def run(self, args):
        """
        Setup the environment, and run pylint.

        @param args: arguments will be passed to pylint
        @type args: list of string
        """
        linter = PyLinter(())
        # register standard checkers
        linter.load_default_plugins()
        # read configuration
        pathConfig = "%s/configuration/pylintrc" % twistedchecker.abspath
        if os.path.exists(pathConfig):
            linter.read_config_file(pathConfig)
        else:
            linter.read_config_file()
        # is there some additional plugins in the file configuration, in
        config_parser = linter.cfgfile_parser
        if config_parser.has_option('MASTER', 'load-plugins'):
            plugins = splitstrip(config_parser.get('MASTER', 'load-plugins'))
            linter.load_plugin_modules(plugins)
        # now we can load file config and command line, plugins (which can
        # provide options) have been registered
        linter.load_config_file()
        # set output stream
        if self.outputStream:
            linter.reporter.set_output(self.outputStream)
        try:
            args = linter.load_command_line_configuration(args)
        except SystemExit, exc:
            if exc.code == 2:  # bad options
                exc.code = 32
            raise
        if not args:
            self.displayHelp()
        # insert current working directory to the python path to have a correct
        # behaviour
        sys.path.insert(0, os.getcwd())
        linter.check(args)
