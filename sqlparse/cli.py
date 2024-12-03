"""Module that contains the command line app.

Why does this file exist, and why not put this in __main__?
  You might be tempted to import things from __main__ later, but that will
  cause problems: the code will get executed twice:
  - When you run `python -m sqlparse` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``sqlparse.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``sqlparse.__main__`` in ``sys.modules``.
  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import argparse
import sys
from io import TextIOWrapper
import sqlparse
from sqlparse.exceptions import SQLParseError

def _error(msg, exit_=None):
    """Print msg and optionally exit with return code exit_."""
    sys.stderr.write(f"Error: {msg}\n")
    if exit_ is not None:
        sys.exit(exit_)
