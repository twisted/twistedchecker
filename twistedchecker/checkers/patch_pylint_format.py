"""
Extension of pylint format checkers.
"""
from pylint.checkers.format import FormatChecker


def check_lines(self, lines, i):
    """
    check lines have less than a maximum number of characters.

    It ignored lines with long URLs.
    """
    maxChars = self.config.max_line_length
    for line in lines.splitlines():
        if len(line) > maxChars:
            if 'http://' in line or 'https://' in line:
                continue
            self.add_message('C0301', line=i, args=(len(line), maxChars))
        i += 1



def patch():
    """
    pylint thinks that its default checkers are so special that anybody
    wants them so there is no clean way to prevent them from being loaded
    or to unregister them.
    """
    FormatChecker.check_lines = check_lines
