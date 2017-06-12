'''fonty.fonty: entry point for fonty'''
import click
import json
import time
from pprint import pprint
from whoosh.qparser import QueryParser
from fonty.models.typeface import Typeface
from fonty.models.repository import Repository
from fonty.lib import search

@click.group()
def main():
    '''Entry function for fonty'''
    pass

@click.command()
@click.option('--verbose/-v', is_flag=True)
def test(verbose):
    '''Testing function.'''
    with open('./sample/repo.json') as json_string:
        repo = Repository.load_from_json(json_string.read())
        search.index_fonts(repo)

@click.command()
@click.argument('name', nargs=-1, type=click.STRING)
@click.option('--variants', '-v', multiple=True, default=None, type=click.STRING)
def install(name, variants):
    '''Installs a font'''

    # Process arguments and options
    name = ' '.join(str(x) for x in name)
    if variants:
        variants = (','.join(str(x) for x in variants)).split(',')

    # Compare local and remote repository hash
    click.echo('Resolving font sources...')

    # Search for typeface in local repositories
    click.echo("Searching for '{}'...".format(click.style(name, fg='green')))
    try:
        repo, typeface = search.search(name)
    except search.SearchNotFound as e:
        click.echo("\nNo results found for '{}'".format(
            click.style(name, fg='green')
        ))
        if e.suggestion:
            click.echo("Did you mean '{}'?".format(e.suggestion))
        return

    click.echo("Found '{typeface}' in {repo}".format(
        typeface=click.style(typeface.name, fg='green'),
        repo=repo.source
    ))

    # Check if variants exists
    available_variants = [x[0] for x in typeface.get_variations()]
    invalid_variants = []
    for variant in variants:
        if variant not in available_variants:
            invalid_variants.append(variant)
    if invalid_variants:
        if len(invalid_variants) > 1:
            click.echo('Variants {} are not available'.format(
                click.style(', '.join(invalid_variants), fg='green')
            ))
        else:
            click.echo('Variant {} is not available'.format(
                click.style(', '.join(invalid_variants), fg='green')
            ))
        return # TODO: Raise exception
    variants_count = len(variants) if variants else len(available_variants)

    # Download font files
    click.echo('Downloading ({}) font files...'.format(variants_count))

    def download_handler(request):
        total_size = int(request.headers['Content-Length'])
        current_size = 0
        with click.progressbar(length=total_size) as bar:
            while current_size < total_size:
                received_size = yield
                current_size += received_size
                bar.update(current_size)
                yield current_size

    fonts = typeface.download(variants, download_handler)

    # Install into local computer
    click.echo('Installing (6) fonts...')

    # Done!
    click.echo('Done in 2.4s!')

@click.command()
@click.argument('name')
def uninstall(name):
    '''Uninstalls a font'''
    click.echo('Uninstalling font ' + name)


# register commands
main.add_command(install)
main.add_command(uninstall)
main.add_command(test)
