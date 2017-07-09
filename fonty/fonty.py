'''fonty.fonty: entry point for fonty'''
import click
import colorama
from fonty.commands.install import cli_install
from fonty.commands.uninstall import cli_uninstall
from fonty.commands.source import cli_source
from fonty.commands.list import cli_list

colorama.init()

@click.group()
def main():
    '''Entry function for fonty'''
    pass

@click.command()
@click.argument('variant', nargs=-1)
def test(variant):
    '''Testing command'''
    from fonty.models.manifest import Manifest
    manifest = Manifest.load('/Users/jamesooi/Desktop/manifest.json')
    typeface = manifest.get('Abel')
    print(typeface.uninstall())

# Register commands
main.add_command(cli_install)
main.add_command(cli_uninstall)
main.add_command(cli_source)
main.add_command(cli_list)
main.add_command(test)
