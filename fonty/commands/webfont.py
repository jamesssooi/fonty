'''fonty.commands.webfont.py: Command-line interface to create webfonts.'''
import os
import sys
import glob
import timeit
from typing import Tuple

import click
from termcolor import colored
from fonty.lib.constants import COLOR_INPUT
from fonty.lib.variants import FontAttribute
from fonty.models.manifest import Manifest
from fonty.models.font import Font, FontFormat

@click.command('webfont')
@click.argument('files', nargs=-1, required=False, type=click.STRING)
@click.option('--typeface', '-t', type=click.STRING)
@click.option('--output', '-o', type=click.Path(file_okay=False, dir_okay=True, writable=True, resolve_path=True))
@click.option('--family-name', type=click.STRING)
def cli_webfont(files: str, typeface: str, output: str, family_name: str):
    '''Converts to webfont'''

    start_time = timeit.default_timer()

    # Get list of files
    if typeface:
        try:
            manifest = Manifest.load()
        except FileNotFoundError:
            manifest = Manifest.generate()
            manifest.save()

        typeface = manifest.get(typeface)
        if typeface is None:
            click.echo("No typeface found with the name '{}'".format(colored(typeface, COLOR_INPUT)))
            sys.exit(1)

        font_paths = [font.local_path for font in typeface.get_fonts()]
    elif files:
        # On Unix based systems, a glob argument of *.ttf will be automatically
        # expanded by the shell. Meanwhile on Windows systems or if the pattern
        # is surrounded with quotes, it will be passed to this function as is.
        # Here we iterate through it and run the glob function anyway to be safe
        font_paths = [glob.glob(path) for path in files]
        font_paths = [item for sublist in font_paths for item in sublist] # Flatten list
        font_paths = [os.path.abspath(path) for path in font_paths] # Get absolute paths
        if not font_paths:
            click.echo("No font files found with the pattern '{}'".format(colored(files[0], COLOR_INPUT)))
            sys.exit(1)
    else:
        click.echo("No typeface name or file paths provided.")
        sys.exit(1)

    # Create font objects
    fonts = [Font(local_path=font_path) for font_path in font_paths]

    # Convert files to web-compatible formats (woff, woff2 and otf/ttf)
    output_dir = output if output else os.getcwd()
    results = []

    for font in fonts:
        # Get family and variant name
        family_name_preferred = font.get_name_data_from_id('16')
        family_name = family_name_preferred if family_name_preferred else font.get_name_data_from_id('1')
        variant_preferred = font.get_name_data_from_id('17')
        variant = variant_preferred if variant_preferred else font.get_name_data_from_id('2')

        # Parse variant
        variant = FontAttribute.parse(variant)
        font_weight = variant.weight.value.css
        font_style = variant.style.value.css
        font_stretch = variant.stretch.value.css

        paths = []

        # Default (TTF/OTF)
        _, ext = os.path.splitext(font.local_path)
        paths.append({'path': font.convert(output_dir), 'format': ext[1:]})

        # Convert to WOFF
        paths.append({'path': font.convert(output_dir, FontFormat.WOFF), 'format': 'woff'})

        # Convert to WOFF2
        paths.append({'path': font.convert(output_dir, FontFormat.WOFF2), 'format': 'woff2'})

        results.append({
            'family_name': family_name,
            'font_weight': font_weight,
            'font_style': font_style,
            'font_stretch': font_stretch,
            'formats': paths
        })

    # Create @font-face declaration
    declarations = []
    for font in results:
        sources = [
            FONT_FACE_SRC_TEMPLATE.format(
                path=os.path.basename(font_format['path']),
                format=FONT_FORMAT_CSS_MAP.get(font_format['format'], font_format['format'])
            ) for font_format in font['formats']
        ]

        declaration = FONT_FACE_TEMPLATE.format(
            family=font['family_name'],
            weight=font['font_weight'],
            style=font['font_style'],
            stretch=font['font_stretch'],
            src=',\n       '.join(sources)
        )

        declarations.append(declaration)

    for x in declarations: print(x)


FONT_FACE_TEMPLATE = '''
@font-face {{
  font-family: '{family}';
  font-weight: {weight};
  font-style: {style};
  font-stretch: {stretch};
  src: {src};
}}
'''

FONT_FACE_SRC_TEMPLATE = '''url('{path}') format('{format}')'''

FONT_FORMAT_CSS_MAP = {
    'woff': 'woff',
    'woff2': 'woff2',
    'otf': 'opentype',
    'ttf': 'truetype',
}
