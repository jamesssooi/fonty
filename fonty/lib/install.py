'''install.py: Functions to install fonts on systems'''

import os
import shutil
import sys
import subprocess
from fonty.lib.constants import APP_DIR, ROOT_DIR, IS_x64

def install_fonts(fonts, path=None):
    '''OS agnostic function to install fonts on systems'''
    platform = sys.platform

    if not isinstance(fonts, list):
        fonts = [fonts]

    # If no path is specified, install the font into the user's system by
    # calling the system's specific subroutine. If a path is provided, install
    # to that directory instead.
    if not path:
        if platform == 'darwin': # OSX
            install_osx(fonts)
            return
        elif platform == 'linux' or platform == 'linux2': # Linux
            install_linux(fonts)
            return
        elif platform == 'win32': # Windows
            install_win32(fonts)
            return
    else:
        install_to_dir(fonts, path)

def install_osx(fonts):
    '''Install a font on an OSX system'''

    for font in fonts:
        if not font.bytes: raise Exception # TODO: Raise Exception
        path = os.path.join(os.path.expanduser('~/Library/Fonts/'), font.filename)
        with open(path, 'wb+') as f:
            f.write(font.bytes)

def install_win32(fonts):
    '''Install a font on a Windows system'''

    font_dir = os.path.join(os.environ['WINDIR'], 'Fonts')
    tmp_folder = os.path.join(APP_DIR, 'tmp')

    # Create empty tmp folder and/or delete its contents
    if not os.path.exists(tmp_folder):
        os.makedirs(tmp_folder, exist_ok=True)
    else:
        for file_ in os.listdir(tmp_folder):
            path = os.path.join(tmp_folder, file_)
            if os.path.isfile(path): os.unlink(path)

    # Copy the fonts into a temp directory and then execute FontReg.exe with
    # the /copy flag. FontReg is an external utility to install fonts on Windows
    # systems. More info: http://code.kliu.org/misc/fontreg/
    for font in fonts:
        if not font.bytes: raise Exception # TODO: Raise Exception

        # Check if font already installed
        if os.path.isfile(os.path.join(font_dir, font.filename)): continue

        path = os.path.join(tmp_folder, font.filename)
        with open(path, 'wb+') as f:
            f.write(font.bytes)
    
    if IS_x64:
        fontreg_source = os.path.join(ROOT_DIR, 'ext\\fontreg\\x64\\FontReg.exe')
    else:
        fontreg_source = os.path.join(ROOT_DIR, 'ext\\fontreg\\x32\\FontReg.exe')

    shutil.copy2(fontreg_source, tmp_folder)

    # Run FontReg.exe
    os.chdir(tmp_folder)
    path_to_fontreg = os.path.join(tmp_folder, 'FontReg.exe')
    subprocess.call([path_to_fontreg, '/copy'])
    os.chdir(ROOT_DIR)

    # Empty tmp folder
    for file_ in os.listdir(tmp_folder):
        path = os.path.join(tmp_folder, file_)
        if os.path.isfile(path): os.unlink(path)

def install_linux(fonts):
    '''Install a font on a Linux system'''
    pass

def install_to_dir(fonts, dir_):
    '''Install fonts to a directory.'''

    if not os.path.exists(dir_):
        os.makedirs(dir_, exist_ok=True)
    
    for font in fonts:
        if not font.bytes: raise Exception # TODO: Raise Exception
        path = os.path.join(dir_, font.filename)
        with open(path, 'wb+') as f:
            f.write(font.bytes)
