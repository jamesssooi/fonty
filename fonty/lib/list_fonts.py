'''list_fonts.py: Cross-platform module to get list of installed fonts.'''
import os
import sys
import json
import codecs
from pprint import pprint
from typing import List

from fontTools.ttLib import TTFont, TTLibError
from fonty.lib.constants import JSON_DUMP_OPTS
from fonty.lib.variants import FontAttribute
from fonty.models.typeface import Typeface
from fonty.models.font import Font

FONT_NAMEID_FAMILY = 1
FONT_NAMEID_VARIANT = 2
FONT_NAMEID_FAMILY_PREFFERED = 16
FONT_NAMEID_VARIANT_PREFFERED = 17

def get_user_fonts():
    '''Returns the list of installed user fonts in this system.'''
    platform_ = sys.platform

    if platform_ == 'darwin': # OSX
        return _get_user_fonts_osx()
    elif platform_ == 'win32' or platform_ == 'cygwin': # Windows
        return _get_user_fonts_win()

def _get_user_fonts_osx() -> List[Typeface]:
    '''Returns the list of installed user fonts in this OSX system.'''
    font_dir = os.path.join(os.path.expanduser('~/Library/Fonts'))
    font_files = [os.path.join(font_dir, f) for f in os.listdir(font_dir)
                  if os.path.isfile(os.path.join(font_dir, f)) and
                  not f.startswith('.')]

    # Parse font files
    data = parse_fonts(font_files)

    # Convert typeface data into Typeface instances
    typefaces = []
    for _, val in data.items():
        fonts = []
        for font in val['fonts']:
            fonts.append(Font(variant=font['variant'],
                              local_path=font['local_path']))
        typefaces.append(Typeface(name=val['name'], fonts=fonts))

    # with open(os.path.expanduser('~/Desktop/manifest.json'), 'w') as f:
    #     json.dump(typefaces, f, **JSON_DUMP_OPTS)

    return typefaces

def _get_user_fonts_win() -> List[Typeface]:
    '''Returns the list of installed fonts in this Windows system.'''
    font_dir = os.path.join(os.environ['WINDIR'], 'Fonts')
    font_files = [os.path.join(font_dir, f) for f in os.listdir(font_dir)
                  if os.path.isfile(os.path.join(font_dir, f)) and
                  not f.startswith('.')]

    # Parse font files
    data = parse_fonts(font_files)

    # Convert typeface data into Typeface instances
    typefaces = []
    for _, val in data.items():
        fonts = []
        for font in val['fonts']:
            fonts.append(Font(variant=font['variant'],
                              local_path=font['local_path']))
        typefaces.append(Typeface(name=val['name'], fonts=fonts))

    return typefaces

def parse_fonts(fonts: List[str]):
    '''Parse a list of font paths and group them into their families.'''
    typefaces = {}

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

        # Append to typefaces object
        if family not in typefaces:
            typefaces[family] = {'name': family, 'fonts': []}

        typefaces[family]['fonts'].append({
            'variant': variant,
            'local_path': font_path
        })

    return typefaces
