'''list_fonts.py: Cross-platform module to get list of installed fonts.'''
import os
import sys
import json

from fontTools.ttLib import TTFont
from pprint import pprint
from fonty.lib.constants import JSON_DUMP_OPTS

FONT_NAMEID_FAMILY = 1
FONT_NAMEID_VARIANT = 2
FONT_NAMEID_FAMILY_PREFFERED = 16
FONT_NAMEID_VARIANT_PREFFERED = 17

def get_font_list():
    '''Returns the list of installed user fonts in this system.'''
    platform_ = sys.platform

    if platform_ == 'darwin': # OSX
        return _get_font_list_osx()

def _get_font_list_osx():
    '''Returns the list of installer user fonts in this OSX system.'''

    font_dir = os.path.join(os.path.expanduser('~/Library/Fonts'))

    font_files = [os.path.join(font_dir, f) for f in os.listdir(font_dir)
                  if os.path.isfile(os.path.join(font_dir, f)) and
                  not f.startswith('.')]

    typefaces = {}
    for font_path in font_files:
        font = TTFont(file=font_path)
        family = None
        variant = None
        for record in font['name'].names:
            if record.nameID == FONT_NAMEID_FAMILY and family is None:
                family = str(record)
            elif record.nameID == FONT_NAMEID_VARIANT and variant is None:
                variant = str(record).lower()
            elif record.nameID == FONT_NAMEID_FAMILY_PREFFERED:
                family = str(record)
            elif record.nameID == FONT_NAMEID_VARIANT_PREFFERED:
                variant = str(record).lower()

        if family not in typefaces:
            typefaces[family] = []

        typefaces[family].append({
            'path': font_path,
            'variant': variant
        })

    pprint(typefaces)

    with open(os.path.expanduser('~/Desktop/manifest.json'), 'w') as f:
        json.dump(typefaces, f, **JSON_DUMP_OPTS)

    return font_files
