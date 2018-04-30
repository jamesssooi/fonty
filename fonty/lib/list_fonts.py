'''list_fonts.py: Cross-platform module to get list of installed fonts.'''
import os
import sys
import codecs
from typing import List

from fontTools.ttLib import TTFont, TTLibError
from fonty.lib.variants import FontAttribute
from fonty.models.font import Font, FontFamily

FONT_NAMEID_FAMILY = 1
FONT_NAMEID_VARIANT = 2
FONT_NAMEID_FAMILY_PREFFERED = 16
FONT_NAMEID_VARIANT_PREFFERED = 17

def get_user_fonts() -> List[FontFamily]:
    '''Returns the list of installed user fonts in this system.'''
    platform_ = sys.platform

    if platform_ == 'darwin': # OSX
        return _get_user_fonts_osx()
    elif platform_ == 'win32' or platform_ == 'cygwin': # Windows
        return _get_user_fonts_win()
    else:
        raise Exception("Unsupported platform")

    return None

def _get_user_fonts_osx() -> List[FontFamily]:
    '''Returns the list of installed user fonts in this OSX system.'''
    font_dir = os.path.join(os.path.expanduser('~/Library/Fonts'))
    font_files = [os.path.join(font_dir, f) for f in os.listdir(font_dir)
                  if os.path.isfile(os.path.join(font_dir, f)) and
                  not f.startswith('.')]

    # Parse font files
    data = parse_fonts(font_files)

    # Convert font family data into FontFamily instances
    families = []
    for family_name, val in data.items():
        fonts = [Font(
            path_to_font=font['local_path'],
            family=family_name,
            variant=font['variant']
        ) for font in val['fonts']]
        families.append(FontFamily(name=val['name'], fonts=fonts))

    return families

def _get_user_fonts_win() -> List[FontFamily]:
    '''Returns the list of installed fonts in this Windows system.'''
    font_dir = os.path.join(os.environ['WINDIR'], 'Fonts')
    font_files = [os.path.join(font_dir, f) for f in os.listdir(font_dir)
                  if os.path.isfile(os.path.join(font_dir, f)) and
                  not f.startswith('.')]

    # Parse font files
    data = parse_fonts(font_files)

    # Convert font family data into FontFamily instances
    families = []
    for family_name, val in data.items():
        fonts = [Font(
            path_to_font=font['local_path'],
            family=family_name,
            variant=font['variant']
        ) for font in val['fonts']]
        families.append(FontFamily(name=val['name'], fonts=fonts))

    return families

def parse_fonts(fonts: List[str]):
    '''Parse a list of font paths and group them into their families.'''
    families: dict = {}

    for font_path in fonts:
        try:
            font = TTFont(file=font_path)
        except TTLibError:
            continue
        family = None
        variant = None

        # Parse font file and retrieve family name and variant
        for record in font['name'].names:

            # Decode bytes
            if b'\x00' in record.string:
                data = record.string.decode('utf-16-be')
            elif b'\xa9' in record.string:
                data = codecs.decode(record.string, errors='ignore')
            else:
                data = codecs.decode(record.string, errors='ignore')

            if record.nameID == FONT_NAMEID_FAMILY and family is None:
                family = data
            elif record.nameID == FONT_NAMEID_FAMILY_PREFFERED:
                family = data
            elif record.nameID == FONT_NAMEID_VARIANT and variant is None:
                variant = data.lower()
            elif record.nameID == FONT_NAMEID_VARIANT_PREFFERED:
                variant = data.lower()

        if variant is not None:
            variant = FontAttribute.parse(variant)

        # Append to families object
        if family not in families:
            families[family] = {'name': family, 'fonts': []}

        families[family]['fonts'].append({
            'variant': variant,
            'local_path': font_path
        })

    return families

def get_user_fonts_count() -> int:
    '''Returns the total number of installed user fonts in this system.'''
    platform_ = sys.platform

    if platform_ == 'darwin': # OSX
        return _get_user_fonts_count_osx()
    elif platform_ == 'win32' or platform_ == 'cygwin': # Windows
        return _get_user_fonts_count_win()
    else:
        raise Exception("Unsupported platform")

    return None

def _get_user_fonts_count_osx() -> int:
    '''Returns the total number of installed user fonts in this macOS system.'''
    font_dir = os.path.join(os.path.expanduser('~/Library/Fonts'))
    font_files = [name for name in os.listdir(font_dir)
                  if os.path.isfile(os.path.join(font_dir, name))
                  and not name.startswith('.')]
    return len(font_files)

def _get_user_fonts_count_win() -> int:
    '''Returns the total number of installed user fonts in this Windows system.'''
    font_dir = os.path.join(os.environ['WINDIR'], 'Fonts')
    font_files = [os.path.join(font_dir, f) for f in os.listdir(font_dir)
                  if os.path.isfile(os.path.join(font_dir, f)) and
                  not f.startswith('.')]
    return len(font_files)
