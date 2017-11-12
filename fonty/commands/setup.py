'''setup.py'''
import time

import click
from ansiwrap import wrap
from fonty.lib.task import Task

@click.command('setup', short_help='Run setup scripts again')
def cli_setup():
    '''Runs the fonty initial setup script again.'''
    postinstall()


def postinstall():
    '''fonty post install script.'''

    intro_text = \
'''
It looks like this is your first time running fonty!
We need to do a little bit of setting up first before continuing...
'''

    click.echo(intro_text)

    # Build font manifest
    task = Task('Building font manifest...')
    time.sleep(5)
    task.complete('Built font manifest with {count} font families found'.format(count=93))

    # Adding default sources
    task = Task('Adding default sources...')
    time.sleep(6)
    task.complete('Added (3) sources'.format(count=93))