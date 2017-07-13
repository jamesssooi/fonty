'''fonty.commands.list.py: Command-line interface to list user installed fonts.'''

import click
from fonty.models.manifest import Manifest

@click.command('list')
@click.option('--update', '-u', is_flag=True)
def cli_list(update: bool):
    '''List all user installed fonts'''

    # Check if manifest.json exists
    try:
        manifest = Manifest.load()
    except FileNotFoundError:
        manifest = Manifest.generate()
        manifest.save()

    # Get font list
    entries = []
    for typeface in manifest.typefaces:
        entries.append('{name} ({variants})'.format(
            name=typeface.name,
            variants=len(typeface.get_variants()))
        )
    entries.sort()

    col1 = entries[0:len(entries)//2]
    col2 = entries[len(entries)//2 + 1:]

    for c1, c2 in zip(col1, col2):
        print("{:40} {}".format(c1, c2))
