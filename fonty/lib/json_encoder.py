'''json_encoder.py'''
from json import JSONEncoder
from fonty.models.font import Font, FontFamily

class FontyJSONEncoder(JSONEncoder):
    '''Extends JSONEncoder to support the encoding of Fonty's data structures.'''

    def default(self, o):
        if isinstance(o, FontFamily):
            return {'name': o.name, 'fonts': o.fonts}

        if isinstance(o, Font):
            return {'variant': str(o.variant), 'local_path': o.path_to_font}

        else:
            return JSONEncoder.default(self, o)
