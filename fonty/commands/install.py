'''fonty.commands.install.py: Command-line interface to install fonts.'''
import timeit
import sys

import click
from termcolor import colored
from fonty.lib import search
from fonty.lib.task import Task, TaskStatus
from fonty.lib.progress import ProgressBar
from fonty.lib.constants import COLOR_INPUT
from fonty.models.subscription import Subscription
from fonty.models.typeface import Typeface

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
@click.pass_context
def cli_install(ctx, name, output, variants):
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
    name = ' '.join(str(x) for x in name)
    if variants:
        variants = (','.join(str(x) for x in variants)).split(',')

    if not name:
        click.echo(ctx.get_help())
        sys.exit(1)

    # Compare local and remote repository hash
    subscriptions = Subscription.load_entries()
    if not subscriptions:
        Task(message="You are not subscribed to any font sources.",
             status=TaskStatus.ERROR,
             asynchronous=False)
        click.echo("\nEnter '{command}' to add a new font source.".format(
            command=colored('fonty source add <url>', color='cyan')
        ))
        return

    # Search for typeface in local repositories
    task = Task("Searching for '{}'...".format(colored(name, 'green')))
    try:
        repo, typeface = search.search(name)
    except search.SearchNotFound as e:
        task.stop(status=TaskStatus.ERROR,
                  message="No results found for '{}'".format(colored(name, 'green')))
        if e.suggestion:
            click.echo("Did you mean '{}'?".format(e.suggestion))
        sys.exit(1)

    task.stop(status=TaskStatus.SUCCESS,
              message="Found '{typeface}' in {repo}".format(
                  typeface=colored(typeface.name, COLOR_INPUT),
                  repo=repo.name
              ))

    # Check if variants exists
    available_variants = [str(variant) for variant in typeface.get_variants()]
    invalid_variants = [x for x in variants if x not in available_variants]
    if invalid_variants:
        task.stop(status=TaskStatus.ERROR,
                  message='Variant(s) [{}] not available'.format(
                      colored(', '.join(invalid_variants), COLOR_INPUT)
                  ))
        sys.exit(1)
        return # TODO: Raise exception
    variants_count = len(variants) if variants else len(available_variants)

    # Download font files
    task = Task("Downloading ({}) font files...".format(variants_count))
    fonts = typeface.download(variants, create_download_task_handler(task))
    task.stop(status=TaskStatus.SUCCESS,
              message="Downloaded ({}) font file(s)".format(len(fonts)))

    # Install into local computer
    task = Task('Installing ({}) fonts...'.format(len(fonts)))
    installed_typeface: Typeface = typeface.install(variants=variants, path=output)

    # Done!
    message = 'Installed {}'.format(colored(typeface.name, COLOR_INPUT))
    if output:
        message += ' to {}'.format(output)
    task.stop(status=TaskStatus.SUCCESS, message=message)

    # Print typeface contents
    installed_typeface.print(suppress_name=True)

    # Calculate execution time
    end_time = timeit.default_timer()
    total_time = end_time - start_time
    click.echo('Done in {}s'.format(round(total_time, 2)))


def create_download_task_handler(task):
    '''Create a download handler that prints a progress bar to a Task instance.'''

    def download_handler(font, request):
        '''A generator function that is yielded for every byte packet received.'''
        total_size = int(request.headers['Content-Length'])
        current_size = 0
        bar = ProgressBar(total=total_size,
                          desc='Downloading {}'.format(font.filename))
        while True:
            current_size = yield
            bar.update(current_size)
            task.message = str(bar)
            yield current_size

    return download_handler
