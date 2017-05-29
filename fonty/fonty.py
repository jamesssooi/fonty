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
    # with open('./fonty/sample/lato.json') as json_string:
    #     typeface = Typeface.load_from_json(json_string.read())
    #     click.echo(typeface.to_pretty_string(verbose))

@click.command()
@click.argument('name')
def install(name):
    '''Installs a font'''

    # Compare local and remote repository hash
    click.echo('Resolving font sources...')
    #time.sleep(1.4)

    # Search for typeface
    click.echo('Searching for {}...'.format(name))
    result = search.search(name)
    click.echo(result)

    # Download font files
    click.echo('Downloading (6) font files...')
    #time.sleep(3)

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
