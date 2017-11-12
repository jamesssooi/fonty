'''fonty.commands.install.py: Command-line interface to install fonts.'''
import os
import re
import timeit
import sys
from urllib.parse import urlparse
from typing import List

import click
from termcolor import colored
from fonty.lib import search
from fonty.lib.variants import FontAttribute
from fonty.lib.task import Task, TaskStatus
from fonty.lib.progress import ProgressBar
from fonty.lib.constants import COLOR_INPUT
from fonty.lib.install import install_fonts
from fonty.models.subscription import Subscription
from fonty.models.font import FontFamily, RemoteFont
from fonty.models.manifest import Manifest

@click.command('install', short_help='Install a font')
@click.argument(
    'name',
    nargs=-1,
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
    default=False
)
@click.pass_context
def cli_install(ctx, name, output, variants, is_files):
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
    '''

    start_time = timeit.default_timer()

    # Process arguments and options
    # name = ' '.join(str(x) for x in name)
    if variants:
        variants = (','.join(str(x) for x in variants)).split(',')
        variants = [FontAttribute.parse(variant) for variant in variants]

    if not name:
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

    # Resolve fonts
    remote_fonts = resolve_fonts(args=name, is_files=is_files, print_task=True)
    task = Task("Resolving ({}) font files...".format(len(remote_fonts)))
    task_printer = create_task_printer(task, remote_fonts)
    local_fonts = [font.load(handler=task_printer) for font in remote_fonts]
    task.complete("Resolved ({}) font file(s)".format(len(local_fonts)))

    # Install into local computer and update font manifest
    task = Task('Installing ({}) fonts...'.format(len(local_fonts)))
    installed_fonts = install_fonts(fonts=local_fonts, output_dir=output)
    installed_families = FontFamily.from_font_list(installed_fonts)

    if not output:
        manifest = Manifest.load()
        for font in installed_fonts:
            manifest.add(font)
        manifest.save()

    # Done!
    message = "Installed '{}'".format(colored(', '.join([f.name for f in installed_families]), COLOR_INPUT))
    if output:
        message += ' to {}'.format(output)
    task.complete(message)

    # Print font family contents
    for family in installed_families:
        family.print(suppress_name=True)

    # Calculate execution time
    end_time = timeit.default_timer()
    total_time = end_time - start_time
    click.echo('Done in {}s'.format(round(total_time, 2)))


def create_task_printer(task: Task, remote_fonts: List[RemoteFont]):
    '''Create a download/load handler that prints its progress to as Task instance.'''

    loaded_count = 0

    def load_handler(font: RemoteFont, meta: any):
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

def resolve_fonts(
        args: List[str],
        is_files: bool,
        print_task: bool = True
    ) -> List[RemoteFont]:
    '''Resolve provided arguments into a list of RemoteFonts.'''
    fonts = []

    if is_files:
        fonts.extend([RemoteFont(
            remote_path=RemoteFont.Path(path=path, type=RemoteFont.Path.Type.LOCAL),
            filename=os.path.basename(path),
            family=None,
            variant=None
        ) for path in args])
    else:
        arg = ' '.join(str(arg) for arg in args)

        # Argument is a URL path to font
        if re.search(r'^https?:\/\/', arg):
            filename = os.path.basename(urlparse(arg).path)
            fonts.append(RemoteFont(
                remote_path=RemoteFont.Path(path=arg, type=RemoteFont.Path.Type.HTTP_REMOTE),
                filename=filename,
                family=None,
                variant=None
            ))

        # Argument is a font name to be searched in font sources
        else:
            if print_task:
                task = Task("Searching for '{}'...".format(colored(arg, 'green')))

            # Search for font family in local repositories
            try:
                source, remote_family = search.search(arg)
                fonts = remote_family.fonts
            except search.SearchNotFound as e:
                task.error("No results found for '{}'".format(colored(arg, 'green')))
                if e.suggestion:
                    click.echo("Did you mean '{}'".format(e.suggestion))
                sys.exit(1)

            if task:
                task.complete("Found '{family}' in {source}".format(
                    family=colored(remote_family.name, COLOR_INPUT),
                    source=source.name
                ))

    return fonts
