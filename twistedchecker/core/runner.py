# -*- test-case-name: twistedchecker.test.test_runner -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

import sys
import os
import StringIO
import re

from pylint.checkers.base import NameChecker
from pylint.lint import PyLinter
from logilab.common.modutils import file_from_modpath

import twistedchecker
from twistedchecker.reporters.limited import LimitedReporter
from twistedchecker.core.exceptionfinder import findAllExceptions
from twistedchecker.checkers import patch_pylint_format


class Runner():
    """
    Run and control the checking process.
    """
    outputStream = None
    linter = None
    allowOptions = None
    # Customized checkers.
    checkers = ("header.HeaderChecker",
                "names.TwistedNamesChecker",
                "pep8format.PEP8Checker",
                "docstring.DocstringChecker",
                "formattingoperation.FormattingOperationChecker",
                "comment.CommentChecker",
                "testclassname.TestClassNameChecker")
    allowedMessagesFromPylint = ("F0001",
                                 "C0103",
                                 "C0301",
                                 "W0311",
                                 "W0312")
    diffOption = None
    errorResultRead = "Error: Failed to read result file '%s'.\n"
    prefixModuleName = "************* Module "
    regexLineStart = "^[WCEFR]\d{4}\:"

    def __init__(self):
        """
        Initialize C{PyLinter} object, and load configuration file.
        """
        self.allowOptions = True
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
        if disabledMessages != {""}:
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
             {"type": "string",
              "metavar": "<result-file>",
              "help": "Set comparing result file to automatically "
                      "generate a diff."}
            ),
            ('pep8',
             {'type': 'yn', 'metavar': '<y_or_n>',
              'default': False,
              'help': 'Show pep8 warnings.'}
            ),
            ('strict-epydoc',
             {'type': 'yn', 'metavar': '<y_or_n>',
              'default': False,
              'help': "Check '@type' and '@rtype' in epydoc."}
            ),
          )


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
        # We patch the default pylint format checker.
        patch_pylint_format.patch()

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


    def getCheckerByName(self, checkerType):
        """
        Get checker by given name.

        @checkerType: type of the checker
        """
        for checker in sum(self.linter._checkers.values(), []):
            if isinstance(checker, checkerType):
                return checker
        return None


    def allowPatternsForNameChecking(self, patternsFunc, patternsClass):
        """
        Allow name exceptions by given patterns.

        @param patternsFunc: patterns of special function names
        @param patternsClass: patterns of special class names
        """
        cfgParser = self.linter.cfgfile_parser
        nameChecker = self.getCheckerByName(NameChecker)
        if not nameChecker:
            return
        if patternsFunc:
            regexFuncAdd = "|((%s).+)$" % "|".join(patternsFunc)
        else:
            regexFuncAdd = ""
        if patternsClass:
            regexClassAdd = "|((%s).+)$" % "|".join(patternsClass)
        else:
            regexClassAdd = ""
        # Modify regex for function, method and class name.
        regexMethod = cfgParser.get("BASIC", "method-rgx") + regexFuncAdd
        regexFunction = cfgParser.get("BASIC", "function-rgx") + regexFuncAdd
        regexClass = cfgParser.get("BASIC", "class-rgx") + regexClassAdd
        # Save to config parser.
        cfgParser.set("BASIC", "method-rgx", regexMethod)
        cfgParser.set("BASIC", "function-rgx", regexFunction)
        cfgParser.set("BASIC", "class-rgx", regexClass)
        # Save to name checker.
        nameChecker.config.method_rgx = re.compile(regexMethod)
        nameChecker.config.function_rgx = re.compile(regexFunction)
        nameChecker.config.class_rgx = re.compile(regexClass)


    def getPathList(self, filesOrModules):
        """
        Transform a list of modules to path.

        @param filesOrModules: a list of modules (may be foo/bar.py or
        foo.bar)
        """
        pathList = []
        for fileOrMod in filesOrModules:
            if not os.path.exists(fileOrMod):
                # May be given module is not not a path,
                # then transform it to a path.
                try:
                    filepath = file_from_modpath(fileOrMod.split('.'))
                except (ImportError, SyntaxError):
                    # Could not load this module.
                    continue
                if not os.path.exists(filepath):
                    # Could not find this module in file system.
                    continue
                if os.path.basename(filepath) == "__init__.py":
                    filepath = os.path.dirname(filepath)
            else:
                filepath = fileOrMod
            pathList.append(filepath)
        return pathList


    def setNameExceptions(self, filesOrModules):
        """
        Find name exceptions in codes and allow them to be ignored
        in checking.

        @param filesOrModules: a list of modules (may be foo/bar.py or
        foo.bar)
        """
        pathList = self.getPathList(filesOrModules)
        for path in pathList:
            patternsFunc, patternsClass = findAllExceptions(path)
            self.allowPatternsForNameChecking(patternsFunc, patternsClass)


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
        # Check for 'strict-epydoc' option.
        if self.allowOptions and not self.linter.option_value("strict-epydoc"):
            map(self.linter.disable, ["W9203", "W9205"])

        # insert current working directory to the python path to have a correct
        # behaviour.
        sys.path.insert(0, os.getcwd())
        # set exceptions for name checking.
        self.setNameExceptions(args)

        # check for diff option.
        self.diffOption = self.linter.option_value("diff")
        if self.diffOption:
            self.prepareDiff()

        # check codes.
        self.linter.check(args)

        # show diff of warnings if diff option on.
        if self.diffOption:
            diffCount = self.showDiffResults()
            exitCode = 1 if diffCount else 0
            sys.exit(exitCode)

        sys.exit(self.linter.msg_status)


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
        try:
            oldWarnings = self.parseWarnings(self._readDiffFile())
        except:
            sys.stderr.write(self.errorResultRead % self.diffOption)
            return 1

        newWarnings = self.parseWarnings(self.streamForDiff.getvalue())

        diffWarnings = self.generateDiff(oldWarnings, newWarnings)

        if diffWarnings:
            diffResult = self.formatWarnings(diffWarnings)
            self.outputStream.write(diffResult + "\n")
            return len(diffWarnings)
        else:
            return 0

    def _readDiffFile(self):
        """
        Read content of diff file.

        This is here to help with testing.

        @return: File content.
        @rtype: c{str}
        """
        return open(self.diffOption).read()

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
        for modulename in sorted(warnings):
            lines.append(self.prefixModuleName + modulename)
            lines.extend(sorted(warnings[modulename],
                         key=lambda x: x.split(":")[1]))

        return "\n".join(lines)


def main():
    """
    An entry point used in the setup.py to create a runnable script.
    """
    runner = Runner()
    runner.run(sys.argv[1:])
