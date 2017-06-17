'''fonty.fonty: entry point for fonty'''

import io

import click
import json
import time
import timeit
import colorama
from termcolor import colored
from pprint import pprint
from fonty.models.repository import Repository
from fonty.models.subscription import Subscription
from fonty.lib import search
from fonty.lib.progress import ProgressBar
from fonty.lib.constants import COLOR_INPUT
from fonty.lib.task import Task, TaskStatus
from fonty.lib.install import install_fonts

colorama.init()

@click.group()
def main():
    '''Entry function for fonty'''
    pass

@click.command()
@click.option('--verbose/-v', is_flag=True)
def test(verbose):
    '''Testing function.'''
    pass

@click.command()
@click.argument('name', nargs=-1, type=click.STRING)
@click.option('--output', '-o', type=click.Path(file_okay=False, writable=True, resolve_path=True))
@click.option('--variants', '-v', multiple=True, default=None, type=click.STRING)
def install(name, output, variants):
    '''Installs a font'''

    start_time = timeit.default_timer()

    # Process arguments and options
    name = ' '.join(str(x) for x in name)
    if variants:
        variants = (','.join(str(x) for x in variants)).split(',')

    # Compare local and remote repository hash
    #click.echo('Resolving font sources...')

    # Search for typeface in local repositories
    task = Task("Searching for '{}'...".format(colored(name, 'green')))
    try:
        repo, typeface = search.search(name)
    except search.SearchNotFound as e:
        task.stop(status=TaskStatus.ERROR,
                  message="No results found for '{}'".format(colored(name, 'green')))
        if e.suggestion: click.echo("Did you mean '{}'?".format(e.suggestion))
        return
    task.stop(status=TaskStatus.SUCCESS,
              message="Found '{typeface}' in {repo}".format(
                  typeface=colored(typeface.name, COLOR_INPUT),
                  repo=repo.name
              ))

    # Check if variants exists
    available_variants = [x[0] for x in typeface.get_variants()]
    invalid_variants = [variant for variant in variants if variant not in available_variants]
    if invalid_variants:
        task.stop(status=TaskStatus.ERROR,
                  message='Variant(s) [{}] is not available'.format(
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
    install_fonts(fonts, output)

    # Done!
    message = 'Installed {typeface}({variants})'.format(
        typeface=colored(typeface.name, COLOR_INPUT),
        variants=colored(', '.join([font.variant for font in fonts]), 'red')
    )

    if output:
        message += ' to {}'.format(output)

    task.stop(status=TaskStatus.SUCCESS,
              message=message)

    # Calculate execution time
    end_time = timeit.default_timer()
    total_time = end_time - start_time
    click.echo('Done in {}s'.format(round(total_time, 2)))


@click.command()
@click.argument('name')
def uninstall(name):
    '''Uninstalls a font'''
    click.echo('Uninstalling font ' + name)


@click.command()
def update():
    '''Fetch latest repository data and reindex fonts.'''

    click.echo('Fetching latest repository data...')

    subscriptions = Subscription.load_entries()
    for sub in subscriptions:
        task = Task('Updating {}'.format(sub.remote_path))

        # Fetch remote repositories
        sub, has_changes = sub.fetch()
        if not has_changes:
            task.stop(TaskStatus.SUCCESS, 'No updates available for {}'.format(sub.remote_path))
            continue

        # Reindex fonts
        task.message = 'Indexing {}'.format(sub.remote_path)
        search.index_fonts(sub.get_local_repository(), sub.local_path)

        task.stop(TaskStatus.SUCCESS, 'Updated {}'.format(sub.remote_path))


@click.command()
@click.argument('url')
def subscribe(url):
    '''Subscribe to a respository.'''
    task = Task("Adding '{}' to subscription list...".format(colored(url, COLOR_INPUT)))

    # Add to subscription list and fetch remote repository
    sub = Subscription(remote_path=url).subscribe()

    # Index fonts
    task.message = "Indexing '{}'".format(colored(url, COLOR_INPUT))
    repo = sub.get_local_repository()
    search.index_fonts(repo, sub.local_path)

    task.stop(status=TaskStatus.SUCCESS,
              message="Subscribed to '{}'".format(colored(repo.name, COLOR_INPUT)))

    click.echo('{} new typefaces available.'.format(colored(len(repo.typefaces), 'green')))


# register commands
main.add_command(install)
main.add_command(uninstall)
main.add_command(test)
main.add_command(update)
main.add_command(subscribe)
