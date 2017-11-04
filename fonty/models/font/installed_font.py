'''installed_font.py'''

from .font import Font

class InstalledFont(Font):
    def __init__(self, installed_path: str, registry_name: str = None, **kwargs) -> None:
        super().__init__(path_to_font=installed_path, **kwargs)
        self.installed_path = installed_path
        self.registry_name = registry_name

    def uninstall(self) -> bool:
        '''Uninstall this font from the system.'''
        from fonty.lib.uninstall import uninstall_fonts
        return uninstall_fonts(self)
