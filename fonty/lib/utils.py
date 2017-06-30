'''utils.py: Utility functions.'''
import os
from datetime import datetime
from typing import Union

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

def tabularize(data, keys=None, gutter_char=' '):
    '''Tabularize a dictionary.'''
    keys = keys if keys is not None else list(data[0].keys())
    max_len = {k: max(len(v[k]) for v in data) for k in keys}
    lines = []
    for value in data:
        lines.append(gutter_char.join(
            str(value[key]).ljust(max_len[key]) for key in keys
        ))
    return '\n'.join(lines)

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
