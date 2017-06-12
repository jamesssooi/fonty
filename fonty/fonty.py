'''fonty.fonty: entry point for fonty'''

import io
import sys
import click
import json
import time
import timeit
from tqdm import tqdm
from termcolor import colored
from pprint import pprint
from whoosh.qparser import QueryParser
from fonty.models.typeface import Typeface
from fonty.models.repository import Repository
from fonty.lib import search
from fonty.lib.progress import Action, ProgressBar
from fonty.lib.constants import COLOR_INPUT, ACTION_OK, ACTION_ERR

@click.group()
def main():
    '''Entry function for fonty'''
    pass

@click.command()
@click.option('--verbose/-v', is_flag=True)
def test(verbose):
    '''Testing function.'''
    bar = ProgressBar(1024)
    for _ in range(1024):
        bar.increment(2)
        print(bar, end='\r')
        time.sleep(0.01)

    # p = Progress('foo')
    # time.sleep(3)
    # p.stop('✓', 'done!')

    # repositories = Repository.load_all()
    # for repo in repositories:
    #     search.index_fonts(repo)

@click.command()
@click.argument('name', nargs=-1, type=click.STRING)
@click.option('--variants', '-v', multiple=True, default=None, type=click.STRING)
def install(name, variants):
    '''Installs a font'''

    start_time = timeit.default_timer()

    # Process arguments and options
    name = ' '.join(str(x) for x in name)
    if variants:
        variants = (','.join(str(x) for x in variants)).split(',')

    # Compare local and remote repository hash
    #click.echo('Resolving font sources...')

    # Search for typeface in local repositories
    action = Action("Searching for '{}'...".format(colored(name, 'green')))
    try:
        repo, typeface = search.search(name)
    except search.SearchNotFound as e:
        click.echo("\nNo results found for '{}'".format(
            click.style(name, fg='green')
        ))
        if e.suggestion:
            click.echo("Did you mean '{}'?".format(e.suggestion))
        return
    action.stop(status=ACTION_OK,
                message="Found '{typeface}' in {repo}".format(
                    typeface=colored(typeface.name, COLOR_INPUT),
                    repo=repo.source
                ))

    # Check if variants exists
    available_variants = [x[0] for x in typeface.get_variants()]
    invalid_variants = [variant for variant in variants if variant not in available_variants]
    # for variant in variants:
    #     if variant not in available_variants:
    #         invalid_variants.append(variant)
    if invalid_variants:
        action.stop(status=ACTION_ERR,
                    message='Variant(s) [{}] is not available'.format(
                        colored(', '.join(invalid_variants), COLOR_INPUT)
                    ))
        return # TODO: Raise exception
    variants_count = len(variants) if variants else len(available_variants)

    # Download font files
    action = Action("Downloading ({}) font files...".format(variants_count))

    def download_handler(font, request):
        total_size = int(request.headers['Content-Length'])
        current_size = 0
        bar = ProgressBar(total=total_size,
                          desc='Downloading {}'.format(font.filename))
        while current_size < total_size:
            current_size = yield
            bar.update(current_size)
            action.message = str(bar)
            yield current_size

    fonts = typeface.download(variants, download_handler)
    action.stop(status=ACTION_OK,
                message="Downloaded ({}) font file(s)".format(len(fonts)))

    # Install into local computer
    action = Action('Installing ({}) fonts...'.format(len(fonts)))
    for font in fonts:
        font.install()
    
    # Done!
    end_time = timeit.default_timer()
    total_time = end_time - start_time
    action.stop(status=ACTION_OK,
                message='Installed {typeface}({variants})'.format(
                    typeface=colored(typeface.name, COLOR_INPUT),
                    variants=click.style(', '.join([font.variant for font in fonts]), dim=True),
                    time=round(total_time, 2)
                ))
    
    click.echo('Done in {}s'.format(round(total_time, 2)))

@click.command()
@click.argument('name')
def uninstall(name):
    '''Uninstalls a font'''
    click.echo('Uninstalling font ' + name)


# register commands
main.add_command(install)
main.add_command(uninstall)
main.add_command(test)
