'''fonty.commands.uninstall.py: Command-line interface to uninstall fonts.'''
import time
import sys

import click
from termcolor import colored
from fonty.lib.task import Task, TaskStatus
from fonty.lib.constants import COLOR_INPUT
from fonty.models.manifest import Manifest

@click.command('uninstall')
@click.argument('name', nargs=-1, type=click.STRING)
@click.option('--variants', '-v', multiple=True, default=None, type=click.STRING)
def cli_uninstall(name, variants):
    '''Uninstall a typeface'''

    # Process arguments and options
    name = ' '.join(str(x) for x in name)
    if variants:
        variants = (','.join(str(x) for x in variants)).split(',')

    # Get manifest list
    try:
        manifest = Manifest.load()
    except FileNotFoundError:
        task = Task("Generating font manifest...")
        manifest = Manifest.generate()
        manifest.save()
        task = task.stop(message='Generated font manifest file')

    # Get typeface from system
    task = Task("Searching for {}".format(colored(name, COLOR_INPUT)))
    typeface = manifest.get(name)
    if typeface is None:
        task.stop(status=TaskStatus.ERROR,
                  message="No typeface found with the name '{}'".format(
                      colored(name, COLOR_INPUT)
                  ))
        sys.exit(1)

    # Check if variants exists
    available_variants = [str(variant) for variant in typeface.get_variants()]
    invalid_variants = [x for x in variants if x not in available_variants]
    if invalid_variants:
        task.stop(status=TaskStatus.ERROR,
                  message="Variant(s) [{}] not available".format(
                      colored(', '.join(invalid_variants), COLOR_INPUT)
                  ))
        sys.exit(1)
    if not variants:
        variants = available_variants

    # Uninstall this typeface
    task.message = "Uninstalling {name} ({variants})".format(
        name=colored(typeface.name, COLOR_INPUT),
        variants=colored(', '.join(variants), 'green')
    )
    success, failed = typeface.uninstall(variants)
    uninstalled_variants = [str(font.variant) for font in success]

    if success and failed:
        task.stop(status=TaskStatus.WARNING,
                  message="Uninstalled {name}({variants}) with errors".format(
                      name=colored(typeface.name, COLOR_INPUT),
                      variants=colored(', '.join(uninstalled_variants), 'green')
                  ))
        click.echo("\nUnable to find the following font files:\n{errors}".format(
            errors='\n'.join('- ' + font.local_path for font in failed)
        ))
        click.echo("\nRebuild your manifest file by running '{command}' to fix this.".format(
            command=colored('fonty list -f', 'cyan')
        ))
    elif success:
        task.stop(status=TaskStatus.SUCCESS,
                  message="Uninstalled {name}({variants})".format(
                      name=colored(typeface.name, COLOR_INPUT),
                      variants=colored(', '.join(variants), 'green')
                  ))
    elif failed:
        task.stop(status=TaskStatus.ERROR,
                  message="Failed to uninstall {name}({variants})".format(
                      name=colored(typeface.name, COLOR_INPUT),
                      variants=colored(', '.join(variants), 'green')
                  ))
        click.echo("\nUnable to find the following font files:\n{errors}".format(
            errors='\n'.join('- ' + font.local_path for font in failed)
        ))
        click.echo("\nRebuild your manifest file by running '{command}' to fix this.".format(
            command=colored('fonty list -f', 'cyan')
        ))
