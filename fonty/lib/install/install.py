'''install.py: Install fonts on systems.'''
import os
import sys
import shutil
import platform
from typing import List, Union

from fonty.models.font import Font, InstalledFont

def install_fonts(fonts: Union[List[Font], Font], output_dir: str = None) -> List[InstalledFont]:
    '''OS agnostic function to install fonts on systems.'''

    if not isinstance(fonts, list):
        fonts = [fonts]

    # If no path is specified, install the font into the user's system by
    # calling the system's specific subroutine. If a path is provided, install
    # to that directory instead.
    if not output_dir:
        platform_ = sys.platform
        if platform_ == 'darwin': # OSX
            from .install_osx import install_osx
            installed_fonts = install_osx(fonts)
        elif platform_ == 'win32' or platform_ == 'cygwin': # Windows
            from .install_win32 import install_win32
            installed_fonts = install_win32(fonts)
    else:
        installed_fonts = install_to_dir(fonts, output_dir)

    return installed_fonts

def install_to_dir(fonts: List[Font], output_dir: str) -> List[InstalledFont]:
    '''Install fonts into a directory.'''

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    installed_fonts = []

    for font in fonts:
        if not os.path.isfile(font.path_to_font):
            raise Exception

        installed_path = os.path.join(output_dir, font.generate_filename())
        installed_path = shutil.move(font.path_to_font, installed_path)

        # Fix permission problems in Cygwin terminals. If Cygwin uses
        # the unix version of Python, then it writes files with no
        # executable permission, rendering the font file unopenable.
        if platform.system().startswith('CYGWIN'):
            os.chmod(installed_path, 0o755)

        installed_fonts.append(InstalledFont(installed_path=installed_path))

    return installed_fonts
