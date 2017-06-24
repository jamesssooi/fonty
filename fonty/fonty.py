'''fonty.fonty: entry point for fonty'''
import click
import colorama
from fonty.commands.install import cli_install
from fonty.commands.source import cli_source

colorama.init()

@click.group()
def main():
    '''Entry function for fonty'''
    pass

@click.command()
def test():
    '''Testing command'''
    from fonty.lib.list_fonts import get_font_list
    get_font_list()

# Register commands
main.add_command(cli_install)
main.add_command(cli_source)
main.add_command(test)
