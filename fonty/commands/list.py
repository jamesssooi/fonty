'''fonty.commands.list.py: Command-line interface to list user installed fonts.'''
import sys
from functools import reduce
from itertools import zip_longest

import click
from ansiwrap import ansilen
from termcolor import colored
from fonty.models.manifest import Manifest
from fonty.lib import utils
from fonty.lib.terminal_size import get_terminal_size
from fonty.lib.constants import COLOR_INPUT

@click.command('list', short_help='List installed fonts')
@click.argument(
    'name',
    nargs=-1,
    required=False,
    type=click.STRING)
@click.option(
    '--rebuild',
    is_flag=True,
    help='Rebuild font list.')
def cli_list(name: str, rebuild: bool):
    '''Print a list of all user-installed fonts.

    \b
    Example usage:
    ==============

    \b
      Basic usage:
      >>> fonty list

    \b
      Show more details on a particular font:
      >>> fonty list "Open Sans"
    '''

    # Process arguments
    name = ' '.join(str(x) for x in name)

    # Rebuild manifest.json if --rebuild flag is specified
    if rebuild:
        manifest = Manifest.generate()
        manifest.save()
        click.echo('Manifest rebuilded with {count} typefaces found.'.format(
            count=len(manifest.typefaces)
        ))
        sys.exit(0)

    # Check if manifest.json exists
    try:
        manifest = Manifest.load()
    except FileNotFoundError:
        manifest = Manifest.generate()
        manifest.save()

    # List all installed fonts if no typeface name is specified
    if not name:
        list_all_fonts(manifest)
    else:
        list_font(manifest, name)

def list_all_fonts(manifest: Manifest):
    '''List all installed fonts in this system.'''

    # Get font list
    entries = ['{name} {variants}'.format(
        name=typeface.name,
        variants=colored('({})'.format(len(typeface.get_variants())), attrs=['dark'])
    ) for typeface in manifest.typefaces]
    entries.sort()

    # Find the optimal column count. How it works:
    # Start by generating the maximum number of possible columns, n. Then
    # calculate the maximum line length when the column count is n. Check if
    # the maximum line length fits within the terminal width. If not, repeat
    # with n - 1 until the maximum line length fits.
    # TODO: There's probably a more efficient algorithm to do this
    MAX_COLS = 5  # Hardcoded maximum number of columns
    PADDING = 10 # Spacing between columns
    term_width, _ = get_terminal_size()
    col_count = MAX_COLS
    cols = None
    while col_count > 0:
        # Split list into n number of columns
        cols = utils.split_list(entries, col_count)

        # Get the longest word for each column
        longest = [max(col, key=ansilen) for col in cols]

        # Calculate the maximum line length of this iteration
        line_length = reduce(lambda x, y: x + ansilen(y) + PADDING, longest, 0)

        # Remove padding from last column
        line_length -= PADDING

        # Check if the line length fits within the terminal size
        if line_length <= term_width:
            break

        col_count -= 1

    # Print list
    col_widths = [len(max(col, key=len)) for col in cols]
    for line in zip_longest(*cols):
        line = filter(None, line)
        separator = ' ' * PADDING
        s = separator.join('{name:{width}}'.format(
            name=val,
            width=col_widths[idx]
        ) for idx, val in enumerate(line))
        click.echo(s)

    # Print count
    click.echo('\n{count} typefaces installed.'.format(count=len(entries)))

def list_font(manifest: Manifest, name: str):
    '''Show details for a particular typeface family.'''

    typeface = manifest.get(name)
    if not typeface:
        click.echo("No results found for '{name}'".format(
            name=colored(name, COLOR_INPUT)
        ))
        sys.exit(1)

    typeface.print()
