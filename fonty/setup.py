'''fonty.setup: initial setup script for fonty.'''
import os
import json
import shutil

import click
from termcolor import colored
from fonty.lib.constants import APP_DIR, ROOT_DIR, COLOR_INPUT
from fonty.lib.task import Task
from fonty.models.subscription import Subscription, AlreadySubscribedError
from fonty.models.manifest import Manifest
from fonty.lib import search

def initial_setup() -> None:
    '''Perform initial fonty setup.'''

    # Print welcome message
    initial_setup_message = '\n'.join([
        "Looks like this is your first time running fonty! Running initial setup scripts...",
    ])
    click.echo(initial_setup_message)

    # Subscribe to default sources
    generate_default_subscriptions()

    # Generate initial font manifest
    generate_manifest()

    # Generate initial config file
    generate_config()

    # Print new line
    click.echo("")

def generate_manifest() -> None:
    '''Generate a manifest list from the user's installed fonts.'''

    task = Task("Generating initial font manifest...")

    # Generate new manifest
    manifest = Manifest.generate()
    manifest.save()

    # Done!
    task.complete()

def generate_default_subscriptions() -> None:
    '''Subscribe to all default sources.'''

    # Get list of default sources
    path_to_defaults = os.path.join(ROOT_DIR, 'defaults', 'sources.json')
    sources = []
    with open(path_to_defaults, encoding='utf-8') as f:
        sources = json.loads(f.read())

    # Subscribe to each default sources
    for source in sources:
        task = Task(
            "Subscribing to default source '{}'...".format(colored(source['name'], COLOR_INPUT))
        )

        # Subscribe to source
        sub = Subscription.load_from_url(source['url'])
        try:
            sub.subscribe()
        except AlreadySubscribedError:
            sub = sub.get(sub.id_)

        # Index fonts
        repo = sub.get_local_repository()
        search.index_fonts(repo, sub.local_path)

        # Done!
        task.complete()

def generate_config() -> None:
    '''Generate default fonty configuration file.'''
    task = Task("Generating default configuration file...")

    # Copy default configuration file to app directory
    path_to_default = os.path.join(ROOT_DIR, 'defaults', 'fonty.conf')
    dest_path = os.path.join(APP_DIR, 'fonty.conf')
    shutil.copyfile(path_to_default, dest_path)

    # Done!
    task.complete()

def is_first_run() -> bool:
    '''Check if fonty has already been setup on this system.'''
    path_to_config = os.path.join(APP_DIR, 'fonty.conf')
    return not os.path.isfile(path_to_config)
