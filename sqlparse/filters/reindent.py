from sqlparse import sql, tokens as T
from sqlparse.utils import offset, indent

class ReindentFilter:

    def __init__(self, width=2, char=' ', wrap_after=0, n='\n', comma_first=False, indent_after_first=False, indent_columns=False, compact=False):
        self.n = n
        self.width = width
        self.char = char
        self.indent = 1 if indent_after_first else 0
        self.offset = 0
        self.wrap_after = wrap_after
        self.comma_first = comma_first
        self.indent_columns = indent_columns
        self.compact = compact
        self._curr_stmt = None
        self._last_stmt = None
        self._last_func = None

    def _flatten_up_to_token(self, token):
        """Yields all tokens up to token but excluding current."""
        for t in self._curr_stmt.flatten():
            if t == token:
                break
            yield t
