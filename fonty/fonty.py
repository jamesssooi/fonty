'''fonty.fonty: entry point for fonty'''

import io

import click
import json
import time
import timeit
import colorama
from termcolor import colored
from pprint import pprint
from fonty.models.repository import Repository
from fonty.models.subscription import Subscription
from fonty.lib import search
from fonty.lib.progress import ProgressBar
from fonty.lib.constants import COLOR_INPUT
from fonty.lib.task import Task, TaskStatus
from fonty.commands.install import cli_install
from fonty.commands.source import cli_source

colorama.init()

@click.group()
def main():
    '''Entry function for fonty'''
    print('')
    pass

@click.command()
@click.option('--verbose/-v', is_flag=True)
def test(verbose):
    '''Testing function.'''
    pass

@click.command()
def update():
    '''Fetch latest repository data and reindex fonts.'''

    click.echo('Fetching latest repository data...')

    subscriptions = Subscription.load_entries()
    for sub in subscriptions:
        task = Task('Updating {}'.format(sub.remote_path))

        # Fetch remote repositories
        sub, has_changes = sub.fetch()
        if not has_changes:
            task.stop(TaskStatus.SUCCESS, 'No updates available for {}'.format(sub.remote_path))
            continue

        # Reindex fonts
        task.message = 'Indexing {}'.format(sub.remote_path)
        search.index_fonts(sub.get_local_repository(), sub.local_path)

        task.stop(TaskStatus.SUCCESS, 'Updated {}'.format(sub.remote_path))


# register commands
main.add_command(cli_install)
main.add_command(cli_source)
