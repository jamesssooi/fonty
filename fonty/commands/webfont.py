'''fonty.commands.webfont.py: Command-line interface to create webfonts.'''
import os
import sys
import glob
import timeit

import click
from termcolor import colored
from fonty.lib.constants import COLOR_INPUT
from fonty.lib.task import Task, TaskStatus
from fonty.lib.progress import ProgressBar
from fonty.lib.variants import FontAttribute
from fonty.models.manifest import Manifest
from fonty.models.font import Font, FontFormat


@click.command('webfont', short_help='Generate webfonts')
@click.argument(
    'files',
    nargs=-1,
    required=False,
    type=click.STRING)
@click.option(
    '--typeface', '-t',
    type=click.STRING,
    help='Specify an existing installed font.')
@click.option(
    '--output', '-o',
    type=click.Path(file_okay=False, dir_okay=True, writable=True),
    help='Output the converted webfonts in this directory.')
@click.pass_context
def cli_webfont(ctx, files: str, typeface: str, output: str):
    '''Generate webfonts and its @font-face declarations.

    Fonts are converted to .woff and .woff2 formats. Their respective @font-face
    declarations are placed in a file named 'styles.css'

    \b
    Example usage:
    ==============

    \b
      Create webfonts of all .ttf fonts in this directory:
      >>> fonty webfont *.ttf

    \b
      Create webfonts of an existing installed font from this computer:
      >>> fonty webfont --typeface "Open Sans"

    \b
      Create and output webfonts into a directory named "fonts":
      >>> fonty webfont --typeface "Open Sans" --output ./fonts
    '''

    start_time = timeit.default_timer()

    # Get list of files
    if typeface:
        try:
            manifest = Manifest.load()
        except FileNotFoundError:
            manifest = Manifest.generate()
            manifest.save()

        typeface_result = manifest.get(typeface)
        if typeface_result is None:
            click.echo(
                "No typeface found with the name '{typeface}'.\nDid you forget to wrap the name in quotes?".format(
                    typeface=colored(typeface, COLOR_INPUT)
                )
            )
            sys.exit(1)

        font_paths = [font.local_path for font in typeface_result.get_fonts()]
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
        click.echo(ctx.get_help())
        sys.exit(1)

    # Create font objects
    fonts = [Font(local_path=font_path) for font_path in font_paths]

    # Print task message
    task = Task('Generating webfonts for ({}) fonts...'.format(len(fonts)))
    bar = ProgressBar(total=len(fonts) * 2)

    # Convert files to web-compatible formats (woff, woff2 and otf/ttf)
    output_dir = output if output else os.getcwd()
    results = []
    for font in fonts:

        filename, ext = os.path.splitext(os.path.basename(font.local_path))

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
        paths.append({'path': font.convert(output_dir), 'format': ext[1:]})

        # Convert to WOFF
        bar.increment()
        task.message = 'Converting {}.woff... {}'.format(filename, bar)
        paths.append({'path': font.convert(output_dir, FontFormat.WOFF), 'format': 'woff'})

        # Convert to WOFF2
        bar.increment()
        task.message = 'Converting {}.woff2... {}'.format(filename, bar)
        paths.append({'path': font.convert(output_dir, FontFormat.WOFF2), 'format': 'woff2'})

        results.append({
            'family_name': family_name,
            'font_weight': font_weight,
            'font_style': font_style,
            'font_stretch': font_stretch,
            'formats': paths
        })

    task.stop(message='Converted ({}) font file(s)'.format(len(fonts)))

    # Create @font-face declaration
    task = Task(message='Creating @font-face declaration(s)...')
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

    # Write declaration to a new CSS file
    css_path = os.path.join(output_dir, 'styles.css')
    with open(file=css_path, mode='w+') as f:
        f.write(META)
        f.write('\n'.join(declarations))

    task.stop(message='Generated @font-face declaration(s) in styles.css')

    # Print completion message
    if typeface:
        task = Task(
            message="Generated webfonts for '{typeface}' in {output}".format(
                typeface=colored(typeface, COLOR_INPUT),
                output=os.path.abspath(output_dir)
            ),
            asynchronous=False,
            status=TaskStatus.SUCCESS
        )
    else:
        task = Task(
            message="Generated webfonts in {output}".format(output=os.path.abspath(output_dir)),
            asynchronous=False,
            status=TaskStatus.SUCCESS
        )

    # Calculate execution time
    end_time = timeit.default_timer()
    total_time = end_time - start_time
    click.echo('Done in {}s'.format(round(total_time, 2)))


# ==============================================================================
# TEMPLATES
# ==============================================================================
META = '''/* Auto-generated by Fonty, a friendly CLI tool for fonts. */\n\n'''

FONT_FACE_TEMPLATE = \
'''\
@font-face {{
  font-family: '{family}';
  font-weight: {weight};
  font-style: {style};
  font-stretch: {stretch};
  src: {src};
}}
'''

FONT_FACE_SRC_TEMPLATE = "url('{path}') format('{format}')"

FONT_FORMAT_CSS_MAP = {
    'woff': 'woff',
    'woff2': 'woff2',
    'otf': 'opentype',
    'ttf': 'truetype',
}
