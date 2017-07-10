'''typeface.py: Class to manage a typeface.'''

import json
import hashlib
from typing import List

from click import style
from fonty.lib.install import install_fonts
from fonty.lib.uninstall import uninstall_fonts
from fonty.models.font import Font

class Typeface(object):
    '''Class to manage a typeface.'''

    def __init__(self, name, fonts, category=None):
        self.name = name
        self.fonts = fonts
        self.category = category

    def download(self, variants=None, handler=None):
        '''Download this typeface.'''
        fonts = self.get_fonts(variants)

        # Download fonts
        for font in fonts:
            font.download(handler)

        return fonts

    def install(self, path: str = None, variants: List[str] = None):
        '''Install this typeface.'''
        from fonty.models.manifest import Manifest

        # Install fonts
        fonts = self.get_fonts(variants)
        success = install_fonts(fonts, path)

        # Update manifest file
        if success:
            manifest = Manifest.load()
            manifest.add(self, success)
            manifest.save()

        return success

    def uninstall(self, variants: List[str] = None):
        '''Uninstall this typeface.'''
        from fonty.models.manifest import Manifest

        # Uninstall fonts
        fonts = self.get_fonts(variants)
        success, failed = uninstall_fonts(fonts)

        # Update manifest file
        if success:
            uninstalled_variants = [str(font.variant) for font in success]
            manifest = Manifest.load()
            manifest.remove(self, uninstalled_variants)

        return success, failed

    def get_fonts(self, variants: List[str] = None):
        '''Returns the list of fonts in this typeface.'''
        if variants:
            return [font for font in self.fonts if str(font.variant) in variants]
        else:
            return self.fonts

    def get_variants(self):
        '''Gets the variations available for this typeface.'''
        return [font.variant for font in self.fonts]

    def to_pretty_string(self, verbose=False):
        '''Prints the contents of this typeface as ANSI formatted string.'''

        variants = self.get_variants()
        font_str = ', '.join(str(variant) for variant in variants)

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
