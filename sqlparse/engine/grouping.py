from sqlparse import sql
from sqlparse import tokens as T
from sqlparse.utils import recurse, imt
T_NUMERICAL = (T.Number, T.Number.Integer, T.Number.Float)
T_STRING = (T.String, T.String.Single, T.String.Symbol)
T_NAME = (T.Name, T.Name.Placeholder)

def _group_matching(tlist, cls):
    """Groups Tokens that have beginning and end."""
    idx = 0
    while idx < len(tlist.tokens):
        token = tlist.tokens[idx]
        if token.match(*cls.M_OPEN):
            end_idx = tlist.token_index(tlist.token_next_match(idx, *cls.M_CLOSE))
            if end_idx:
                group = tlist.group_tokens(cls, idx, end_idx)
                idx = tlist.token_index(group)
        idx += 1

@recurse(sql.Identifier)
def group_order(tlist):
    """Group together Identifier and Asc/Desc token"""
    idx = 0
    while idx < len(tlist.tokens):
        token = tlist.tokens[idx]
        if isinstance(token, sql.Identifier):
            next_token = tlist.token_next(idx)
            if next_token and next_token.match(T.Keyword, ('ASC', 'DESC')):
                token.tokens.append(next_token)
                tlist.tokens.pop(idx + 1)
        idx += 1

def _group(tlist, cls, match, valid_prev=lambda t: True, valid_next=lambda t: True, post=None, extend=True, recurse=True):
    """Groups together tokens that are joined by a middle token. i.e. x < y"""
    idx = 1
    while idx < len(tlist.tokens) - 1:
        prev = tlist.tokens[idx - 1]
        token = tlist.tokens[idx]
        next_token = tlist.tokens[idx + 1]

        if token.match(*match) and valid_prev(prev) and valid_next(next_token):
            # Check for comments between tokens
            prev_idx, next_idx = idx - 1, idx + 1
            while prev_idx > 0 and tlist.tokens[prev_idx].is_whitespace:
                prev_idx -= 1
            while next_idx < len(tlist.tokens) - 1 and tlist.tokens[next_idx].is_whitespace:
                next_idx += 1

            # Create the new group
            group = cls([prev, token, next_token])
            tlist.tokens[prev_idx:next_idx + 1] = [group]

            if extend:
                idx = tlist.token_index(group)
                while idx > 0 and tlist.token_prev(idx).match(*match):
                    prev = tlist.tokens[idx - 1]
                    if not valid_prev(prev):
                        break
                    group.tokens.insert(0, prev)
                    tlist.tokens.pop(idx - 1)
                    idx -= 1

                while idx < len(tlist.tokens) - 1 and tlist.token_next(idx).match(*match):
                    next_token = tlist.tokens[idx + 1]
                    if not valid_next(next_token):
                        break
                    group.tokens.append(next_token)
                    tlist.tokens.pop(idx + 1)

            if post:
                post(group)

            if recurse:
                _group(group, cls, match, valid_prev, valid_next, post, extend, recurse)

            idx = tlist.token_index(group)
        else:
            idx += 1
