'''uninstall_win32.py: Uninstall fonts on Windows'''
import os
import ctypes
from typing import List

import winreg
import winshell
import win32api
import win32con
from fonty.models.font import InstalledFont

def uninstall_win32(fonts: List[InstalledFont]) -> List[InstalledFont]:
    '''Uninstall fonts on a Windows system'''
    uninstalled_fonts = []

    # Store a copy of the registry in memory
    reg_path = 'SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Fonts'
    font_reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
    value_count = winreg.QueryInfoKey(font_reg)[1]
    registry_values = [winreg.EnumValue(font_reg, i) for i in range(0, value_count)]

    for font in fonts:
        # Firstly, we call the RemoveFontResource Win32 API to remove the font
        # from the current session.
        gdi32 = ctypes.WinDLL('gdi32')
        gdi32.RemoveFontResourceW.argtype = (ctypes.c_wchar_p,)
        res = gdi32.RemoveFontResourceW(ctypes.c_wchar_p(font.path_to_font))

        # Find the registry value name to delete
        registry_value = os.path.basename(font.path_to_font)
        registry_value_name = next((
            val[0] for val in registry_values if val[1] == registry_value
        ), None)

        # Then we remove the font from the registry
        if registry_value_name:
            reg_path = 'SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Fonts'
            font_reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_WRITE)
            winreg.DeleteValue(font_reg, registry_value_name)

        # Then we delete the file
        winshell.delete_file(font.path_to_font)
        uninstalled_fonts.append(font)

        # And finally, we broadcast a message to all top-level windows that the
        # font list has changed.
        win32api.PostMessage(win32con.HWND_BROADCAST, win32con.WM_FONTCHANGE)


    return uninstalled_fonts
