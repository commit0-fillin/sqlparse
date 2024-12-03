from sqlparse import sql, tokens as T

class OutputFilter:
    varname_prefix = ''

    def __init__(self, varname='sql'):
        self.varname = self.varname_prefix + varname
        self.count = 0
        self.queries = []

class OutputPythonFilter(OutputFilter):
    pass

class OutputPHPFilter(OutputFilter):
    varname_prefix = '$'
