'''typeface.py: Class to manage a typeface.'''

import json
from click import style
from pprint import pprint
from fonty.models.font import Font
import fonty.lib.utils as utils

class Typeface(object):
    '''Class to manage a typeface.'''

    def __init__(self, name, fonts):
        self.name = name
        self.fonts = fonts

    def get_variations(self):
        '''Gets the variations available for this typeface.'''
        return [(font.variation, font.get_descriptive_variation()) for font in self.fonts]

    def to_pretty_string(self, verbose=False):
        '''Prints the contents of this typeface as ANSI formatted string.'''

        font_str = ''
        font_variations = self.get_variations()
        variations = []
        for var, desc in font_variations:
            if desc is not None:
                variations.append(desc + '({})'.format(var))
            else:
                variations.append(var)
        font_str = ', '.join(variations)

        return '{name}\n{category}\n{fonts}'.format(
            name=style(self.name, 'blue'),
            category='  Category: ' + style('sans-serif', dim=True),
            fonts='  Variations({}): '.format(len(variations)) + style(font_str, dim=True)
        )

    @staticmethod
    def load_from_json(json_string):
        '''Initialize a new typeface instance from JSON data.'''
        data = json.loads(json_string)

        # convert fonts to a Font object
        data['fonts'] = [Font(v, k) for k, v in data['fonts'].items()]

        return Typeface(data['name'], data['fonts'])
