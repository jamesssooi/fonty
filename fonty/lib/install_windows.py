'''install_windows.py: Install fonts on Windows programatically'''
import os
import ctypes
import winreg
from ctypes import wintypes
from typing import List

import winshell
import win32api
import ctypes
import win32con
from fonty.models.font import Font
from fonty.lib.constants import APP_DIR

def install_fonts(fonts: List[Font]):
    '''Install fonts on a Windows system.

    On Windows, installing fonts is a rather cumbersome process involving the
    Win32 native APIs and registries.
    '''
    font_dir = os.path.join(os.environ['WINDIR'], 'Fonts')
    tmp_folder = os.path.join(APP_DIR, 'tmp')

    if not isinstance(fonts, list):
        fonts = [fonts]

    # Create empty tmp folder and/or delete its contents
    if not os.path.exists(tmp_folder):
        os.makedirs(tmp_folder, exist_ok=True)
    else:
        for file_ in os.listdir(tmp_folder):
            path = os.path.join(tmp_folder, file_)
            if os.path.isfile(path):
                os.unlink(path)

    for idx, font in enumerate(fonts):
        # Firstly, we copy the font files into the %WINDIR%\Fonts directory.
        # We use the native Windows shell (Windows Explorer) to copy the files so
        # that fonty doesn't need to run in an elevated command prompt. Instead,
        # Windows will automatically ask for permission in the Copy dialog.

        # Write font files to tmp folder
        path = os.path.join(tmp_folder, font.filename)
        with open(path, 'wb+') as f:
            f.write(font.bytes)

        # Copy to %WINDIR%\Fonts
        to_path = os.path.join(font_dir, font.filename)
        winshell.move_file(path, to_path)

        # Then we call the AddFontResource Win32 API to make the font available
        # in the current session.
        gdi32 = ctypes.WinDLL('gdi32')
        gdi32.AddFontResourceW.argtypes = (ctypes.c_wchar_p,)
        gdi32.AddFontResourceW(ctypes.c_wchar_p(to_path))

        # Then we add the font into the registry so that it is persistent after
        # rebooting.
        reg_path = 'SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Fonts'
        font_registry = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(font_registry, font.filename, 0, winreg.REG_SZ, font.filename)

        # And then finally, we broadcast a message to all top-level windows that
        # the font list has changed.
        win32api.PostMessage(win32con.HWND_BROADCAST, win32con.WM_FONTCHANGE)

        fonts[idx].local_path = to_path
    
    return fonts

def uninstall_fonts(fonts: List[Font]):
    '''Uninstall fonts on a Windows system.'''

    for idx, font in enumerate(fonts):
        # Firstly, we call the RemoveFontResource Win32 API to remove the font
        # from the current session.
        gdi32 = ctypes.WinDLL('gdi32')
        gdi32.RemoveFontResourceW.argtype = (ctypes.c_wchar_p,)
        gdi32.RemoveFontResourceW(ctypes.c_wchar_p(font.local_path))

        # Then we remove the font from the registry
        reg_path = 'SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Fonts'
        font_registry = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_WRITE)
        winreg.DeleteValue(font_registry, font.filename)

        # Then we broadcast a message to all top-level windows that the font
        # list has changed.
        win32api.PostMessage(win32con.HWND_BROADCAST, win32con.WM_FONTCHANGE)

        # Finally, we remove the font file
        os.remove(font.local_path)