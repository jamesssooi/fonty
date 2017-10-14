'''fonty.fonty: entry point for fonty'''
import click
from fonty.commands.install import cli_install
from fonty.commands.uninstall import cli_uninstall
from fonty.commands.source import cli_source
from fonty.commands.list import cli_list
from fonty.commands.webfont import cli_webfont

@click.group()
def main():
    '''Fonty 0.1.0'''
    pass

# Register commands
main.add_command(cli_install)
main.add_command(cli_uninstall)
main.add_command(cli_source)
main.add_command(cli_list)
main.add_command(cli_webfont)
