'''disable.py: Functions to disable fonts on systems'''
import os
import sys
import platform

platform_ = sys.platform

def disable_fonts(fonts):
    '''OS agnostic function to disable fonts on systems.'''

    if not isinstance(fonts, list):
        fonts = [fonts]

    # Call OS specific subroutine
    if platform_ == 'darwin': # macOS
        return disable_fonts_osx(fonts)

def disable_fonts_osx(fonts):
    '''Disable fonts on macOS systems.
    
    On macOS systems, the enabling/disabling of fonts is managed by a Property
    List (.plist) file in the user's Library/Preferences folder. The .plist file
    contains a `DisabledFonts` array that lists the file path of all the
    disable fonts.
    '''
    import plistlib
    plist_path = os.path.expanduser('~/Library/Preferences/com.apple.FontRegistry.user.plist')

    if not os.path.exists(plist_path):
        raise Exception

    with open(plist_path, 'rb') as file_:
        plist_data = plistlib.load(file_)

    from pprint import pprint
    pprint(plist_data['DisabledFonts'])