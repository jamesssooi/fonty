'''manifest.py'''
import json
from datetime import datetime
from typing import List, Union

from fonty.models.font import Font
from fonty.models.typeface import Typeface
from fonty.lib.constants import APP_DIR, MANIFEST_PATH, JSON_DUMP_OPTS
from fonty.lib.list_fonts import get_user_fonts
from fonty.lib.json_encoder import FontyJSONEncoder
from fonty.lib import utils

class Manifest:
    '''Manifest is a class to manage a manifest list of installed fonts on the user's system.'''

    def __init__(self, typefaces, last_updated: Union[str, datetime] = None):
        self.typefaces = typefaces
        self.last_updated = utils.parse_date(last_updated)

    def add(self, font: Font):
        '''Add a font to the manifest.'''

        family_name = font.get_family_name()

        # Load existing or create a Typeface object
        typeface = self.get(family_name)
        typeface_idx = self.get_index(family_name)
        if typeface is None:
            typeface = Typeface(name=family_name)

        # Check if font is already in manifest
        existing_variants = [str(variant) for variant in typeface.get_variants()]
        variant = str(font.get_variant())
        if variant in existing_variants:
            return None

        # Add font to Typeface object
        typeface.fonts.append(font)

        # Update manifest instance
        if typeface_idx is None:
            self.typefaces.append(typeface)
        else:
            self.typefaces[typeface_idx] = typeface

        return self

    def remove(self, typeface: Typeface, variants: List[str] = None) -> int:
        '''Remove a font or an entire family from the manifest.'''
        
        typeface_idx = self.get_index(typeface.name)
        if typeface_idx is None:
            raise Exception

        data = self.typefaces[typeface_idx]

        if variants is None:
            count = len(self.typefaces[typeface_idx].fonts)
            self.typefaces(typeface_idx)
        else:
            count = 0
            for variant in variants:
                font_idx = next((
                    idx for idx, val in enumerate(typeface.fonts)
                    if str(val.variant) in variants
                ), None)

                if font_idx is None:
                    raise Exception

                data.fonts.pop(font_idx)
                count += 1

            if not data.fonts:
                self.typefaces.pop(typeface_idx)
            else:
                self.typefaces[typeface_idx] = data

        return count

    def get(self, name: str) -> Typeface:
        '''Load a typeface from the manifest.'''
        typeface = next((val for val in self.typefaces if val.name.lower() == name.lower()), None)
        return typeface

    def get_index(self, name: str) -> int:
        '''Get the index position of the typeface in the manifest.'''
        typeface_idx = next((idx for idx, val in enumerate(self.typefaces) if val.name.lower() == name.lower()), None)
        return typeface_idx

    def save(self, path: str = None) -> str:
        '''Save the manifest list to disk.'''
        utils.check_dirs(APP_DIR)
        if path is None:
            path = MANIFEST_PATH

        data = {
            'lastUpdated': datetime.now().isoformat(),
            'typefaces': self.typefaces
        }

        # Write to file (manifest.json)
        with open(path, 'w') as f:
            json.dump(data, f, cls=FontyJSONEncoder, **JSON_DUMP_OPTS)

    @staticmethod
    def load(path: str = None) -> 'Manifest':
        '''Load the manifest file from disk.'''
        if not path:
            path = MANIFEST_PATH

        with open(path, encoding='utf-8') as f:
            data = json.loads(f.read())

        # Convert data into Typefaces and Font instances
        typefaces = []
        for typeface_json in data['typefaces']:
            fonts = []
            for font_json in typeface_json['fonts']:
                d = {'variant': font_json['variant'],
                     'local_path': font_json['localPath']}
                if 'remotePath' in font_json:
                    d['remote_path'] = font_json['remotePath']
                if 'filename' in font_json:
                    d['filename'] = font_json['filename']
                fonts.append(Font(**d))

            typefaces.append(
                Typeface(name=typeface_json.get('name'),
                         category=typeface_json.get('category', None),
                         fonts=fonts)
            )

        return Manifest(typefaces=typefaces,
                        last_updated=data['lastUpdated'])

    @staticmethod
    def generate() -> 'Manifest':
        '''Generate a manifest list from the user's installed fonts.'''
        return Manifest(typefaces=get_user_fonts(),
                        last_updated=datetime.now())
