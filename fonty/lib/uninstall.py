'''install.py: Functions to uninstall fonts from systems'''
import os
from typing import List

from send2trash import send2trash
from fonty.models.font import InstalledFont

def uninstall_fonts(fonts: List[InstalledFont]):
    '''Uninstalls a list of fonts from the current system.'''
    success = []

    for font in fonts:
        # Delete font file to trash
        send2trash(font.path_to_font)
        success.append(font)

    return success
