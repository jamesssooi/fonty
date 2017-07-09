'''install.py: Functions to uninstall fonts from systems'''
import os
from send2trash import send2trash

def uninstall_fonts(fonts):
    '''Uninstalls a list of fonts from the current system.'''
    success = []
    failed = []

    for font in fonts:
        if not font.local_path:
            failed.append(font)
            continue

        if not os.path.exists(font.local_path):
            failed.append(font)
            continue

        # Delete font file to trash
        send2trash(font.local_path)
        success.append(font)

    return success, failed
