'''fonty.commands.install.py: Command-line interface to install fonts.'''
import os
import re
import timeit
import sys
from urllib.parse import urlparse
from typing import List, Tuple

import click
from termcolor import colored
from fonty.lib import search
from fonty.lib.variants import FontAttribute
from fonty.lib.task import Task, TaskStatus
from fonty.lib.progress import ProgressBar
from fonty.lib.constants import COLOR_INPUT
from fonty.lib.install import install_fonts
from fonty.lib.telemetry import TelemetryEvent, TelemetryEventTypes
from fonty.models.subscription import Subscription
from fonty.models.font import FontFamily, RemoteFont
from fonty.models.manifest import Manifest

@click.command('install', short_help='Install a font')
@click.argument(
    'args',
    nargs=-1,
    metavar='[NAME|FILES|URL]',
    type=click.STRING)
@click.option(
    '--output', '-o',
    type=click.Path(file_okay=False, writable=True, resolve_path=True),
    help='Install the font in this directory.')
@click.option(
    '--variants', '-v',
    multiple=True,
    default=None,
    help='Specify which font variants to install.')
@click.option(
    '--files', '-f', 'is_files',
    type=click.BOOL,
    is_flag=True,
    default=False,
    help='Install from a list of font files.')
@click.pass_context
def cli_install(ctx, args, output, variants, is_files):
    '''Install a font into this computer or a directory.

    \b
    Example usage:
    ==============

    \b
      Install Open Sans into your computer:
      >>> fonty install "Open Sans"

    \b
      Install Open Sans into a directory named "fonts":
      >>> fonty install "Open Sans" --output ./fonts

    \b
      Install only the bold and bold italic variants of Open Sans:
      >>> fonty install "Open Sans" -v 700,700i

    \b
      Install all .ttf files in this directory:
      >>> fonty install --files *.ttf
    '''

    start_time = timeit.default_timer()

    # Process arguments and options
    if variants:
        variants = (','.join(str(x) for x in variants)).split(',')
        variants = [FontAttribute.parse(variant) for variant in variants]

    if not args:
        click.echo(ctx.get_help())
        sys.exit(1)

    # Compare local and remote repository hash
    subscriptions = Subscription.load_entries()
    if not subscriptions:
        Task(
            status=TaskStatus.ERROR,
            message="You are not subscribed to any font sources",
            asynchronous=False
        )
        click.echo("\nEnter '{command}' to add a new font source.".format(
            command=colored('fonty source add <url>', color='cyan')
        ))
        return

    # Find fonts in local files
    font_source = None
    if is_files:
        font_source = 'local_files'
        remote_fonts = [RemoteFont(
            remote_path=RemoteFont.Path(path=path, type=RemoteFont.Path.Type.LOCAL),
            filename=os.path.basename(path),
            family=None,
            variant=None
        ) for path in args]

    # Find fonts in remote sources
    else:
        arg = ' '.join(str(arg) for arg in args)
        try:
            remote_fonts, font_source = resolve_download(arg, print_task=True)
        except search.SearchNotFound:
            # Send telemetry data
            TelemetryEvent(
                status_code=1,
                event_type=TelemetryEventTypes.FONT_INSTALL,
                data={
                    'font_name': arg,
                    'font_source': 'not_resolved',
                    'variants': ', '.join(variants) or None
                }
            ).send()
            sys.exit(1)

    # Filter out variants
    # We will need to filter the variants again after downloading because
    # we might not have the font's variants data at this point.
    if variants:
        remote_fonts = [
            font for font in remote_fonts
            if font.variant is None or font.variant in variants
        ]

    # Load fonts
    task = Task("Resolving ({}) font files...".format(len(remote_fonts)))
    task_printer = create_task_printer(task, remote_fonts)
    local_fonts = [font.load(handler=task_printer) for font in remote_fonts]
    task.complete("Resolved ({}) font file(s)".format(len(local_fonts)))

    # Filter out variants again
    if variants:
        local_fonts = [font for font in local_fonts if font.variant in variants]
        if not local_fonts:
            task = Task(
                message="No font files match your specified variants",
                status=TaskStatus.ERROR,
                asynchronous=False
            )
            sys.exit(1)

    # Install into local computer and update font manifest
    task = Task('Installing ({}) font(s)...'.format(len(local_fonts)))
    installed_fonts = install_fonts(fonts=local_fonts, output_dir=output)
    installed_families = FontFamily.from_font_list(installed_fonts)

    # Update the font manifest
    if not output:
        manifest = Manifest.load()
        for font in installed_fonts:
            manifest.add(font)
        manifest.save()

        # Check for manifest staleness
        if manifest.is_stale():
            task.message = 'Rebuilding font manifest...'
            manifest = Manifest.generate()
            manifest.save()

    # Done!
    message = "Installed '{}'".format(colored(', '.join([f.name for f in installed_families]), COLOR_INPUT))
    if output:
        message += ' to {}'.format(output)
    task.complete(message)

    # Print font family contents
    for family in installed_families:
        family.print(suppress_name=True)

    # Remove temporary files
    for font in remote_fonts:
        font.clear()

    # Calculate execution time
    end_time = timeit.default_timer()
    total_time = round(end_time - start_time, 2)
    click.echo('Done in {}s'.format(total_time))

    # Send telemetry
    TelemetryEvent(
        status_code=0,
        event_type=TelemetryEventTypes.FONT_INSTALL,
        execution_time=total_time,
        data={
            'font_name': arg if not is_files else None,
            'font_source': font_source,
            'variants': ', '.join(variants) or None,
            'output_dir': bool(output)
        }
    ).send()


