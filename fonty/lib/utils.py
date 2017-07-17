'''utils.py: Utility functions.'''
import math
import os
from datetime import datetime
from typing import Union, List

import dateutil.parser
from fonty.lib.constants import APP_DIR

def xstr(s):
    return '' if s is None else str(s)

def empty_string_if_none(obj, fn):
    if obj is None:
        return ''
    else:
        return fn(obj)

def exists(obj):
    return obj is not None

# def tabularize(data, keys=None, gutter_char=' '):
#     '''Tabularize a dictionary.'''
#     keys = keys if keys is not None else list(data[0].keys())
#     max_len = {k: max(len(v[k]) for v in data) for k in keys}
#     lines = []
#     for value in data:
#         lines.append(gutter_char.join(
#             str(value[key]).ljust(max_len[key]) for key in keys
#         ))
#     return '\n'.join(lines)

def tabularize(data: List[dict], keys: List[str] = None,
               gutter: str = ' ', join: bool = True):
    '''Tabularize a list of dictionaries.'''

    # Load all keys if no explicit keys are provided
    if keys is None:
        keys = list(data[0].keys())

    # Calculate column widths for each key
    col_widths = {key: max(len(str(item[key])) for item in data) for key in keys}

    # Generate string outputs
    lines = []
    for item in data:
        s = gutter.join('{value:{width}}'.format(
            value=item[k],
            width=col_widths[k]
        ) for k in keys)
        lines.append(s)

    if join:
        return '\n'.join(lines)
    else:
        return lines

def check_dirs(path: str = None) -> str:
    '''Check if directory exists. If not, create one.'''
    if path is None:
        path = APP_DIR

    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

    return path

def parse_date(d: Union[str, datetime]):
    '''Parse a date string.'''
    if isinstance(d, str):
        d = dateutil.parser.parse(d)
    return d

def split_list(list_: list, count: int) -> List[list]:
    '''Split a list into `n` number of columns.'''
    output: List = []
    total_count = len(list_)

    for i in range(0, count):
        start = math.ceil(total_count / count) * i
        end = math.ceil(total_count / count) * (i+1)
        output.append(list_[start:end])

    return output
