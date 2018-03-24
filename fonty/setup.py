'''fonty.setup: initial setup script for fonty.'''
import os
import json

from termcolor import colored
from fonty.lib.constants import ROOT_DIR, COLOR_INPUT
from fonty.lib.task import Task
from fonty.models.subscription import Subscription, AlreadySubscribedError
from fonty.lib import search

def setup():

    # Subscribe to default sources
    generate_default_subscriptions()

def generate_config_file():
    pass

def generate_manifest():
    pass

def generate_default_subscriptions():

    # Get list of default sources
    path_to_defaults = os.path.join(ROOT_DIR, 'defaults', 'sources.json')
    sources = []
    with open(path_to_defaults, encoding='utf-8') as f:
        sources = json.loads(f.read())

    # Subscribe to each default sources
    for source in sources:
        task = Task("Loading '{}'...".format(colored(source['name'], COLOR_INPUT)))

        # Subscribe to source
        sub = Subscription.load_from_url(source['url'])
        try:
            sub.subscribe()
        except AlreadySubscribedError as e:
            sub = sub.get(sub.id_)

        # Index fonts
        repo = sub.get_local_repository()
        task.message = "Indexing {count} font families in '{repo}'".format(
            count=len(repo.families),
            repo=colored(repo.name, COLOR_INPUT)
        )
        search.index_fonts(repo, sub.local_path)

        task.complete("Indexed {count} new font families in '{repo}'".format(
            count=len(repo.families),
            repo=colored(repo.name, COLOR_INPUT)
        ))
