# pylint: skip-file
'''variants.py: A module to normalize font variants.'''
import re
import sys
from collections import namedtuple
from enum import Enum

Data = namedtuple('Data', 'name, id, css, hidden')

class FONT_WEIGHT(Enum):
    THIN       = Data(name='Thin',       id='100', css='100', hidden=False)
    EXTRALIGHT = Data(name='ExtraLight', id='200', css='200', hidden=False)
    LIGHT      = Data(name='Light',      id='300', css='300', hidden=False)
    REGULAR    = Data(name='Regular',    id='400', css='400', hidden=False)
    MEDIUM     = Data(name='Medium',     id='500', css='500', hidden=False)
    SEMIBOLD   = Data(name='Semibold',   id='600', css='600', hidden=False)
    BOLD       = Data(name='Bold',       id='700', css='700', hidden=False)
    EXTRABOLD  = Data(name='Extrabold',  id='800', css='800', hidden=False)
    BLACK      = Data(name='Black',      id='900', css='900', hidden=False)

class FONT_STYLE(Enum):
    NORMAL     = Data(name='Normal',     id='',  css='normal',        hidden=True)
    ITALIC     = Data(name='Italic',     id='i', css='italic',  hidden=False)
    OBLIQUE    = Data(name='Oblique',    id='o', css='oblique', hidden=False)

class FONT_STRETCH(Enum):
    NORMAL     = Data(name='Normal',     id='normal',    css='normal',    hidden=True)
    CONDENSED  = Data(name='Condensed',  id='condensed', css='condensed', hidden=False)
    EXPANDED   = Data(name='Expanded',   id='expanded',  css='expanded',  hidden=False)


class FontAttribute:
    def __init__(self, weight, style, stretch, misc: str = None, _raw = None) -> None:
        self.weight = weight
        self.style = style
        self.stretch = stretch
        self.misc = misc
        self._raw = _raw

    def __str__(self):
        return self.print()

    def __eq__(self, other):
        if (isinstance(other, self.__class__)):
            return str(self) == str(other)
        return False
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def print(self, long: bool = False, output: bool = False) -> str:
        '''Print this font's attributes'''
        if not self.weight.value.hidden:
            weight = self.weight.value.name if long else self.weight.value.id
        else:
            weight = None

        if not self.style.value.hidden:
            style = self.style.value.name if long else self.style.value.id
        else:
            style = None

        if not self.stretch.value.hidden:
            stretch = self.stretch.value.name if long else self.stretch.value.id
        else:
            stretch = None

        misc = self.misc
        strings_to_join = filter(None, [
            ''.join(filter(None, [weight, style])),
            stretch,
            misc
        ])

        s = '_'.join(strings_to_join)

        if output:
            sys.stdout.write(s + '\n')

        return s

    @staticmethod
    def parse(variant_str: str):
        '''Parse a variant string.'''
        # Default values
        weight = FONT_WEIGHT.REGULAR
        style = FONT_STYLE.NORMAL
        stretch = FONT_STRETCH.NORMAL
        misc = ''

        variant_str = variant_str.lower()
        raw = variant_str

        # Normalize string
        variant_str = ''.join(s.strip() for s in variant_str.split(' '))
        variant_str = variant_str.replace('_', '')

        is_css_format = re.match(r'\d00.*', variant_str) is not None

        # Parse the variant string
        if is_css_format:
            css_re = re.compile('(\d{{3}})({styles})?_*({stretch})?_*(.+)?'.format(
                styles=('|'.join(key for key, _ in CSS_STYLE_MAP.items())),
                stretch='|'.join(key for key, _ in STRETCH_MAP.items())
            ))
            m = css_re.search(variant_str)
            if m is not None:
                if m.group(1): # Weight
                    weight = CSS_WEIGHT_MAP[m.group(1)]
                if m.group(2): # Style
                    style = CSS_STYLE_MAP[m.group(2)]
                if m.group(3):
                    stretch = STRETCH_MAP[m.group(3)]
                if m.group(4):
                    misc = m.group(4)
        else:
            # Parse weight from string and remove the match from the string
            weight_re = re.compile('({})'.format(
                '|'.join(key for key, _ in WEIGHT_MAP.items())
            ))
            m = weight_re.search(variant_str)
            if m is not None:
                weight_str = variant_str[m.start(0):m.end(0)]
                weight = WEIGHT_MAP[weight_str]
                variant_str = variant_str.replace(weight_str, '')

            # Parse style from string and remove the match from the string
            style_re = re.compile('({})'.format(
                '|'.join(key for key, _ in STYLE_MAP.items())
            ))
            m = style_re.search(variant_str)
            if m is not None:
                style_str = variant_str[m.start(0):m.end(0)]
                style = STYLE_MAP[style_str]
                variant_str = variant_str.replace(style_str, '')

            # Parse stretch from string and remove the match from the string
            stretch_re = re.compile('({})'.format(
                '|'.join(key for key, _ in STRETCH_MAP.items())
            ))
            m = stretch_re.search(variant_str)
            if m is not None:
                stretch_str = variant_str[m.start(0):m.end(0)]
                stretch = STRETCH_MAP[stretch_str]
                variant_str = variant_str.replace(stretch_str, '')

            misc = variant_str # The remainder/unparseable string

        return FontAttribute(weight=weight,
                             style=style,
                             stretch=stretch,
                             misc=misc,
                             _raw=raw)


