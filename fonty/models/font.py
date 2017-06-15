'''font.py: Class to manage individual fonts.'''

import requests
from click import style
from fonty.lib.install import install

class Font(object):
    '''Class to manage individual fonts.'''

    def __init__(self, filename=None, local_path=None, remote_path=None, variant=None, category=None, raw_bytes=None):
        self.filename = filename
        self.local_path = local_path
        self.remote_path = remote_path
        self.category = category
        self.bytes = raw_bytes

        # standardise variant identifiers to the CSS standard
        if variant in VARIATIONS_MAP_CSS:
            self.variant = VARIATIONS_MAP_CSS[variation]
        else:
            self.variant = variant
    
    def download(self, handler=None):
        '''Download this font. Appends the bytes as a property to self.'''

        if not self.remote_path:
            raise Exception # TODO: Raise Exception

        request = requests.get(self.remote_path, stream=True)
        if handler:
            iterator = handler(self, request)
            next(iterator)
        
        self.bytes = b''
        for bytes_ in request.iter_content(128):
            if bytes_:
                self.bytes += bytes_
                if handler: iterator.send(len(self.bytes))
        
        return self

    def install(self, path=None):
        install(self, path)

    def to_pretty_string(self):
        '''Prints the contents of this font as ANSI formatted string.'''
        variation = '{css} {descriptive}'.format(
            css=self.variation,
            descriptive='({})'.format(VARIATIONS_MAP_DESCRIPTIVE[self.variation])
        )

        return style('{variation} - {path}'.format(
            variation=variation,
            path=self.local_path
        ), dim=True)

    def get_descriptive_variant(self):
        '''Get the descriptive variation name of this font.

        For example, a font variation of 400i returns 'italics', while a font
        variation of 700 returns 'bold'. Returns None if there's no matching
        descriptive value.
        '''
        if self.variant in VARIATIONS_MAP_DESCRIPTIVE:
            return VARIATIONS_MAP_DESCRIPTIVE[self.variant]
        else:
            return None


VARIATIONS_MAP_DESCRIPTIVE = {
    '100'  : 'thin',
    '100i' : 'thin-italics',
    '200'  : '',
    '200i' : '',
    '300'  : 'light',
    '300i' : 'light-italics',
    '400'  : 'regular',
    '400i' : 'italics',
    '500'  : 'semibold',
    '500i' : 'semibold-italics',
    '600'  : '',
    '600i' : '',
    '700'  : 'bold',
    '700i' : 'bold-italics',
    '800'  : '',
    '800i' : '',
    '900'  : 'black',
    '900i' : 'black-italics',
}

VARIATIONS_MAP_CSS = dict((v, k) for k, v in VARIATIONS_MAP_DESCRIPTIVE.items())
