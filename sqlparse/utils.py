import itertools
import re
from collections import deque
from contextlib import contextmanager
SPLIT_REGEX = re.compile('\n(\n (?:                     # Start of non-capturing group\n  (?:\\r\\n|\\r|\\n)      |  # Match any single newline, or\n  [^\\r\\n\'"]+          |  # Match any character series without quotes or\n                         # newlines, or\n  "(?:[^"\\\\]|\\\\.)*"   |  # Match double-quoted strings, or\n  \'(?:[^\'\\\\]|\\\\.)*\'      # Match single quoted strings\n )\n)\n', re.VERBOSE)
LINE_MATCH = re.compile('(\\r\\n|\\r|\\n)')

def split_unquoted_newlines(stmt):
    """Split a string on all unquoted newlines.

    Unlike str.splitlines(), this will ignore CR/LF/CR+LF if the requisite
    character is inside of a string."""
    return [part.strip() for part in SPLIT_REGEX.split(stmt) if part.strip()]

def remove_quotes(val):
    """Helper that removes surrounding quotes from strings."""
    if val and val[0] in ('"', "'") and val[-1] == val[0]:
        return val[1:-1]
    return val

def recurse(*cls):
    """Function decorator to help with recursion

    :param cls: Classes to not recurse over
    :return: function
    """
    def wrap(f):
        def wrapped(tlist):
            for sgroup in tlist.get_sublists():
                if not isinstance(sgroup, cls):
                    wrapped(sgroup)
            f(tlist)
        return wrapped
    return wrap

def imt(token, i=None, m=None, t=None):
    """Helper function to simplify comparisons Instance, Match and TokenType
    :param token:
    :param i: Class or Tuple/List of Classes
    :param m: Tuple of TokenType & Value. Can be list of Tuple for multiple
    :param t: TokenType or Tuple/List of TokenTypes
    :return:  bool
    """
    if i is not None:
        if isinstance(i, (list, tuple)):
            return isinstance(token, tuple(i))
        return isinstance(token, i)
    if m is not None:
        if isinstance(m[0], (list, tuple)):
            return any(token.match(*_m) for _m in m)
        return token.match(*m)
    if t is not None:
        return token.ttype in (t if isinstance(t, (list, tuple)) else (t,))
    return False

def consume(iterator, n):
    """Advance the iterator n-steps ahead. If n is none, consume entirely."""
    if n is None:
        deque(iterator, maxlen=0)
    else:
        next(itertools.islice(iterator, n, n), None)
