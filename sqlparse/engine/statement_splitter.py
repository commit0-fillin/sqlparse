from sqlparse import sql, tokens as T

class StatementSplitter:
    """Filter that split stream at individual statements"""

    def __init__(self):
        self._reset()

    def _reset(self):
        """Set the filter attributes to its default values"""
        self.level = 0
        self.split_level = 0
        self.consume_ws = False
        self.current_statement = []

    def _change_splitlevel(self, ttype, value):
        """Get the new split level (increase, decrease or remain equal)"""
        if ttype in T.Keyword:
            if value.upper() in ('BEGIN', 'CASE'):
                return 1
            elif value.upper() in ('END', 'END CASE'):
                return -1
        elif ttype is T.Punctuation:
            if value == '(':
                return 1
            elif value == ')':
                return -1
        return 0

    def process(self, stream):
        """Process the stream"""
        self._reset()
        for ttype, value in stream:
            # Ignore comments
            if ttype in T.Comment:
                continue
            
            # Handle whitespace
            if ttype in T.Whitespace:
                if self.consume_ws:
                    continue
                else:
                    self.consume_ws = True
            else:
                self.consume_ws = False
            
            # Update split level
            self.level += self._change_splitlevel(ttype, value)
            
            # Add token to current statement
            self.current_statement.append((ttype, value))
            
            # Check for statement end
            if self.level <= 0 and ttype is T.Punctuation and value == ';':
                yield self.current_statement
                self._reset()
        
        # Yield any remaining statement
        if self.current_statement:
            yield self.current_statement
