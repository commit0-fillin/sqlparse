"""SQL formatter"""
from sqlparse import filters
from sqlparse.exceptions import SQLParseError

def validate_options(options):
    """Validates options."""
    if not isinstance(options, dict):
        raise SQLParseError("Options must be a dictionary")
    
    valid_options = {
        'keyword_case', 'identifier_case', 'strip_comments', 'strip_whitespace',
        'reindent', 'indent_width', 'indent_after_first', 'indent_columns',
        'wrap_after', 'comma_first', 'use_space_around_operators', 'output_format'
    }
    
    for key in options:
        if key not in valid_options:
            raise SQLParseError(f"Invalid option: {key}")
    
    if 'keyword_case' in options and options['keyword_case'] not in ('upper', 'lower', 'capitalize', None):
        raise SQLParseError("Invalid value for 'keyword_case'. Must be 'upper', 'lower', 'capitalize', or None")
    
    if 'identifier_case' in options and options['identifier_case'] not in ('upper', 'lower', 'capitalize', None):
        raise SQLParseError("Invalid value for 'identifier_case'. Must be 'upper', 'lower', 'capitalize', or None")
    
    if 'indent_width' in options and not isinstance(options['indent_width'], int):
        raise SQLParseError("'indent_width' must be an integer")
    
    if 'wrap_after' in options and not isinstance(options['wrap_after'], int):
        raise SQLParseError("'wrap_after' must be an integer")

def build_filter_stack(stack, options):
    """Setup and return a filter stack.

    Args:
      stack: :class:`~sqlparse.filters.FilterStack` instance
      options: Dictionary with options validated by validate_options.
    """
    # Keyword case
    if 'keyword_case' in options:
        stack.preprocess.append(
            filters.KeywordCaseFilter(case=options['keyword_case']))

    # Identifier case
    if 'identifier_case' in options:
        stack.preprocess.append(
            filters.IdentifierCaseFilter(case=options['identifier_case']))

    # Strip comments
    if options.get('strip_comments', False):
        stack.preprocess.append(filters.StripCommentsFilter())

    # Strip whitespace
    if options.get('strip_whitespace', False):
        stack.preprocess.append(filters.StripWhitespaceFilter())

    # Reindent
    if options.get('reindent', False):
        stack.postprocess.append(filters.ReindentFilter(
            char=' ' * options.get('indent_width', 2),
            indent_after_first=options.get('indent_after_first', False),
            indent_columns=options.get('indent_columns', False),
            wrap_after=options.get('wrap_after', 0),
            comma_first=options.get('comma_first', False)
        ))

    # Use space around operators
    if options.get('use_space_around_operators', False):
        stack.postprocess.append(filters.SpacesAroundOperatorsFilter())

    # Output format
    output_format = options.get('output_format')
    if output_format:
        if output_format.lower() == 'python':
            stack.postprocess.append(filters.OutputPythonFilter())
        elif output_format.lower() == 'php':
            stack.postprocess.append(filters.OutputPHPFilter())

    return stack
