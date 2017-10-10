'''font.py: Class to manage individual fonts.'''
import os
import codecs
from enum import Enum

import requests
from fontTools.ttLib import TTFont
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
        self.name_table = None

        if variant and not isinstance(variant, FontAttribute):
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

    def parse(self) -> 'Font':
        '''Parse the font's metadata from the font's name table.'''
        if not self.local_path or not os.path.isfile(self.local_path):
            raise Exception

        font = TTFont(file=self.local_path)
        if self.name_table is None:
            self.name_table = {}

        # Parse font file and retrieve family name and variant
        for record in font['name'].names:
            # Decode bytes
            if b'\x00' in record.string:
                data = record.string.decode('utf-16-be')
            elif b'\xa9' in record.string:
                data = codecs.decode(record.string, errors='ignore')
            else:
                data = codecs.decode(record.string, errors='ignore')

            self.name_table[str(record.nameID)] = data

        return self

    def get_name_data_from_id(self, name_id: str) -> str:
        '''Gets data from the font's name table via the name id.'''
        if self.name_table is None:
            self.parse()
        return self.name_table.get(name_id, None)

    def convert(self, path: str, font_format: 'FontFormat' = None) -> str:
        '''Converts this font to either woff or woff2 formats.'''
        from fontTools.ttLib import TTFont
        filename, ext = os.path.splitext(os.path.basename(self.local_path))
        font = TTFont(file=self.local_path)

        # Get font flavor
        if font_format:
            if font_format == FontFormat.WOFF:
                font.flavor = 'woff'
                ext = '.woff'
            elif font_format == FontFormat.WOFF2:
                font.flavor = 'woff2'
                ext = '.woff2'
            else:
                raise Exception # Only woff and woff2 supported for now

        # Create output directory if it doesn't exist
        path = os.path.abspath(path)
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        if os.path.isdir(path):
            path = os.path.join(path, '') # Append trailing slash

        # Generate output paths
        output_path = '{dir}/{filename}{ext}'.format(
            dir=os.path.dirname(path),
            filename=filename,
            ext=ext
        )

        # Convert and save
        font.save(file=output_path)

        return output_path


class FontFormat(Enum):
    WOFF = 'woff'
    WOFF2 = 'woff2'
    TTF = 'ttf'
    OTF = 'otf'
