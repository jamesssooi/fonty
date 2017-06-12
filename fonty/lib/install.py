'''install.py: Functions to install fonts on systems'''

import os
import sys

def install(font, path=None):
    '''OS agnostic function to install fonts on systems'''
    platform = sys.platform
    
    if platform == 'darwin': # OSX
        install_osx(font)
    elif platform == 'linux' or platform == 'linux2':
        install_linux(font)
    elif platform == 'win32':
        install_win32(font)

def install_osx(font):
    '''Install a font on an OSX system'''
    path = os.path.join(os.path.expanduser('~/Library/Fonts/'), font.filename)

    if not font.bytes:
        raise Exception # TODO: Raise Exception
    
    with open(path, 'wb+') as f:
        f.write(font.bytes)

def install_win32(font):
    '''Install a font on a Windows system'''
    pass

def install_linux(font):
    '''Install a font on a Linux system'''
    pass
