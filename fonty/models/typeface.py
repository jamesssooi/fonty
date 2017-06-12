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

    def download(self, variations=None, handler=None):
        '''Download this typeface.'''

        # Get list of fonts to download
        if variations:
            fonts = [font for font in self.fonts if font.variation in variations]
        else:
            fonts = self.fonts

        # Download fonts
        for font in fonts:
            font.download(handler)
        # font_bytes = []
        # for font in fonts:
        #     request = requests.get(font.remote_path, stream=True)
        #     file_size = request.headers['Content-Length']
        #     if handler:
        #         iterator = handler(request)
        #         next(iterator)

        #     data = []
        #     total_bytes = 0
        #     for bytes_ in request.iter_content(512):
        #         if bytes_:
        #             total_bytes += len(bytes_)
        #             data.append(bytes_)
        #             if handler:
        #                 iterator.send(len(bytes_))
        #     font_bytes.append(data)

        return fonts

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
                variation=key,
                remote_path=value
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
