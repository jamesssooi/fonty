'''font.py: Class to manage individual fonts.'''

import requests
from click import style
from fonty.lib.install import install_fonts
from fonty.lib.variants import FontAttribute

class Font(object):
    '''Class to manage individual fonts.'''

    def __init__(self, filename=None, local_path=None, remote_path=None,
                 variant=None, raw_bytes=None):
        self.filename = filename
        self.local_path = local_path
        self.remote_path = remote_path
        self.bytes = raw_bytes

        if not isinstance(variant, FontAttribute):
            variant = FontAttribute.parse(variant)
        self.variant = variant

    def download(self, handler=None):
        '''Download this font and return its bytes. Also appends the bytes as a property to self.'''

        if not self.remote_path:
            raise Exception # TODO: Raise Exception

        request = requests.get(self.remote_path, stream=True)
        if handler:
            iterator = handler(self, request)
            next(iterator)

        self.bytes = b''
        for bytes_ in request.iter_content(128):
            if bytes_:
                self.bytes += bytes_

                # Send total bytes downloaded to the handler. We use
                # `request.raw.tell()` instead of `len(bytes_)` to
                # account for requests with gzip compression.
                if handler:
                    iterator.send(request.raw.tell()) # total bytes received

        return self.bytes

    def install(self, path=None):
        '''Installs this font to the system.'''
        install_fonts(self, path)

    def to_pretty_string(self):
        '''Prints the contents of this font as ANSI formatted string.'''
        variation = '{css} {descriptive}'.format(
            css=self.variant,
            descriptive='({})'.format(str(self.variant))
        )

        return style('{variation} - {path}'.format(
            variation=variation,
            path=self.local_path
        ), dim=True)
