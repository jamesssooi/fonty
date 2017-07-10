'''fonty.commands.list.py: Command-line interface to list user installed fonts.'''

import click
from fonty.models.manifest import Manifest

@click.command('list')
@click.option('--update', '-u', is_flag=True)
def cli_list(update: bool):
    '''List all user installed fonts'''

    # Check if manifest.json exists
    manifest = Manifest.generate()
    manifest.save()

    # Read manifest.json

    # Print

    pass