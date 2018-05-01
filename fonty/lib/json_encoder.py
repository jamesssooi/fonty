'''json_encoder.py'''
from json import JSONEncoder
from datetime import datetime
from fonty.models.font import Font, FontFamily

class FontyJSONEncoder(JSONEncoder):
    '''Extends JSONEncoder to support the encoding of Fonty's data structures.'''

    def default(self, o): # pylint: disable=E0202

        # Datetime objects
        if isinstance(o, datetime):
            return o.isoformat()

        # FontFamily objects
        elif isinstance(o, FontFamily):
            return {'name': o.name, 'fonts': o.fonts}

        # Font objects
        elif isinstance(o, Font):
            return {'variant': str(o.variant), 'local_path': o.path_to_font}

        return JSONEncoder.default(self, o)
