'''installed_font.py'''

from .font import Font

class InstalledFont(Font):
    def __init__(self, installed_path: str, registry_path: str = None, **kwargs) -> None:
        super().__init__(path_to_font=installed_path, **kwargs)
        self.installed_path = installed_path
        self.registry_path = registry_path

    def uninstall(self) -> bool:
        '''Uninstall this font from the system.'''
        pass
