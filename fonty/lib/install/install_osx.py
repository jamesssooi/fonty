'''install_osx.py: Install fonts on macOS'''
import os
from typing import List
from fonty.models.font import Font, InstalledFont

def install_osx(fonts: List[Font]) -> List[InstalledFont]:
    '''Install fonts on an OSX system.

    Installing fonts on OSX systems is a breeze. The only action required is to
    place the font files in `~/Library/Fonts/` and OSX will take care of the rest.
    '''
    font_dir = os.path.expanduser('~/Library/Fonts/')
    installed_fonts = []

    for font in fonts:
        install_path = os.path.join(font_dir, font.generate_filename())
        os.rename(font.path_to_font, install_path)
        installed_fonts.append(InstalledFont(installed_path=install_path))

    return installed_fonts
