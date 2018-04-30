'''uninstall_win32.py: Uninstall fonts on Windows'''
import os
import ctypes
import shutil
import errno
from typing import List

import winreg
import winshell
import win32api
import win32con
from win32com.shell import shell, shellcon
from fonty.models.font import InstalledFont
from fonty.lib.constants import TMP_DIR

def uninstall_win32(fonts: List[InstalledFont]) -> List[InstalledFont]:
    '''Uninstall fonts on a Windows system'''
    uninstalled_fonts = []

    # Filter fonts that do not exist
    for font in fonts:
        if not os.path.isfile(font.path_to_font):
            uninstalled_fonts.append(font)
            fonts.remove(font)

    # Remove all fonts from the session
    gdi32 = ctypes.WinDLL('gdi32')
    gdi32.RemoveFontResourceW.argtype = (ctypes.c_wchar_p,)
    for font in fonts:
        gdi32.RemoveFontResourceW(ctypes.c_wchar_p(font.path_to_font))

    # Delete font files
    deleted_fonts = []
    flags = shellcon.FOF_WANTMAPPINGHANDLE | shellcon.FOF_ALLOWUNDO | shellcon.FOF_SILENT | shellcon.FOF_NOCONFIRMATION
    for font in fonts:
        # Make a temp copy
        path_to_copy = os.path.join(TMP_DIR, os.path.basename(font.path_to_font))
        shutil.copy2(font.path_to_font, path_to_copy)

        # Delete file using shell
        return_code, aborted, _ = shell.SHFileOperation(
            (0, shellcon.FO_DELETE, font.path_to_font, '', flags, None, None)
        )

        if return_code != 0 or aborted:
            current_font = font
            break
        else:
            deleted_fonts.append({'original': font.path_to_font, 'copy': path_to_copy})

    # If font deletion fails (file in use, etc), re-add the fonts into the
    # current session to revert to previous state
    if return_code != 0 or aborted:
        for deleted_font in deleted_fonts:
            winshell.move_file(deleted_font['copy'], deleted_font['original'])
        for font in fonts:
            gdi32.AddFontResourceW(ctypes.c_wchar_p(font.path_to_font))

        if return_code == 124: # Font file in use
            raise IOError(
                errno.EACCES,
                'File is being used by another process',
                os.path.basename(current_font.path_to_font)
            )

    # Remove font from registry
    reg_path = 'SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Fonts'
    font_reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
    value_count = winreg.QueryInfoKey(font_reg)[1]
    registry_values = [winreg.EnumValue(font_reg, i) for i in range(0, value_count)]
    for font in fonts:
        registry_value = os.path.basename(font.path_to_font)
        registry_value_name = next((
            val[0] for val in registry_values if val[1] == registry_value
        ), None)

        if registry_value_name:
            reg_path = 'SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Fonts'
            font_reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_WRITE)
            winreg.DeleteValue(font_reg, registry_value_name)

    # Remove temporary files
    for deleted_font in deleted_fonts:
        winshell.delete_file(deleted_font['copy'], no_confirm=True)

    # Broadcast message to all top-level windows that the font list has changed.
    win32api.PostMessage(win32con.HWND_BROADCAST, win32con.WM_FONTCHANGE)

    return fonts
