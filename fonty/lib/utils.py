'''utils.py: Utility functions.'''

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
