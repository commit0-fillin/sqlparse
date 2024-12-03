import re
from sqlparse import sql, tokens as T
from sqlparse.utils import split_unquoted_newlines

class StripCommentsFilter:
    def __init__(self):
        self._inline_comments = []
        self._multiline_comments = []

    def _process(self, stream):
        for token in stream:
            if token.is_whitespace:
                yield token
            elif token.ttype in T.Comment:
                if token.ttype == T.Comment.Single:
                    self._inline_comments.append(token)
                elif token.ttype == T.Comment.Multiline:
                    self._multiline_comments.append(token)
            else:
                yield token

    def process(self, stream):
        return self._process(stream)

    def get_inline_comments(self):
        return self._inline_comments

    def get_multiline_comments(self):
        return self._multiline_comments

class StripWhitespaceFilter:
    def __init__(self):
        self._whitespaces = []

    def _process(self, stream):
        for token in stream:
            if token.is_whitespace:
                self._whitespaces.append(token)
            else:
                yield token

    def process(self, stream):
        return self._process(stream)

    def get_whitespaces(self):
        return self._whitespaces

class SpacesAroundOperatorsFilter:
    def __init__(self):
        self.operators = set(['=', '<', '>', '>=', '<=', '<>', '!=', '+', '-', '*', '/', '%'])

    def _process(self, stream):
        for token in stream:
            if token.ttype in T.Operator or token.value in self.operators:
                yield sql.Token(T.Whitespace, ' ')
                yield token
                yield sql.Token(T.Whitespace, ' ')
            else:
                yield token

    def process(self, stream):
        return self._process(stream)

class StripTrailingSemicolonFilter:
    def _process(self, stream):
        tokens = list(stream)
        if tokens and tokens[-1].ttype == T.Punctuation and tokens[-1].value == ';':
            tokens = tokens[:-1]
        return tokens

    def process(self, stream):
        return self._process(stream)

class SerializerUnicode:
    def __init__(self, encoding='utf-8'):
        self.encoding = encoding

    def _process(self, stream):
        for token in stream:
            value = token.value
            if isinstance(value, bytes):
                value = value.decode(self.encoding)
            yield sql.Token(token.ttype, value)

    def process(self, stream):
        return self._process(stream)
