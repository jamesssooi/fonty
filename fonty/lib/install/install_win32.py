'''install_win32.py: Install fonts on Windows'''
import os
import ctypes
from typing import List

import winshell
import winreg
import win32api
import win32con
from fonty.models.font import Font, InstalledFont

def install_win32(fonts: List[Font]) -> List[InstalledFont]:
    '''Install fonts on a Windows system.

    Installing fonts on Windows is quite a bit more complicated. Naively placing
    the font files in %WINDIR%/Fonts/ will not work. We will also need to call
    the appropriate Win32 native APIs, as well as update the registry.

    Since dealing with fonts on Windows requires administrative rights, fonty
    will also need to be run in an elevated environment, which creates a
    terrible UX for fonty.

    Possible workaround:
    https://stackoverflow.com/questions/130763/request-uac-elevation-from-within-a-python-script
    '''
    font_dir = os.path.join(os.environ['WINDIR'], 'Fonts')
    installed_fonts: List[InstalledFont] = []

    for font in fonts:
        # Firstly, we copy the font files into the %WINDIR%/Fonts directory
        installed_path = os.path.join(font_dir, font.generate_filename())
        winshell.move_file(font.path_to_font, installed_path, rename_on_collision=False, no_confirm=True)

        # Then we call the AddFontResource Win32 API to make the font available
        # in the current session
        gdi32 = ctypes.WinDLL('gdi32')
        gdi32.AddFontResourceW.argtypes = (ctypes.c_wchar_p,)
        gdi32.AddFontResourceW(ctypes.c_wchar_p(installed_path))

        # Then we add the font into the registry so that it is persistent across
        # system reboots
        reg_value_name = '{family} {variant}'.format(
            family=font.family,
            variant=font.variant.print(long=True)
        )
        reg_value = os.path.basename(installed_path)
        reg_path = 'SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Fonts'
        font_reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(font_reg, reg_value_name, 0, winreg.REG_SZ, reg_value)

        installed_fonts.append(InstalledFont(
            installed_path=installed_path,
            registry_name=(reg_value_name)
        ))

    # Broadcast a message to all top-level windows that the fonts has changed
    win32api.PostMessage(win32con.HWND_BROADCAST, win32con.WM_FONTCHANGE)

    return installed_fonts
