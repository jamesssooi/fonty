'''uninstall.py: Command-line interface to uninstall fonts.'''

import click

@click.argument('name', nargs=-1)
def uninstall(name):
    pass 


