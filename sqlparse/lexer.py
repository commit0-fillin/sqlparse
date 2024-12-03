"""SQL Lexer"""
import re
from threading import Lock
from io import TextIOBase
from sqlparse import tokens, keywords
from sqlparse.utils import consume

class Lexer:
    """The Lexer supports configurable syntax.
    To add support for additional keywords, use the `add_keywords` method."""
    _default_instance = None
    _lock = Lock()

    @classmethod
    def get_default_instance(cls):
        """Returns the lexer instance used internally
        by the sqlparse core functions."""
        with cls._lock:
            if cls._default_instance is None:
                cls._default_instance = cls()
                cls._default_instance.default_initialization()
            return cls._default_instance

    def default_initialization(self):
        """Initialize the lexer with default dictionaries.
        Useful if you need to revert custom syntax settings."""
        self.clear()
        self.set_SQL_REGEX(keywords.SQL_REGEX)
        self.add_keywords(keywords.KEYWORDS)
        self.add_keywords(keywords.KEYWORDS_COMMON)
        self.add_keywords(keywords.KEYWORDS_ORACLE)

    def clear(self):
        """Clear all syntax configurations.
        Useful if you want to load a reduced set of syntax configurations.
        After this call, regexps and keyword dictionaries need to be loaded
        to make the lexer functional again."""
        self._SQL_REGEX = []
        self._keywords = {}

    def set_SQL_REGEX(self, SQL_REGEX):
        """Set the list of regex that will parse the SQL."""
        self._SQL_REGEX = SQL_REGEX

    def add_keywords(self, keywords):
        """Add keyword dictionaries. Keywords are looked up in the same order
        that dictionaries were added."""
        self._keywords.update(keywords)

    def is_keyword(self, value):
        """Checks for a keyword.

        If the given value is in one of the KEYWORDS_* dictionary
        it's considered a keyword. Otherwise, tokens.Name is returned.
        """
        val = value.upper()
        if val in self._keywords:
            return self._keywords[val]
        return tokens.Name

    def get_tokens(self, text, encoding=None):
        """
        Return an iterable of (tokentype, value) pairs generated from
        `text`. If `unfiltered` is set to `True`, the filtering mechanism
        is bypassed even if filters are defined.

        Also preprocess the text, i.e. expand tabs and strip it if
        wanted and applies registered filters.

        Split ``text`` into (tokentype, text) pairs.

        ``stack`` is the initial stack (default: ``['root']``)
        """
        if encoding is not None:
            if isinstance(text, str):
                text = text.encode(encoding)
            elif isinstance(text, bytes):
                text = text.decode(encoding)

        iterable = enumerate(text)
        for pos, char in iterable:
            for regex, token_type in self._SQL_REGEX:
                match = regex.match(text, pos)
                if match:
                    value = match.group()
                    if token_type is tokens.Keyword:
                        token_type = self.is_keyword(value)
                    yield token_type, value
                    consume(iterable, len(value) - 1)
                    break
            else:
                yield tokens.Error, char

def tokenize(sql, encoding=None):
    """Tokenize sql.

    Tokenize *sql* using the :class:`Lexer` and return a 2-tuple stream
    of ``(token type, value)`` items.
    """
    lexer = Lexer.get_default_instance()
    return lexer.get_tokens(sql, encoding)
