'''font.py: Class to manage individual fonts.'''

import requests
from click import style

class Font(object):
    '''Class to manage individual fonts.'''

    def __init__(self, local_path=None, remote_path=None, variation=None, category=None, raw_bytes=None):
        self.local_path = local_path
        self.remote_path = remote_path
        self.category = category
        self.raw_bytes = raw_bytes

        # standardise variation identifiers to the CSS standard
        if variation in VARIATIONS_MAP_CSS:
            self.variation = VARIATIONS_MAP_CSS[variation]
        else:
            self.variation = variation
    
    def download(self, handler=None):
        '''Download this font.'''

        if not self.remote_path:
            raise Exception # TODO: Raise Exception

        request = requests.get(self.remote_path, stream=True)
        if handler:
            iterator = handler(request)
            next(iterator)
        
        self.raw_bytes = []
        for bytes_ in request.iter_content(512):
            if bytes_:
                self.raw_bytes.append(bytes_)
                if handler: iterator.send(len(bytes_))
        
        return self

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

    def get_descriptive_variation(self):
        '''Get the descriptive variation name of this font.

        For example, a font variation of 400i returns 'italics', while a font
        variation of 700 returns 'bold'. Returns None if there's no matching
        descriptive value.
        '''
        if self.variation in VARIATIONS_MAP_DESCRIPTIVE:
            return VARIATIONS_MAP_DESCRIPTIVE[self.variation]
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
