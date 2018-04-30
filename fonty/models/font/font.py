'''font.py: Class to manage individual fonts.'''
import os
import codecs
from typing import Dict, Any, Optional

from fontTools.ttLib import TTFont
from fonty.lib.variants import FontAttribute
from fonty.lib.font_name_ids import FONT_NAMEID_FAMILY, FONT_NAMEID_FAMILY_PREFFERED, \
                                    FONT_NAMEID_VARIANT, FONT_NAMEID_VARIANT_PREFFERED
from .font_format import FontFormat

class Font(object):
    '''Class to manage individual fonts.'''

    # Class Properties ------------------------------------------------------- #
    path_to_font: str
    family: str
    variant: FontAttribute
    name_table: Optional[Dict[Any, Any]] = None

    # Constructor ------------------------------------------------------------ #
    def __init__(
            self,
            path_to_font: str,
            family: str = None,
            variant: FontAttribute = None
        ) -> None:
        self.path_to_font = path_to_font

        # Get family name
        self.family = family if family else self.get_family_name()

        # Get variant
        self.variant = variant if variant else self.get_variant()

    # Class Methods ----------------------------------------------------------- #
    def install(self):
        '''Installs this font to the system.'''
        from fonty.lib.install import install_fonts

        # Install the font on to the system
        installed_font = install_fonts(self)

        return installed_font

    def generate_filename(self, ext: str = None) -> str:
        '''Generate a suitable filename from this font's name tables.'''
        family_name = self.get_family_name()
        variant = self.get_variant()

        if ext is None:
            _, ext = os.path.splitext(self.path_to_font)
            ext = ext if ext is not '' else '.otf' # Fallback to .otf

        return '{family}-{variant}{ext}'.format(
            family=family_name,
            variant=variant.print(long=True),
            ext=ext
        )

    def parse(self) -> 'Font':
        '''Parse the font's metadata from the font's name table.'''
        if not self.path_to_font or not os.path.isfile(self.path_to_font):
            raise Exception

        font = TTFont(file=self.path_to_font)
        if self.name_table is None:
            self.name_table = {}

        # Parse font file and retrieve family name and variant
        for record in font['name'].names:
            # Decode bytes
            if b'\x00' in record.string:
                data = record.string.decode('utf-16-be')
            elif b'\xa9' in record.string:
                data = codecs.decode(record.string, errors='ignore')
            else:
                data = codecs.decode(record.string, errors='ignore')

            self.name_table[str(record.nameID)] = data

        return self

    def get_name_data_from_id(self, name_id: str) -> str:
        '''Gets data from the font's name table via the name id.'''
        if self.name_table is None:
            self.parse()
        return self.name_table.get(name_id, None)

    def get_family_name(self) -> str:
        '''Get family name from the font's name tables.'''
        if self.name_table is None:
            self.parse()

        family_name = self.get_name_data_from_id(FONT_NAMEID_FAMILY)
        family_name_preferred = self.get_name_data_from_id(FONT_NAMEID_FAMILY_PREFFERED)

        return family_name_preferred if family_name_preferred else family_name

    def get_variant(self) -> FontAttribute:
        '''Get the font attributes from the font's name tables.'''
        if self.name_table is None:
            self.parse()

        variant = self.get_name_data_from_id(FONT_NAMEID_VARIANT)
        variant_preferred = self.get_name_data_from_id(FONT_NAMEID_VARIANT_PREFFERED)
        variant = variant_preferred if variant_preferred else variant

        return FontAttribute.parse(variant)

    def convert(self, path: str, font_format: 'FontFormat' = None) -> str:
        '''Converts this font to either woff or woff2 formats.'''
        _, ext = os.path.splitext(os.path.basename(self.path_to_font))
        font = TTFont(file=self.path_to_font)

        # Get font flavor
        if font_format:
            if font_format == FontFormat.WOFF:
                font.flavor = 'woff'
                ext = '.woff'
            elif font_format == FontFormat.WOFF2:
                font.flavor = 'woff2'
                ext = '.woff2'
            else:
                raise Exception # Only woff and woff2 supported for now

        # Create output directory if it doesn't exist
        path = os.path.abspath(path)
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        if os.path.isdir(path):
            path = os.path.join(path, '') # Append trailing slash

        # Generate output paths
        output_path = os.path.join(os.path.dirname(path), self.generate_filename(ext))

        # Convert and save
        font.save(file=output_path)

        return output_path
