"""
Controller for generating diff of warnings.
"""
import sys
import os

from logilab.common.modutils import modpath_from_file, get_module_files
from logilab.common.modutils import file_from_modpath
from twistedchecker.core.vcschecking import SVNCheckingController

class DiffController:
    """
    Control the process of generating diff.
    """
    pathModule = None
    branchToCompare = None
    rawArguments = None

    warningOneModule = ("when using diff option,"
                        "only one module is allowed for checking, found %d")
    warningModuleNotExist = "could not find given module"
    warningModuleLoadError = "error occurred when loading given module"
    warningVCSNotFound = "could not find version control system of given module"

    messageCheckModule = "preparing to check module '%s' (%s)"

    def __init__(self, ref, args, paths):
        """
        Initial the diff process.

        @param ref: a branch to compare with
        @param args: arguments for pylint
        @param paths: a list of path for checking
        """
        if len(paths) != 1:
            self.log( self.warningOneModule % len(paths))
            sys.exit()
        self.pathModule = paths[0]
        self.branchToCompare = ref
        self.rawArguments = args
        self._checkModuleExistence()
        nameVCS = self._findVCS()
        if not nameVCS:
            self.log(warningVCSNotFound)
            sys.exit()
        self.log(self.messageCheckModule % (paths[0], nameVCS))
        checkingControllerClass = self._getCheckingControllerClass(nameVCS)
        checkingController = checkingControllerClass(self.pathModule,
                                                     self.branchToCompare,
                                                     self.log)
        self.generateDiff(checkingController)


    def _checkModuleExistence(self):
        """
        Check if module exists, and finally make sure 'pathModule'
        saves the path for given module.
        """
        if not os.path.exists(self.pathModule):
            # May be given module is not not a path,
            # then transform it to a path.
            try:
                filepath = file_from_modpath(self.pathModule.split('.'))
            except (ImportError, SyntaxError) as ex:
                # TODO: need to check
                self.log(self.warningModuleLoadError)
                self.log(ex)
                sys.exit()
            if not os.path.exists(filepath):
                # Could not find this module, exit.
                self.log(self.warningModuleNotExist)
                sys.exit()
            if os.path.basename(filepath) == "__init__.py":
                filepath = os.path.dirname(filepath)
        else:
            filepath = self.pathModule

        self.pathModule = os.path.abspath(filepath)


    def log(self, msg):
        """
        Show message to user.

        @param msg: message
        """
        print >> sys.stderr, "[TwistedChecker]", msg


    def _findVCS(self):
        """
        Find which VCS is used by user.

        @return: name of vcs
        """
        pathModuleDir = os.path.dirname(self.pathModule)
        # Check for svn.
        if os.path.exists(pathModuleDir + os.sep + ".svn"):
            return "svn"
        # Check for bzr.
        previousPath = None
        currentPath = pathModuleDir
        while currentPath and currentPath != previousPath:
            if os.path.exists(currentPath + os.sep + ".bzr"):
                return "bzr"
            previousPath = currentPath
            currentPath = os.path.dirname(currentPath)


    def _getCheckingControllerClass(self, nameVCS):
        """
        Get the class of checking controller according to given VCS.

        @param nameVCS: name of VCS
        """
        if nameVCS == "svn":
            return SVNCheckingController
        elif nameVCS == "bzr":
            return None
        else:
            return None


    def generateDiff(self, checkingController):
        """
        Generate diff by warnings.

        @param checkingController: the checking controller of specific VCS
        """
        print checkingController.getComparingWarnings()