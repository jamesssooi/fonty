'''manifest.py'''
import json
from datetime import datetime
from typing import List, Union

from fonty.models.font import FontFamily, InstalledFont
from fonty.lib.constants import APP_DIR, MANIFEST_PATH, JSON_DUMP_OPTS
from fonty.lib.list_fonts import get_user_fonts, get_user_fonts_count
from fonty.lib.json_encoder import FontyJSONEncoder
from fonty.lib.variants import FontAttribute
from fonty.lib import utils

class Manifest:
    '''Manifest is a class to manage a manifest list of installed fonts on the user's system.'''

    # Class Attributes

    schema_version: str = "0.1.0"
    families: List[FontFamily]
    last_modified: datetime
    font_count: int

    # Constructor

    def __init__(
        self,
        families: List[FontFamily],
        last_modified: Union[str, datetime] = None,
        font_count: int = 0
    ) -> None:
        self.families = families
        self.last_modified = utils.parse_date(last_modified)
        self.font_count = font_count


    # Class Methods

    def add(self, font: InstalledFont) -> int:
        '''Add a font to the manifest.'''

        family_name = font.get_family_name()

        # Load existing or create a FontFamily object
        family = self.get(family_name)
        family_idx = self.get_index(family_name)
        if family is None:
            family = FontFamily(name=family_name, fonts=[])

        # Check if font is already in manifest
        existing_variants = [str(variant) for variant in family.get_variants()]
        variant = str(font.get_variant())
        if variant in existing_variants:
            return 0

        # Add font to FontFamily object
        family.fonts.append(font)

        # Update manifest instance
        if family_idx is None:
            self.families.append(family)
        else:
            self.families[family_idx] = family

        self.font_count += 1
        return 1

    def remove(self, font: InstalledFont) -> int:
        '''Remove a font from the manifest.'''

        # Load FontFamily
        family = self.get(font.family)
        family_idx = self.get_index(font.family)
        if family is None:
            return 0

        # Remove font from FontFamily
        font_idx = next((
            i for i, val in enumerate(family.fonts) if val.variant == font.variant
        ), None)
        if font_idx is None:
            return 0
        family.fonts.pop(font_idx)

        # Update the instance with the updated FontFamily
        if family.fonts:
            self.families[family_idx] = family
        else:
            del self.families[family_idx]

        self.font_count -= 1
        return 1

    def get(self, name: str) -> FontFamily:
        '''Load a font family from the manifest.'''
        return next((val for val in self.families if val.name.lower() == name.lower()), None)

    def get_index(self, name: str) -> int:
        '''Get the index position of the font family in the manifest.'''
        return next((idx for idx, val in enumerate(self.families) if val.name.lower() == name.lower()), None)

    def save(self, path: str = None) -> None:
        '''Save the manifest list to disk.'''
        utils.check_dirs(APP_DIR)
        path = path if path else MANIFEST_PATH

        data = {
            'schema_version': self.schema_version,
            'last_modified': datetime.now().isoformat(),
            'font_count': self.font_count,
            'font_families': self.families
        }

        # Write to file (manifest.json)
        with open(path, 'w') as f:
            json.dump(data, f, cls=FontyJSONEncoder, **JSON_DUMP_OPTS)

    def is_stale(self) -> bool:
        '''Returns `true` if the total number of fonts in the manifest does not
           match the total number of fonts in the system.
        '''
        return get_user_fonts_count() != self.font_count

    # Static Methods

    @staticmethod
    def load(path: str = None) -> 'Manifest':
        '''Load the manifest file from disk.'''
        path = path if path else MANIFEST_PATH

        with open(path, encoding='utf-8') as f:
            data = json.loads(f.read())

        # Create FontFamily instances
        families = []
        for family in data['font_families']:
            fonts: List[InstalledFont] = [InstalledFont(
                installed_path=font.get('local_path'),
                registry_name=font.get('registryName', None),
                family=family.get('name'),
                variant=FontAttribute.parse(font.get('variant'))
            ) for font in family['fonts']]
            families.append(FontFamily(name=family.get('name'), fonts=fonts))

        return Manifest(
            families=families,
            font_count=data['font_count'],
            last_modified=data['last_modified']
        )

    @staticmethod
    def generate() -> 'Manifest':
        '''Generate a manifest list from the user's installed fonts.'''
        return Manifest(
            families=get_user_fonts(),
            font_count=get_user_fonts_count(),
            last_modified=datetime.now()
        )
