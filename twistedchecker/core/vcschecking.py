import os
import sys
import vcstools
import tempfile


TWISTED_SVN_TRUNK = "svn://svn.twistedmatrix.com/svn/Twisted/trunk"


class VCSCheckingController:
    """
    A virtual class for checking a VCS branch.
    """

    def __init__(self, path, compare, logFunction):
        """
        Prepare for check a VCS branch.

        @param path: path of given module
        @param compare: a VCS branch to compare with
        @param logFunction: a function to show messages
        """


    def getWarnings(self):
        """
        Get warnings of given module.
        """


    def getComparingWarnings(self):
        """
        Get warnings of the comparing branch.
        """



class SVNCheckingController(VCSCheckingController):
    """
    A controller for checking SVN branch.
    """
    relpathInBranch = None
    pathModule = None
    pathRoot = None
    pathRelative = None

    messageFetching = "fetching %s"
    messageUseCache = "use cache of %s"

    def __init__(self, path, comparingBranch, logFunction):
        """
        Prepare for check a SVN branch.

        @param path: path of given module
        @param comparingBranch: branch to compare with.
        @param logFunction: a function to show messages
        """
        self.log = logFunction
        self.pathModule = path
        self.comparingBranch = comparingBranch
        self.pathRoot = self._findRootPath()
        self.pathRelative = os.path.relpath(path, self.pathRoot)
        


    def _findRootPath(self):
        """
        Find root path of the SVN repository.
        """
        if os.path.isfile(self.pathModule):
            pathRoot = os.path.dirname(self.pathModule)
        else:
            pathRoot = self.pathModule
        previousPath = None
        while pathRoot != previousPath:
            # If '.svn' directory does not exist in current path,
            # then previous path should be root.
            currentPath = os.path.dirname(pathRoot)
            if not os.path.exists(currentPath + os.sep + ".svn"):
                break
            previousPath = pathRoot
            pathRoot = currentPath
        return pathRoot


    def getBranchUrl(self, branch):
        """
        Get URL of svn repository of comparing branch.
        """
        if branch == "trunk":
            return TWISTED_SVN_TRUNK
        elif branch == "base":
            vcsClient = vcstools.VcsClient('svn', pathRoot)
            return vcsClient.get_url()
        else:
            return branch


    def fetchComparingBranch(self):
        """
        Get comparing branch and save to tmp directory.

        @return: path to the branch
        """
        urlComparingBranch = self.getBranchUrl(self.comparingBranch)
        tmpdir = tempfile.gettempdir()
        folderBranch = 'TWISTEDCHECKER-%x' % (hash(urlComparingBranch), )
        pathCheckout = tmpdir + os.sep + folderBranch
        if os.path.exists(pathCheckout):
            self.log(self.messageUseCache % urlComparingBranch)
            return pathCheckout
        vcsClient = vcstools.VcsClient('svn', pathCheckout)
        self.log(self.messageFetching % urlComparingBranch)
        vcsClient.checkout(urlComparingBranch)
        return pathCheckout


    def getWarningsOfModule(self):
        """
        """

    def getComparingWarnings(self):
        """
        Get warnings of the comparing branch.
        """
        pathBranch = self.fetchComparingBranch()
        print pathBranch
        
