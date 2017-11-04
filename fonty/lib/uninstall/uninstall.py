'''uninstall.py: Uninstall fonts on systems'''
import sys
from typing import List, Union
from fonty.models.font import InstalledFont

def uninstall_fonts(fonts: Union[List[InstalledFont], InstalledFont]) -> bool:
    '''OS agnostic function to uninstall fonts on systems.'''

    if not isinstance(fonts, list):
        fonts = [fonts]

    platform_ = sys.platform
    if platform_ == 'darwin': # macOS
        from .uninstall_osx import uninstall_osx
        result = uninstall_osx(fonts)
    elif platform_ == 'win32' or platform_ == 'cygwin': # Windows
        from .uninstall_win32 import uninstall_win32
        result = uninstall_win32(fonts)

    return result
