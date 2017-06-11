'''font.py: Class to manage individual fonts.'''

import requests
from click import style

class Font(object):
    '''Class to manage individual fonts.'''

    def __init__(self, path_to_file=None, variation=None, category=None):
        self.path_to_file = path_to_file
        self.category = category

        # standardise variation identifiers to the CSS standard
        if variation in VARIATIONS_MAP_CSS:
            self.variation = VARIATIONS_MAP_CSS[variation]
        else:
            self.variation = variation

    def uninstall(self):
        pass

    def to_pretty_string(self):
        '''Prints the contents of this font as ANSI formatted string.'''
        variation = '{css} {descriptive}'.format(
            css=self.variation,
            descriptive='({})'.format(VARIATIONS_MAP_DESCRIPTIVE[self.variation])
        )

        return style('{variation} - {path}'.format(
            variation=variation,
            path=self.path_to_file
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
