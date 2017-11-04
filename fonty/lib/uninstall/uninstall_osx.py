'''uninstall_osx.py: Uninstall fonts on macOS'''
from typing import List
from send2trash import send2trash
from fonty.models.font import InstalledFont

def uninstall_osx(fonts: List[InstalledFont]) -> List[InstalledFont]:
    '''Uninstall fonts on a macOS system'''
    uninstalled_fonts = []
    for font in fonts:
        send2trash(font.path_to_font)
        uninstalled_fonts.append(font)
    return uninstalled_fonts
