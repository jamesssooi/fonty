'''fonty.commands.uninstall.py: Command-line interface to uninstall fonts.'''
import sys
import timeit

import click
from termcolor import colored
from fonty.lib.task import Task
from fonty.lib.variants import FontAttribute
from fonty.lib.constants import COLOR_INPUT
from fonty.lib.uninstall import uninstall_fonts
from fonty.lib.telemetry import TelemetryEvent, TelemetryEventTypes
from fonty.models.manifest import Manifest
from fonty.models.font import FontFamily

@click.command('uninstall', short_help='Uninstall a font')
@click.argument(
    'name',
    nargs=-1,
    type=click.STRING)
@click.option(
    '--variants', '-v',
    multiple=True,
    default=None,
    help='Specify which font variants to uninstall.')
@click.pass_context
def cli_uninstall(ctx, name, variants):
    '''Uninstall a font from this computer.

    \b
    Example usage:
    ==============

    \b
      Uninstall Open Sans from your computer:
      >>> fonty uninstall "Open Sans"

    \b
      Uninstall only the bold and bold italic variants of Open Sans:
      >>> fonty uninstall "Open Sans" -v 700,700i

    '''

    start_time = timeit.default_timer()

    # Process arguments and options
    name = ' '.join(str(x) for x in name)
    if variants:
        variants = (','.join(str(x) for x in variants)).split(',')
        variants = [FontAttribute.parse(variant) for variant in variants]

    if not name:
        click.echo(ctx.get_help())
        sys.exit(1)

    # Get manifest list
    try:
        manifest = Manifest.load()
    except FileNotFoundError:
        task = Task("Generating font manifest...")
        manifest = Manifest.generate()
        manifest.save()
        task = task.complete('Generated font manifest file')

    # Get font family from system
    task = Task("Searching for {}".format(colored(name, COLOR_INPUT)))
    family = manifest.get(name)
    if family is None:
        task.error("No font family found with the name '{}'".format(colored(name, COLOR_INPUT)))

        # Send telemetry
        TelemetryEvent(
            status_code=1,
            event_type=TelemetryEventTypes.FONT_UNINSTALL,
            data={'font_name': name}
        ).send()

        sys.exit(1)

    # Check if variants exists
    if variants:
        invalid_variants = [x for x in variants if x not in family.variants]
        if invalid_variants:
            task.error("Variant(s) [{}] not available".format(
                colored(', '.join([str(v) for v in invalid_variants]), COLOR_INPUT)
            ))

            # Send telemetry
            TelemetryEvent(
                status_code=1,
                event_type=TelemetryEventTypes.FONT_UNINSTALL,
                data={'font_name': name}
            ).send()

            sys.exit(1)

    if not variants:
        variants = family.variants

    # Uninstall this font family
    local_fonts = family.get_fonts(variants)
    task.message = "Uninstalling {name} ({variants})".format(
        name=colored(family.name, COLOR_INPUT),
        variants=colored(', '.join([str(v) for v in variants]), 'green')
    )
    uninstalled_fonts = uninstall_fonts(local_fonts)
    uninstalled_families = FontFamily.from_font_list(uninstalled_fonts)

    # Update the font manifest
    manifest = Manifest.load()
    for font in uninstalled_fonts:
        manifest.remove(font)
        manifest.save()

    # Check for manifest staleness
    if manifest.is_stale():
        task.message = 'Rebuilding font manifest...'
        manifest = Manifest.generate()
        manifest.save()

    # Print success message
    message = "Uninstalled {}".format(
        ', '.join([
            '{family}({variant})'.format(
                family=colored(family.name, COLOR_INPUT),
                variant=colored(', '.join([str(v) for v in family.variants]), 'green')
            ) for family in uninstalled_families
        ])
    )
    task.complete(message)

    # Calculate execution time
    end_time = timeit.default_timer()
    total_time = round(end_time - start_time, 2)
    click.echo('Done in {}s'.format(total_time))

    # Send telemetry
    TelemetryEvent(
        status_code=0,
        event_type=TelemetryEventTypes.FONT_UNINSTALL,
        execution_time=total_time,
        data={'font_name': name}
    ).send()
