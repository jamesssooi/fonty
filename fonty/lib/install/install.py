'''install.py: Install fonts on systems.'''
import sys
from typing import List, Union

from fonty.models.font import Font, InstalledFont

def install_fonts(fonts: Union[List[Font], Font]) -> List[InstalledFont]:
    '''OS agnostic function to install fonts on systems.'''

    if not isinstance(fonts, list):
        fonts = [fonts]

    # If no path is specified, install the font into the user's system by
    # calling the system's specific subroutine. If a path is provided, install
    # to that directory instead.
    platform_ = sys.platform
    if platform_ == 'darwin': # OSX
        from .install_osx import install_osx
        installed_fonts = install_osx(fonts)
    elif platform_ == 'win32' or platform_ == 'cygwin': # Windows
        from .install_win32 import install_win32
        installed_fonts = install_win32(fonts)

    return installed_fonts
