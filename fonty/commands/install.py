'''fonty.commands.install.py: Command-line interface to install fonts.'''
import timeit

import click
from termcolor import colored
from fonty.lib import search
from fonty.lib.task import Task, TaskStatus
from fonty.lib.progress import ProgressBar
from fonty.lib.install import install_fonts
from fonty.lib.constants import COLOR_INPUT
from fonty.models.subscription import Subscription

@click.command('install')
@click.argument('name', nargs=-1, type=click.STRING)
@click.option('--output', '-o', type=click.Path(file_okay=False, writable=True, resolve_path=True))
@click.option('--variants', '-v', multiple=True, default=None, type=click.STRING)
def cli_install(name, output, variants):
    '''Installs a font'''

    start_time = timeit.default_timer()

    # Process arguments and options
    name = ' '.join(str(x) for x in name)
    if variants:
        variants = (','.join(str(x) for x in variants)).split(',')

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
        return
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
        return # TODO: Raise exception
    variants_count = len(variants) if variants else len(available_variants)

    # Download font files
    task = Task("Downloading ({}) font files...".format(variants_count))

    def download_handler(font, request):
        total_size = int(request.headers['Content-Length'])
        current_size = 0
        bar = ProgressBar(total=total_size,
                          desc='Downloading {}'.format(font.filename))
        while True:
            current_size = yield
            bar.update(current_size)
            task.message = str(bar)
            yield current_size

    fonts = typeface.download(variants, download_handler)
    task.stop(status=TaskStatus.SUCCESS,
              message="Downloaded ({}) font file(s)".format(len(fonts)))

    # Install into local computer
    task = Task('Installing ({}) fonts...'.format(len(fonts)))
    typeface.install(variants=variants, path=output)

    # Done!
    message = 'Installed {typeface}({variants})'.format(
        typeface=colored(typeface.name, COLOR_INPUT),
        variants=colored(', '.join([str(font.variant) for font in fonts]), 'red')
    )

    if output:
        message += ' to {}'.format(output)

    task.stop(status=TaskStatus.SUCCESS,
              message=message)

    # Calculate execution time
    end_time = timeit.default_timer()
    total_time = end_time - start_time
    click.echo('Done in {}s'.format(round(total_time, 2)))
