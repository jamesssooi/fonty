'''typeface.py: Class to manage a typeface.'''

import json
import hashlib
import requests
import click
from click import style
from pprint import pprint
from fonty.models.font import Font
import fonty.lib.utils as utils

class Typeface(object):
    '''Class to manage a typeface.'''

    def __init__(self, name, category, fonts):
        self.name = name
        self.fonts = fonts
        self.category = category

    def download(self, variants=None, handler=None):
        '''Download this typeface.'''

        # Filter font list to requested variants only
        if variants:
            fonts = [font for font in self.fonts if font.variant in variants]
        else:
            fonts = self.fonts

        # Download fonts
        for font in fonts:
            font.download(handler)

        return fonts

    def get_variants(self):
        '''Gets the variations available for this typeface.'''
        return [(font.variant, font.get_descriptive_variant()) for font in self.fonts]

    def to_pretty_string(self, verbose=False):
        '''Prints the contents of this typeface as ANSI formatted string.'''

        font_str = ''
        font_variants = self.get_variants()
        variants = []
        for var, desc in font_variants:
            if desc is not None:
                variants.append(desc + '({})'.format(var))
            else:
                variants.append(var)
        font_str = ', '.join(variants)

        return '{name}\n{category}\n{fonts}'.format(
            name=style(self.name, 'blue'),
            category='  Category: ' + style('sans-serif', dim=True),
            fonts='  Variations({}): '.format(len(variants)) + style(font_str, dim=True)
        )

    def generate_id(self, source):
        '''Generates a unique id.'''
        unique_str = '{source}-{name}'.format(source=source, name=self.name)
        return hashlib.md5(unique_str.encode('utf-8')).hexdigest()

    @staticmethod
    def load_from_json(json_string):
        '''Initialize a new typeface instance from JSON data.'''
        data = json_string
        if not isinstance(json_string, dict):
            data = json.loads(json_string)

        # convert fonts to a Font object
        fonts = []
        for key, value in data['fonts'].items():
            fonts.append(Font(
                variant=key,
                filename=value['filename'],
                remote_path=value['url']
            ))

        return Typeface(data['name'], data['category'], fonts)


# Functions
def download_generator(total_size):
    current_size = 0
    while current_size < total_size:
        received_size = yield
        current_size += received_size
        yield current_size
    return
