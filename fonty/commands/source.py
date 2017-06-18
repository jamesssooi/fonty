'''fonty.commands.source.py: Command-line interface to manage sources.'''
import timeit
import shutil

import click
from termcolor import colored
from fonty.lib import search
from fonty.lib.task import Task, TaskStatus
from fonty.lib.constants import COLOR_INPUT, SEARCH_INDEX_PATH
from fonty.models.subscription import Subscription

@click.group('source')
def cli_source():
    pass

@cli_source.command()
@click.argument('url')
def add(url):
    '''Add a new source.'''

    # Add to subscription list and fetch remote repository
    task = Task("Loading '{}'...".format(colored(url, COLOR_INPUT)))
    sub = Subscription(remote_path=url).subscribe()
    repo = sub.get_local_repository()
    task.stop(status=TaskStatus.SUCCESS,
              message="Loaded '{}'".format(colored(repo.name, COLOR_INPUT)))

    # Index fonts
    task = Task("Indexing {count} typeface(s) in '{repo}'".format(
        count=len(repo.typefaces),
        repo=colored(repo.name, COLOR_INPUT)
    ))
    search.index_fonts(repo, sub.local_path)
    task.stop(status=TaskStatus.SUCCESS,
              message="Indexed {count} new typeface(s)".format(
                  count=colored(len(repo.typefaces), COLOR_INPUT)
              ))


@cli_source.command()
def remove():
    print('Remove source')


@cli_source.command()
@click.option('--force', '-f', is_flag=True)
def update(force: bool):
    '''Fetch latest repository data and reindex fonts.'''

    # Delete search index directory if `force` flag is True
    if force:
        shutil.rmtree(SEARCH_INDEX_PATH)

    subscriptions = Subscription.load_entries()
    for sub in subscriptions:
        name = colored(sub.get_local_repository().name, COLOR_INPUT)
        task = Task("Updating '{}'".format(name))

        # Fetch remote repositories
        sub, has_changes = sub.fetch()
        if not has_changes and not force:
            task.stop(status=TaskStatus.SUCCESS,
                      message="No updates available for '{}'".format(name))
            continue

        # Reindex fonts
        task.message = "Indexing '{}'".format(name)
        updated_repo = sub.get_local_repository()
        search.index_fonts(updated_repo, sub.local_path)

        task.stop(status=TaskStatus.SUCCESS,
                  message="Updated '{}'".format(name))
