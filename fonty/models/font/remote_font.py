'''remote_font.py'''
import os
import shutil
from enum import Enum
from urllib.parse import urlparse

import requests
from . import Font
from fonty.lib.variants import FontAttribute
from fonty.lib.constants import TMP_DIR

class RemoteFont(object):
    '''Represents a remote font.'''

    # Meta Classes ----------------------------------------------------------- #
    class Path:
        '''Represents a font path.'''
        class Type(Enum):
            '''Represents the type of the font path.'''
            LOCAL = 1
            HTTP_REMOTE = 2

        def __init__(self, path: str, type: 'Type') -> None:
            self.path = path
            self.type = type

        @property
        def filename(self) -> str:
            '''Returns the basename of the path.'''
            if self.type == self.Type.HTTP_REMOTE:
                return os.path.basename(urlparse(self.path).path)
            elif self.type == self.Type.LOCAL:
                return os.path.basename(self.path)
            return None

    # Constructor ------------------------------------------------------------ #
    def __init__(
            self,
            remote_path: 'Path',
            filename: str,
            family: str,
            variant: FontAttribute
        ) -> None:
        self.remote_path = remote_path
        self.filename = filename
        self.family = family
        self.variant = variant

        # Parse variant if possible
        if variant is None and remote_path.type == RemoteFont.Path.Type.LOCAL:
            font = Font(path_to_font=self.remote_path.path)
            self.variant = font.variant

        # Internal properties
        self._tmp_path = None

    # Class Methods ---------------------------------------------------------- #
    def load(self, handler = None):
        '''Load this remote font and return a Font instance.'''
        from .font import Font

        # Create tmp directory
        if not os.path.exists(TMP_DIR):
            os.makedirs(TMP_DIR, exist_ok=True)

        # If path is a HTTP Remote, download the font
        if self.remote_path.type == RemoteFont.Path.Type.HTTP_REMOTE:
            request = requests.get(self.remote_path.path, stream=True)

            if handler:
                iterator = handler(self, request)
                next(iterator)

            total_bytes = b''
            for bytes_ in request.iter_content(128):
                if not bytes_: continue
                total_bytes += bytes_
                # Send total bytes downloaded to the handler. We use
                # `request.raw.tell()` instead of `len(bytes_)` to
                # account for requests with gzip compression.
                if handler:
                    iterator.send(request.raw.tell()) # total bytes received

            if handler:
                iterator.send(len(total_bytes))
                iterator.close()

            # Save file to tmp directory
            path_to_font = os.path.join(TMP_DIR, self.remote_path.filename)
            with open(path_to_font, 'wb+') as f:
                f.write(total_bytes)

        # If path is a local file, copy to tmp directory
        elif self.remote_path.type == RemoteFont.Path.Type.LOCAL:

            if handler:
                iterator = handler(self, self.remote_path.path)
                next(iterator)

            if not os.path.isfile(self.remote_path.path): raise Exception
            path_to_font = os.path.join(TMP_DIR, self.remote_path.filename)
            shutil.copy(self.remote_path.path, path_to_font)

            if handler:
                iterator.close()

        self._tmp_path = path_to_font
        return Font(path_to_font=path_to_font)

    def clear(self) -> None:
        '''Remove temporary files.'''
        if self._tmp_path and os.path.isfile(self._tmp_path):
            os.unlink(self._tmp_path)
