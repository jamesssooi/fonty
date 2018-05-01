'''fonty.lib.utils'''
import math
import os
from datetime import datetime
from typing import Union, List

import dateutil.parser
from fonty.lib.constants import APP_DIR

def xstr(s) -> str:
    '''Returns an empty string if object is of `NoneType`'''
    return '' if s is None else str(s)

def exists(obj) -> bool:
    '''Returns `true` if object is not of `NoneType`'''
    return obj is not None

def tabularize(
    data: List[dict],
    keys: List[str] = None,
    gutter: str = ' ',
    join: bool = True
) -> Union[List[str], str]:
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

    return lines

def check_dirs(path: str = None) -> str:
    '''Check if a directory exists. If not, create one.'''
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
