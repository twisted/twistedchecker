# -*- test-case-name: twistedchecker.test.test_runner -*-
import sys
import os
import StringIO
import re

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
                "pep8format.PEP8Checker",
                "docstring.DocstringChecker",
                "formattingoperation.FormattingOperationChecker",
                "comment.CommentChecker")
    allowedMessagesFromPylint = ("F0001",
                                 "C0103",
                                 "C0301",
                                 "W0311",
                                 "W0312")
    diffOption = None
    errorResultNotExist = "Error: Result file '%s' does not exist.\n"
    prefixModuleName = "************* Module "
    regexLineStart = "^[WCEFR]\d{4}\:"

    def __init__(self):
        """
        Initialize C{PyLinter} object, and load configuration file.
        """
        self.linter = PyLinter(self._makeOptions())
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
        # disable messages
        disabledMessages = set(self.linter
                           .cfgfile_parser.get("TWISTEDCHECKER", "disable")
                           .replace(" ", "").split(","))
        if disabledMessages[0]:
            map(self.linter.disable, disabledMessages)
            allowedMessages -= disabledMessages
        # set default output stream to stdout
        self.setOutput(sys.stdout)
        # set default reporter to limited reporter
        self.setReporter(LimitedReporter(allowedMessages))
        


    def _makeOptions(self):
        """
        Return options for twistedchecker.
        """
        return (
            ("diff",
             {"action": "callback", "callback": self._optionCallbackDiff,
              "type": "string",
              "metavar": "<result-file>",
              "help": "Set comparing result file to automatically "
                      "generate a diff."}
            ),
          )


    def _optionCallbackDiff(self, obj, opt, val, parser):
        """
        Be called when the option "--diff" is used.

        @param obj: option object
        @param opt: option name
        @param val: option value
        @param parser: option parser
        """
        # check if given value is a existing file
        if not os.path.exists(val):
            sys.stderr.write(self.errorResultNotExist % val)
            sys.exit()

        self.diffOption = val


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
        self.outputStream.write(self.linter.help())
        sys.exit(32)


    def registerCheckers(self):
        """
        Register all checkers of TwistedChecker to C{PyLinter}.

        @return: a list of allowed messages
        """
        # add checkers for python 3
        cfgfile = self.linter.cfgfile_parser
        if (cfgfile.has_option("TWISTEDCHECKER", "check-python3") and
            cfgfile.getboolean("TWISTEDCHECKER", "check-python3")):
            self.checkers += ("python3.Python3Checker",)
        # register checkers
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
        # check for diff option.
        if self.diffOption:
            self.prepareDiff()
        # insert current working directory to the python path to have a correct
        # behaviour.
        sys.path.insert(0, os.getcwd())
        self.linter.check(args)
        # show diff of warnings if diff option on.
        if self.diffOption:
            self.showDiffResults()


    def prepareDiff(self):
        """
        Prepare to run the checker and get diff results.
        """
        self.streamForDiff = StringIO.StringIO()
        self.linter.reporter.set_output(self.streamForDiff)


    def showDiffResults(self):
        """
        Show results when diff option on.
        """
        oldResult = open(self.diffOption).read()
        oldWarnings = self.computeWarnings(oldResult)

        newResult = self.streamForDiff.getvalue()
        newWarnings = self.computeWarnings(newResult)

        diffWarnings = self.generateDiff(oldResult, newResult)
        diffResult = self.formatWarnings(diffWarnings)
        self.outputStream.write(diffResult + "\n")
        exitCode = 1 if diffWarnings else 0
        sys.exit(exitCode)


    def generateDiff(self, oldWarnings, newWarnings):
        """
        Generate diff between given two lists of warnings.

        @param oldWarnings: parsed old warnings
        @param newWarnings: parsed new warnings
        @return: a dict object of diff
        """
        diffWarnings = {}

        for modulename in newWarnings:
            diffInModule = (
                newWarnings[modulename] -
                oldWarnings.get(modulename, set()))
            if diffInModule:
                diffWarnings[modulename] = diffInModule

        return diffWarnings


    def parseWarnings(self, result):
        """
        Transform result in string to a dict object.

        @param result: a list of warnings in string
        @return: a dict of warnings
        """
        warnings = {}
        currentModule = None
        warningsCurrentModule = []
        for line in result.splitlines():
            if line.startswith(self.prefixModuleName):
                # Save results for previous module
                if currentModule:
                    warnings[currentModule] = set(warningsCurrentModule)
                # Initial results for current module
                moduleName = line.replace(self.prefixModuleName, "")
                currentModule = moduleName
                warningsCurrentModule = []
            elif re.search(self.regexLineStart, line):
                warningsCurrentModule.append(line)
            else:
                if warningsCurrentModule:
                    warningsCurrentModule[-1] += "\n" + line
        # Save warnings for last module
        if currentModule:
            warnings[currentModule] = set(warningsCurrentModule)
        return warnings


    def formatWarnings(self, warnings):
        """
        Format warnings to a list of results.

        @param warnings: a dict of warnings produced by parseWarnings
        @return: a list of warnings in string
        """
        lines = []
        for modulename in warnings:
            lines.append(self.prefixModuleName + modulename)
            lines.extend(warnings[modulename])

        return "\n".join(lines)
