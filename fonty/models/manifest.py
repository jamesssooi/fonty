'''manifest.py'''
import os
import json
from datetime import datetime
from typing import List, Union

from fontTools.ttLib import TTFont
from fonty.models.font import Font
from fonty.lib.constants import MANIFEST_PATH, JSON_DUMP_OPTS
from fonty.lib.list_fonts import get_user_fonts
from fonty.lib import utils

class Manifest:
    '''Manifest is a class to manage a manifest list of installed fonts on the user's system.'''

    def __init__(self, typefaces, last_updated: Union[str, datetime] = None):
        self.typefaces = typefaces
        self.last_updated = utils.parse_date(last_updated)

    def add(self, family: str, font: Font):
        '''Add a font to the manifest.'''

        # Check data integrity of font instance
        if not font.local_path or not font.variant:
            raise Exception

        if family not in self.typefaces:
            self.typefaces[family] = {'name': family, 'fonts': []}

        self.typefaces[family]['fonts'].append({
            'path': font.local_path,
            'variant': font.variant
        })

    def remove(self, family: str, variant: str = None) -> int:
        '''Remove a font or an entire family from the manifest.'''

        if family not in self.typefaces:
            raise Exception

        if variant is None:
            count = len(self.typefaces[family]['fonts'])
            del self.typefaces[family]
        else:
            idx_to_delete = next((
                idx for idx, val in enumerate(self.typefaces[family]['fonts'])
                if val['variant'] == variant
            ), None)

            if idx_to_delete is not None:
                count = 1
                del self.typefaces[family][idx_to_delete]

        return count

    def save(self, path: str = None) -> str:
        '''Save the manifest list to disk.'''
        if path is None:
            path = MANIFEST_PATH
        path = utils.check_dirs(path)

        data = {
            'lastUpdated': datetime.now().isoformat(),
            'typefaces': self.typefaces
        }

        # Write to file (manifest.json)
        with open(path, 'w') as f:
            json.dump(data, f, **JSON_DUMP_OPTS)

    @staticmethod
    def load(path: str = None) -> 'Manifest':
        '''Load the manifest file from disk.'''
        if not path:
            path = MANIFEST_PATH

        with open(path, encoding='utf-8') as f:
            data = json.loads(f.read())

        return Manifest(typefaces=data['typefaces'],
                        last_updated=data['lastUpdated'])

    @staticmethod
    def generate() -> 'Manifest':
        '''Generate a manifest list from the user's installed fonts.'''
        return Manifest(typefaces=get_user_fonts(),
                        last_updated=datetime.now())
