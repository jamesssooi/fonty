'''fonty.commands.list.py: Command-line interface to list user installed fonts.'''
import sys
import timeit
from functools import reduce
from itertools import zip_longest

import click
from ansiwrap import ansilen
from termcolor import colored
from fonty.models.manifest import Manifest
from fonty.lib import utils
from fonty.lib.terminal_size import get_terminal_size
from fonty.lib.constants import COLOR_INPUT
from fonty.lib.task import Task
from fonty.lib.telemetry import TelemetryEvent, TelemetryEventTypes

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

    start_time = timeit.default_timer()

    # Process arguments
    name = ' '.join(str(x) for x in name)

    # Rebuild manifest.json if --rebuild flag is specified
    if rebuild:
        task = Task('Rebuilding font manifest...')
        manifest = Manifest.generate()
        manifest.save()
        task.complete('Rebuilt font manifest with {count} font families found.'.format(
            count=len(manifest.families)
        ))

        # Calculate execution time
        end_time = timeit.default_timer()
        total_time = round(end_time - start_time, 2)
        click.echo('Done in {}s'.format(total_time))

        # Send telemetry
        TelemetryEvent(
            status_code=0,
            execution_time=total_time,
            event_type=TelemetryEventTypes.FONT_LIST_REBUILD
        ).send()

        sys.exit(0)

    # Check if manifest.json exists
    try:
        manifest = Manifest.load()
    except FileNotFoundError:
        manifest = Manifest.generate()
        manifest.save()

    # Rebuild manifest.json if the manifest is stale
    if manifest.is_stale():
        task = Task('Rebuilding font manifest...')
        manifest = Manifest.generate()
        manifest.save()
        task.complete('Rebuilt font manifest with {count} font families found.'.format(
            count=len(manifest.families)
        ))

    # List all installed fonts if no font family name is specified
    if not name:
        list_all_fonts(manifest)
    else:
        list_font(manifest, name)

    # Calculate execution time
    end_time = timeit.default_timer()
    total_time = round(end_time - start_time, 2)

    # Send telemetry
    TelemetryEvent(
        status_code=0,
        event_type=TelemetryEventTypes.FONT_LIST,
        execution_time=total_time,
        data={'font_name': name}
    ).send()

def list_all_fonts(manifest: Manifest):
    '''List all installed fonts in this system.'''

    # Get font list
    entries = ['{name} {variants}'.format(
        name=family.name,
        variants=colored('({})'.format(len(family.get_variants())), attrs=['dark'])
    ) for family in manifest.families]
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
        longest = [max(col, key=ansilen) for col in cols if len(col) > 0]

        # Calculate the maximum line length of this iteration
        line_length = reduce(lambda x, y: x + ansilen(y) + PADDING, longest, 0)

        # Remove padding from last column
        line_length -= PADDING

        # Check if the line length fits within the terminal size
        if line_length <= term_width:
            break

        col_count -= 1

    # Print list
    col_widths = [len(max(col, key=len)) for col in cols if len(col) > 0]
    for line in zip_longest(*cols):
        line = filter(None, line)
        separator = ' ' * PADDING
        s = separator.join('{name:{width}}'.format(
            name=val,
            width=col_widths[idx]
        ) for idx, val in enumerate(line))
        click.echo(s)

    # Print count
    click.echo('\n{count} font families installed.'.format(count=len(entries)))

def list_font(manifest: Manifest, name: str):
    '''Show details for a particular font family.'''

    family = manifest.get(name)
    if not family:
        click.echo("No results found for '{name}'".format(
            name=colored(name, COLOR_INPUT)
        ))
        sys.exit(1)

    family.print()
