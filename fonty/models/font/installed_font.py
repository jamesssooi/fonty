'''installed_font.py'''
from typing import Optional
from .font import Font

class InstalledFont(Font):
    '''Represents an installed font on the computer.'''

    # Class Properties ------------------------------------------------------- #
    installed_path: str
    registry_name: Optional[str]

    # Constructor ------------------------------------------------------------ #
    def __init__(self, installed_path: str, registry_name: str = None, **kwargs) -> None:
        super().__init__(path_to_font=installed_path, **kwargs)
        self.installed_path = installed_path
        self.registry_name = registry_name

    # Class Methods ---------------------------------------------------------- #
    def uninstall(self) -> bool:
        '''Uninstall this font from the system.'''
        from fonty.lib.uninstall import uninstall_fonts
        return bool(uninstall_fonts(self))
