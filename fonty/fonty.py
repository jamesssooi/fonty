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
    '''Fonty 0.1.0'''
    pass

@click.command()
def test():
    '''Testing command'''
    # from fonty.models.manifest import Manifest
    # manifest = Manifest.load('/Users/jamesooi/Desktop/manifest.json')
    # typeface = manifest.get('Abel')
    # print(typeface.uninstall())
    # from fonty.lib import utils
    # data = [{'name': 'James Ooi', 'age': 23},
    #         {'name': 'Louise Ng', 'age': 19}]

    # print(utils.tabularize(data))

    from fonty.lib.disable import disable_fonts

    disable_fonts(['123'])

# Register commands
main.add_command(cli_install)
main.add_command(cli_uninstall)
main.add_command(cli_source)
main.add_command(cli_list)
