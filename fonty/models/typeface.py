'''typeface.py: Class to manage a typeface.'''

import json
import hashlib
from typing import List, Callable
from functools import reduce

from click import style
from termcolor import colored
from fonty.lib.variants import FontAttribute
from fonty.lib.install import install_fonts
from fonty.lib.uninstall import uninstall_fonts
from fonty.models.font import Font, RemoteFont
from fonty.lib import utils

class Typeface(object):
    '''Class to manage a typeface.'''

    def __init__(self, name: str, fonts: List[Font] = [], category: str = None):
        self.name = name
        self.fonts = fonts
        self.category = category

    @property
    def variants(self):
        '''Gets the variations available for this typeface.'''
        return [font.variant for font in self.fonts]

    def download(self, variants=None, handler=None):
        '''Download this typeface.'''
        fonts = self.get_fonts(variants)

        # Download fonts
        for font in fonts:
            font.download(handler)

        return fonts

    def install(self, variants: List[str] = None):
        '''Install this typeface.'''
        fonts = self.get_fonts(variants)
        for font in fonts:
            font.install()

        return Typeface(
            name=self.name,
            category=self.category,
            fonts=fonts
        )

    def uninstall(self, variants: List[str] = None):
        '''Uninstall this typeface.'''
        fonts = self.get_fonts(variants)
        for font in fonts:
            font.uninstall()

        return True

    def get_fonts(self, variants: List[FontAttribute] = None):
        '''Returns the list of fonts in this typeface.'''
        if variants:
            return [font for font in self.fonts if font.variant in variants]
        else:
            return self.fonts

    def get_variants(self):
        '''Gets the variations available for this typeface.'''
        return [font.variant for font in self.fonts]

    def print(self, output: bool = True, indent: int = 0, suppress_name: bool = False):
        '''Prints the contents of this typeface.'''
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

        return Typeface(name=data['name'],
                        fonts=fonts,
                        category=data['category'])

    @staticmethod
    def load_from_manifest(name: str):
        '''Load a typeface from the user's local manifest file.'''
        from fonty.models.manifest import Manifest

        try:
            manifest = Manifest.load()
        except Exception as e:
            raise e # TODO: Implement exception

        return manifest.get(name)

    @staticmethod
    def from_font_list(fonts: List[Font]) -> List['Typeface']:
        '''Create typeface instance(s) from a list of fonts.'''

        family_names = list(set([font.family for font in fonts]))

        families = [
            Typeface(
                name=family,
                fonts=[font for font in fonts if font.family == family]
            ) for family in family_names
        ]

        return families

class RemoteFontFamily(object):
    '''Class to manage a remote font family.'''

    def __init__(self, name: str, fonts: RemoteFont):
        self.name = name
        self.fonts = fonts

    @property
    def variants(self) -> List[FontAttribute]:
        '''Gets the variants available for this remote font family.'''
        return [font.variant for font in self.fonts]

    def get_variants(self, variants: List[FontAttribute]=None) -> List[RemoteFont]:
        '''Get fonts of the specified variants.'''
        if variants:
            return [font for font in self.fonts if font.variant in variants]
        else:
            return self.fonts

    def generate_id(self, source):
        '''Generates a unique id.'''
        unique_str = '{source}-{name}'.format(source=source, name=self.name)
        return hashlib.md5(unique_str.encode('utf-8')).hexdigest()