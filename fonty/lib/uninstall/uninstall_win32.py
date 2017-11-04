'''uninstall_win32.py: Uninstall fonts on Windows'''
import os
import ctypes
from typing import List

import winreg
import win32api
import win32con
from fonty.models.font import InstalledFont

def uninstall_win32(fonts: List[InstalledFont]) -> bool:
    '''Uninstall fonts on a Windows system'''

    for font in fonts:
        # Firstly, we call the RemoveFontResource Win32 API to remove the font
        # from the current session.
        gdi32 = ctypes.WinDLL('gdi32')
        gdi32.RemoveFontResourceW.argtype = (ctypes.c_wchar_p,)
        gdi32.RemoveFontResourceW(ctypes.c_wchar_p(font.path_to_font))

        # Then we remove the font from the registry
        reg_path = 'SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Fonts'
        font_reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_WRITE)
        winreg.DeleteValue(font_reg, font.registry_name)

        # Then we broadcast a message to all top-level windows that the font
        # list has changed.
        win32api.PostMessage(win32con.HWND_BROADCAST, win32con.WM_FONTCHANGE)

        # Finally, we remove the font file
        os.remove(font.path_to_font)

    return True
