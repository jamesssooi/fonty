'''remote_font.py'''
import os

import requests
from fonty.lib.variants import FontAttribute
from fonty.lib.constants import APP_DIR, TMP_DIR

class RemoteFont(object):

    def __init__(self, remote_path: str, filename: str, family: str, variant: FontAttribute):
        self.remote_path = remote_path
        self.filename = filename
        self.family = family
        self.variant = variant

        # Internal properties
        self._tmp_path = None

    def download(self, path: str = None, handler = None):
        '''Download this font into a tmp directory and return a Font instance.'''
        from .font import Font

        request = requests.get(self.remote_path, stream=True)
        if handler:
            iterator = handler(self, request)
            next(iterator)

        total_bytes = b''
        for bytes_ in request.iter_content(128):
            if bytes_:
                total_bytes += bytes_

                # Send total bytes downloaded to the handler. We use
                # `request.raw.tell()` instead of `len(bytes_)` to
                # account for requests with gzip compression.
                if handler:
                    iterator.send(request.raw.tell()) # total bytes received

        # Save font to directory if provided, or to a tmp directory if not
        output_folder = path if path else TMP_DIR
        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)
        path_to_font = os.path.join(output_folder, self.filename)

        with open(path_to_font, 'wb+') as f:
            f.write(total_bytes)

        self._tmp_path = path_to_font

        return Font(path_to_font=path_to_font)