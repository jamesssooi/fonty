'''family.py: Class to manage a font family.'''
import hashlib
from typing import List

from termcolor import colored
from fonty.lib.variants import FontAttribute
from fonty.lib import utils
from . import Font, RemoteFont


class FontFamily(object):
    '''Class to manage a family of fonts.'''

    def __init__(self, name: str, fonts: List[Font]) -> None:
        self.name = name
        self.fonts = fonts

    @property
    def variants(self):
        '''Gets the variations available for this font family.'''
        return [font.variant for font in self.fonts]

    def get_fonts(self, variants: List[FontAttribute] = None) -> List[Font]:
        '''Returns the list of fonts in this font family.'''
        if variants:
            return [font for font in self.fonts if font.variant in variants]
        return self.fonts

    def get_variants(self) -> List[FontAttribute]:
        '''Gets the variations available for this font family.'''
        return [font.variant for font in self.fonts]

    def print(self, output: bool = True, indent: int = 0, suppress_name: bool = False):
        '''Prints the contents of this font family.'''
        lines = []

        # Name
        if not suppress_name:
            lines.append(colored(self.name, 'cyan'))

        # Font files
        fonts = [{
            'variant': font.variant.print(long=True),
            'path': colored(font.path_to_font, attrs=['dark'])
        } for font in self.fonts]
        font_lines = utils.tabularize(fonts, join=False)

        # Indent font files
        for idx, _ in enumerate(font_lines):
            if idx != len(font_lines) - 1:
                font_lines[idx] = '  ├─ ' + font_lines[idx]
            else:
                font_lines[idx] = '  └─ ' + font_lines[idx]

        lines += font_lines

        # Indent lines
        if indent:
            for idx, _ in enumerate(lines):
                lines[idx] = ' ' * indent + lines[idx]

        if output:
            print('\n'.join(lines))

        return '\n'.join(lines)

    def generate_id(self, source):
        '''Generates a unique id for this font family.'''
        unique_str = '{source}-{name}'.format(source=source, name=self.name)
        return hashlib.md5(unique_str.encode('utf-8')).hexdigest()

    @staticmethod
    def from_font_list(fonts: List[Font]) -> List['FontFamily']:
        '''Create font family instance(s) from a list of fonts.'''

        family_names = list(set([font.family for font in fonts]))

        families = [
            FontFamily(name=family, fonts=[f for f in fonts if f.family == family])
            for family in family_names
        ]

        return families


class RemoteFontFamily(object):
    '''Class to manage a remote font family.'''

    def __init__(self, name: str, fonts: List[RemoteFont]) -> None:
        self.name = name
        self.fonts = fonts

    @property
    def variants(self) -> List[FontAttribute]:
        '''Gets the variants available for this remote font family.'''
        return [font.variant for font in self.fonts]

    def get_variants(self, variants: List[FontAttribute] = None) -> List[RemoteFont]:
        '''Get fonts of the specified variants.'''
        if variants:
            return [font for font in self.fonts if font.variant in variants]
        return self.fonts

    def generate_id(self, source):
        '''Generates a unique id.'''
        unique_str = '{source}-{name}'.format(source=source, name=self.name)
        return hashlib.md5(unique_str.encode('utf-8')).hexdigest()