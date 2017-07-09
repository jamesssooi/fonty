'''json_encoder.py'''
from json import JSONEncoder
from fonty.models.typeface import Typeface
from fonty.models.font import Font

class FontyJSONEncoder(JSONEncoder):
    '''Extends JSONEncoder to support the encoding of Fonty's data structures.'''

    def default(self, o):
        if isinstance(o, Typeface):
            d = {'name': o.name, 'fonts': o.fonts}
            if o.category is not None:
                d['category'] = o.category
            return d

        if isinstance(o, Font):
            d = {'variant': str(o.variant)}
            if o.local_path is not None:
                d['localPath'] = o.local_path
            if o.remote_path is not None:
                d['remotePath'] = o.remote_path
            if o.filename is not None:
                d['filename'] = o.filename
            return d

        else:
            return JSONEncoder.default(self, o)