def create_task_printer(task: Task, remote_fonts: List[RemoteFont]):
    '''Create a download/load handler that prints its progress to as Task instance.'''

    loaded_count = 0

    def load_handler(font: RemoteFont, meta):
        '''Generator function that is advanced when the font downloading/loading progresses.'''

        # Create a total loaded fonts counter. eg. (3/12) fonts downloaded
        nonlocal loaded_count
        loaded_count += 1
        loaded_fonts_str = colored('({count}/{total})'.format(
            count=loaded_count,
            total=len(remote_fonts)
        ), attrs=['dark'])

        # Handle HTTP remotes
        if font.remote_path.type == RemoteFont.Path.Type.HTTP_REMOTE:
            total_size: str = meta.headers.get('Content-Length', None)

            # Create progress bar
            bar = None
            if total_size:
                bar = ProgressBar(
                    total=int(total_size),
                    desc='{count} Downloading {filename}... '.format(
                        count=loaded_fonts_str,
                        filename=font.filename
                    )
                )

            try:
                while True:
                    current_size = yield
                    if bar:
                        bar.update(current_size)
                        task.message = str(bar)
                    else:
                        task.message = '{count} Downloading {filename}... {size}kB'.format(
                            count=loaded_fonts_str,
                            filename=font.filename,
                            size=round(current_size / 1000, 2)
                        )
            except GeneratorExit:
                if bar:
                    bar.update(bar.total)
                    task.message = str(bar)
                else:
                    task.message = '{count} Downloading {filename}... DONE'.format(
                        count=loaded_fonts_str,
                        filename=font.filename
                    )

        # Handle local files
        elif font.remote_path.type == RemoteFont.Path.Type.LOCAL:
            try:
                while True:
                    task.message = '{count} Loading {filename}...'.format(
                        count=loaded_fonts_str,
                        filename=font.filename
                    )
                    yield
            except GeneratorExit:
                task.message = '{count} Loaded {filename}'.format(
                    count=loaded_fonts_str,
                    filename=font.filename
                )

    return load_handler

def resolve_download(arg, print_task: bool = True) -> Tuple[List[RemoteFont], str]:
    '''Resolve if provided argument is a font name or a HTTP download link.'''
    font_source: str = ''

    # Check if argument is a URL path to font
    if re.search(r'^https?:\/\/', arg):
        font_source = 'remote_url'
        fonts = [RemoteFont(
            remote_path=RemoteFont.Path(path=arg, type=RemoteFont.Path.Type.HTTP_REMOTE),
            filename=os.path.basename(urlparse(arg).path),
            family=None,
            variant=None
        )]

    # Argument is a font name to be searched in font sources
    else:
        font_source = 'remote_source'

        # Print task message
        if print_task:
            task = Task("Searching for '{}'...".format(colored(arg, COLOR_INPUT)))

        # Search for font family in local repositories
        try:

            # Search fonts in index
            source, remote_family = search.search(arg)
            fonts = remote_family.fonts

        except search.SearchNotFound as e:

            # Print no results message
            task.error("No results found for '{}'".format(colored(arg, COLOR_INPUT)))
            if e.suggestion:
                click.echo("Did you mean '{}'".format(e.suggestion))

            raise e

        # Complete task message
        if task:
            task.complete("Found '{family}' in {source}".format(
                family=colored(remote_family.name, COLOR_INPUT),
                source=source.name
            ))

    return fonts, font_source
