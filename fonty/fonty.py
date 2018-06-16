'''fonty.fonty: entry point for fonty'''
import os
import sys
import inspect
import click
import colorama

from termcolor import colored

from fonty.version import __version__
from fonty.setup import initial_setup, is_first_run
from fonty.lib import version_checker
from fonty.lib.config import load_config, CommonConfiguration
from fonty.lib.meta_store import MetaStore

# Import CLI commands
from fonty.commands.install import cli_install
from fonty.commands.uninstall import cli_uninstall
from fonty.commands.source import cli_source
from fonty.commands.list import cli_list
from fonty.commands.webfont import cli_webfont

# Enable colored output on Windows
colorama.init()

# def foo(*args, **kwargs):
#     print('foo')

@click.group(invoke_without_command=True)
@click.option('--version', '-v', is_flag=True, help="Show the version number.")
@click.pass_context
def main(ctx, version: bool):
    '''fonty is a simple command line tool for installing, managing and
    converting fonts.

    \b
    Basic usage:
    ============

    \b
      Install Open Sans into your computer:
      >>> fonty install "Open Sans"

    \b
      Uninstall Open Sans from your computer:
      >>> fonty uninstall "Open Sans"

    \b
      Download and convert Open Sans to webfonts:
      >>> fonty webfont --download "Open Sans"
    '''

    # Perform initial setup scripts if this is fonty's first run
    if is_first_run():
        initial_setup()

    # Load configuration values
    load_config()

    # Check for updates
    if CommonConfiguration.check_for_updates:
        version_checker.cache_latest_version()

    # Ignore the rest of this function if there is an invoked subcommand
    if ctx.invoked_subcommand:
        return

    # Print fonty's version number and file path if the --version flag is true
    if version:
        click.echo('fonty v{version}\n{path}'.format(
            version=__version__,
            path=os.path.abspath(inspect.stack()[0][1])
        ))
        sys.exit(0)

    # Default behaviour: Print help text
    click.echo(ctx.get_help())


# Register commands
main.add_command(cli_install)
main.add_command(cli_uninstall)
main.add_command(cli_source)
main.add_command(cli_list)
main.add_command(cli_webfont)

# Register callbacks
@main.resultcallback()
@click.pass_context
def after_command(ctx, *args, **kwargs):
    '''A callback that is called after the command has finished executing.'''

    # Notify user for updates
    if CommonConfiguration.check_for_updates and ctx.invoked_subcommand and version_checker.has_new_version():
        click.echo('')
        click.echo("A new fonty version is available. You have '{current}', the latest is '{latest}'.".format(
            current=colored(__version__, 'yellow'),
            latest=colored(MetaStore.latest_version, 'yellow'),
        ))
        click.echo("Run '{}' to upgrade.".format(colored('pip install --upgrade fonty', 'cyan')))
        click.echo('')
