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

# Register commands
main.add_command(cli_install)
main.add_command(cli_source)
