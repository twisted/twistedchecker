import re
from pylint.interfaces import IAstroidChecker
from pylint.checkers import BaseChecker

COMMENT_RGX = re.compile(b"#.*$", re.M)

class CommentChecker(BaseChecker):
    """
    A checker for checking comment issues.

    A good comment should begin with one whitespace and
    with first letter capitalized.
    """
    msgs = {
     'W9401': ('Comments should begin with one whitespace',
               'Used for checking comment format issues.',
                   'comments-one-whitespace'),
     'W9402': ('The first letter of comment should be capitalized',
               'Used for checking comment format issues. ',
                   'comments-capitalized')
    }
    __implements__ = IAstroidChecker
    name = 'comment'
    options = ()

    def visit_module(self, node):
        """
        A interface will be called when visiting a module.

        @param node: node of current module
        """
        isFirstLineOfComment = True
        isDocString = False

        with node.stream() as stream:
            for (linenum, line) in enumerate(stream):
                if line.strip().startswith(b'"""'):
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
                        if (comment.startswith(b"#  ") or
                            not comment.startswith(b"# ")):
                            self.add_message('W9401', line=linenum + 1, node=node)
                        # Check for W9402
                        strippedComment = comment.lstrip(b"#").lstrip()
                        if strippedComment:
                            firstLetter = strippedComment[0:1]
                            if (firstLetter.isalpha() and
                                not firstLetter.isupper()):
                                self.add_message('W9402', line=linenum + 1, node=node)
                        isFirstLineOfComment = False
                else:
                    isFirstLineOfComment = True
