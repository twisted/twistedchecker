from pylint.interfaces import IASTNGChecker
from pylint.checkers import BaseChecker
from pylint.checkers.format import COMMENT_RGX



class CommentChecker(BaseChecker):
    """
    A checker for checking comment issues.

    A good comment should begin with one whitespace and
    with first letter capitalized.
    """
    msgs = {
     'W9401': ('Comments should begin with one whitespace',
               'Used for checking comment format issues.'),
     'W9402': ('The first letter of comment should be capitalized',
               'Used for checking comment format issues.')
    }
    __implements__ = IASTNGChecker
    name = 'comment'
    options = ()

    def visit_module(self, node):
        """
        A interface will be called when visiting a module.

        @param node: node of current module
        """
        if not node.file_stream:
            # Failed to open the module
            return
        isFirstLineOfComment = True
        isDocString = False
        lines = node.file_stream.readlines()
        for linenum, line in enumerate(lines):
            if line.strip().startswith('"""'):
                # This is a simple assumption than docstring are delimited
                # with triple double quotes on a single line.
                # Should do the job for Twisted code.
                isDocString = not isDocString

            if isDocString:
                # We ignore comments in docstrings.
                continue

            matchedComment = COMMENT_RGX.search(line)
            if matchedComment:
                if isFirstLineOfComment:
                    # Check for W9401
                    comment = matchedComment.group()
                    if (comment.startswith("#  ") or
                        not comment.startswith("# ")):
                        self.add_message('W9401', line=linenum + 1)
                    # Check for W9402
                    strippedComment = comment.lstrip("#").lstrip()
                    if strippedComment:
                        firstLetter = strippedComment[0]
                        if (firstLetter.isalpha() and
                            not firstLetter.isupper()):
                            self.add_message('W9402', line=linenum + 1)
                    isFirstLineOfComment = False
            else:
                isFirstLineOfComment = True
