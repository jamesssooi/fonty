'''fonty.commands.webfont.py: Command-line interface to create webfonts.'''
import os
import sys
import glob
import timeit
from typing import List

import click
from termcolor import colored
from fonty.lib.constants import COLOR_INPUT
from fonty.lib.task import Task, TaskStatus
from fonty.lib.progress import ProgressBar
from fonty.lib.telemetry import TelemetryEvent, TelemetryEventTypes
from fonty.models.manifest import Manifest
from fonty.models.font import Font, FontFormat
from fonty.commands.install import resolve_download, create_task_printer

@click.command('webfont', short_help='Generate webfonts')
@click.argument(
    'args',
    nargs=-1,
    required=False,
    metavar='[FILES|NAME]',
    type=click.STRING)
@click.option(
    '--installed', '-i', 'is_installed',
    type=click.BOOL,
    is_flag=True,
    default=False,
    help='Convert an existing installed font.')
@click.option(
    '--download', '-d', 'is_download',
    type=click.BOOL,
    is_flag=True,
    default=False,
    help='Download font from subscribed sources.'
)
@click.option(
    '--output', '-o',
    type=click.Path(file_okay=False, dir_okay=True, writable=True),
    help='Output the converted webfonts in this directory.')
@click.pass_context
def cli_webfont(ctx, args: List[str], is_installed: bool, is_download: bool, output: str):
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
      Output converted webfonts into a specific directory
      >>> fonty webfont *.ttf -o ./webfonts

    \b
      Download and convert from subscribed sources:
      >>> fonty webfont --download "Open Sans"

    \b
      Convert an existing installed font from your system:
      >>> fonty webfont --installed "Open Sans"
    '''

    start_time = timeit.default_timer()

    if len(args) < 1:
        click.echo(ctx.get_help())
        sys.exit(1)

    # Resolve fonts
    if is_download:
        arg = ' '.join(str(s) for s in args)
        remote_fonts, font_source = resolve_download(arg, print_task=True)

        # Download fonts
        task = Task("Downloading ({}) font files...".format(len(remote_fonts)))
        task_printer = create_task_printer(task, remote_fonts)
        fonts = [font.load(handler=task_printer) for font in remote_fonts]
        task.complete("Downloaded ({}) font files".format(len(fonts)))

    elif is_installed:
        arg = ' '.join(str(s) for s in args)
        manifest = Manifest.load()
        family = manifest.get(arg)
        if not family:
            task = Task(
                status=TaskStatus.ERROR,
                message="No font(s) found for '{}'".format(colored(arg, COLOR_INPUT)),
                asynchronous=False
            )
            sys.exit(1)
        fonts = family.fonts
    else:
        # On Unix based systems, a glob argument of *.ttf will be automatically
        # expanded by the shell. Meanwhile on Windows systems or if the pattern
        # is surrounded with quotes, it will be passed to this function as is.
        # Here we iterate through it and run the glob function anyway to be safe
        font_paths = [glob.glob(arg) for arg in args]
        flat_font_paths = [item for sublist in font_paths for item in sublist] # Flatten list
        abs_font_paths = [os.path.abspath(path) for path in flat_font_paths] # Get absolute paths
        if not font_paths:
            task.error("No font files found with the pattern '{}'".format(
                colored(args[0], COLOR_INPUT
            )))
            sys.exit(1)
        fonts = [Font(path_to_font=path) for path in abs_font_paths]

    # Print task message
    task = Task('Generating webfonts for ({}) fonts...'.format(len(fonts)))
    bar = ProgressBar(total=len(fonts) * 2)

    # Convert files to web-compatible formats (woff, woff2 and otf/ttf)
    output_dir = output if output else os.getcwd()
    results: List[dict] = []
    for font in fonts:

        completed_count_str = colored('({count}/{total})'.format(
            count=len(results),
            total=len(fonts)
        ), attrs=['dark'])

        _, ext = os.path.splitext(os.path.basename(font.path_to_font))
        filename = font.generate_filename(ext='')

        # Get family and variant name
        family_name = font.get_family_name()
        variant = font.get_variant()

        # Parse variant
        font_weight = variant.weight.value.css
        font_style = variant.style.value.css
        font_stretch = variant.stretch.value.css

        # Default (TTF/OTF)
        format_default = {'path': font.convert(output_dir), 'format': ext[1:]}

        # Convert to WOFF
        bar.increment()
        task.message = '{count} Converting {filename}.woff... {bar}'.format(
            count=completed_count_str,
            filename=filename,
            bar=bar
        )
        format_woff = {'path': font.convert(output_dir, FontFormat.WOFF), 'format': 'woff'}

        # Convert to WOFF2
        bar.increment()
        task.message = '{count} Converting {filename}.woff2... {bar}'.format(
            count=completed_count_str,
            filename=filename,
            bar=bar
        )
        format_woff2 = {'path': font.convert(output_dir, FontFormat.WOFF2), 'format': 'woff2'}

        results.append({
            'family_name': family_name,
            'font_weight': font_weight,
            'font_style': font_style,
            'font_stretch': font_stretch,
            'formats': [format_woff2, format_woff, format_default]
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
    css_path = os.path.join(output_dir, 'fonty.css')
    with open(file=css_path, mode='w+') as f:
        f.write(META)
        f.write('\n'.join(declarations))

    task.stop(message='Generated @font-face declaration(s) in fonty.css')

    # Print completion message
    family_names = list(set([font.family for font in fonts]))
    task = Task(
        message="Generated webfonts for {families} in {output}".format(
            families=', '.join("'{}'".format(colored(name, COLOR_INPUT)) for name in family_names),
            output=os.path.abspath(output_dir)
        ),
        status=TaskStatus.SUCCESS,
        truncate=False,
        asynchronous=False
    )

    # Remove temporary files
    if 'remote_fonts' in locals():
        for font in remote_fonts:
            font.clear()

    # Calculate execution time
    end_time = timeit.default_timer()
    total_time = round(end_time - start_time, 2)
    click.echo('Done in {}s'.format(total_time))

    # Send telemetry
    TelemetryEvent(
        status_code=0,
        event_type=TelemetryEventTypes.FONT_CONVERT,
        execution_time=total_time,
        data={
            'source': font_source if is_download else 'system' if is_installed else 'local_files',
            'font_name': arg if is_download or is_installed else '',
            'output_dir': bool(output)
        }
    ).send()


# TEMPLATES
# ============================================================================ #
META = '''/*
 * Auto-generated by fonty, a command-line tool for installing, managing
 * and converting fonts.
 */

'''

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