#===============================================================================
# WORD MAPPING
#===============================================================================
WEIGHT_MAP = {
    'thin'       : FONT_WEIGHT.THIN,
    'extralight' : FONT_WEIGHT.EXTRALIGHT,
    'light'      : FONT_WEIGHT.LIGHT,
    'regular'    : FONT_WEIGHT.REGULAR,
    'medium'     : FONT_WEIGHT.MEDIUM,
    'semibold'   : FONT_WEIGHT.SEMIBOLD,
    'bold'       : FONT_WEIGHT.BOLD,
    'extrabold'  : FONT_WEIGHT.EXTRABOLD,
    'black'      : FONT_WEIGHT.BLACK,

    # aliases
    'hairline'   : FONT_WEIGHT.THIN,
    'ultralight' : FONT_WEIGHT.EXTRALIGHT,
    'book'       : FONT_WEIGHT.REGULAR,
    'roman'      : FONT_WEIGHT.REGULAR,
    'normal'     : FONT_WEIGHT.REGULAR,
    'demibold'   : FONT_WEIGHT.SEMIBOLD,
    'negreta'    : FONT_WEIGHT.BOLD,
    'negrita'    : FONT_WEIGHT.BOLD,
    'ultrabold'  : FONT_WEIGHT.EXTRABOLD,
    'heavy'      : FONT_WEIGHT.BLACK,
    'script'     : FONT_WEIGHT.REGULAR,
}

CSS_WEIGHT_MAP = {
    '100'        : FONT_WEIGHT.THIN,
    '200'        : FONT_WEIGHT.EXTRALIGHT,
    '300'        : FONT_WEIGHT.LIGHT,
    '400'        : FONT_WEIGHT.REGULAR,
    '500'        : FONT_WEIGHT.MEDIUM,
    '600'        : FONT_WEIGHT.SEMIBOLD,
    '700'        : FONT_WEIGHT.BOLD,
    '800'        : FONT_WEIGHT.EXTRABOLD,
    '900'        : FONT_WEIGHT.BLACK,
}

STYLE_MAP = {
    'italic'     : FONT_STYLE.ITALIC,
    'cursiva'    : FONT_STYLE.ITALIC,
    'slanted'    : FONT_STYLE.OBLIQUE,
    'oblique'    : FONT_STYLE.OBLIQUE
}

CSS_STYLE_MAP = {
    'i'          : FONT_STYLE.ITALIC,
    'o'          : FONT_STYLE.OBLIQUE
}

STRETCH_MAP = {
    'condensed'  : FONT_STRETCH.CONDENSED,
    'extended'   : FONT_STRETCH.EXPANDED,
    'expanded'   : FONT_STRETCH.EXPANDED,
    'stretch'    : FONT_STRETCH.EXPANDED
}