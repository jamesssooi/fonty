'''uninstall.py: Uninstall fonts on systems'''
import sys
from typing import List, Union
from fonty.models.font import InstalledFont

def uninstall_fonts(fonts: Union[List[InstalledFont], InstalledFont]) -> List[InstalledFont]:
    '''OS agnostic function to uninstall fonts on systems.
    
    Returns a list of succesfully uninstalled fonts.
    '''

    if not isinstance(fonts, list):
        fonts = [fonts]

    platform_ = sys.platform
    if platform_ == 'darwin': # macOS
        from .uninstall_osx import uninstall_osx
        uninstalled_fonts = uninstall_osx(fonts)
    elif platform_ == 'win32' or platform_ == 'cygwin': # Windows
        from .uninstall_win32 import uninstall_win32
        uninstalled_fonts = uninstall_win32(fonts)

    return uninstalled_fonts
