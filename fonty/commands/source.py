'''fonty.commands.source.py: Command-line interface to manage sources.'''
import shutil
import sys
import time
import timeit

import click
from termcolor import colored
from fonty.lib import search
from fonty.lib.task import Task, TaskStatus
from fonty.lib.constants import COLOR_INPUT, SEARCH_INDEX_PATH
from fonty.models.subscription import Subscription

@click.group('source')
def cli_source():
    '''Manage font sources'''
    pass

@cli_source.command()
@click.argument('url')
def add(url):
    '''Add a new source'''

    # Add to subscription list and fetch remote repository
    task = Task("Loading '{}'...".format(colored(url, COLOR_INPUT)))
    sub = Subscription.load_from_url(url).subscribe()
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

    print('')
    sub.pprint(output=True)


@cli_source.command()
@click.pass_context
@click.argument('identifier', nargs=-1)
def remove(ctx, identifier: str):
    '''Remove a source'''

    # Process arguments and options
    identifier = ' '.join(str(x) for x in identifier)

    if not identifier:
        click.echo(ctx.get_help())
        click.echo('\nError: Missing argument')
        sys.exit(1)

    # Search for subscription
    task = Task("Looking for '{}'".format(colored(identifier, COLOR_INPUT)))
    sub = Subscription.get(identifier)

    if sub is None:
        time.sleep(0.3)
        task.stop(status=TaskStatus.ERROR,
                  message="No subscriptions found with '{}'".format(
                      colored(identifier, COLOR_INPUT)))
        return

    # Unsubscribe
    task.message = "Unsubscribing '{}'".format(colored(sub.name, COLOR_INPUT))
    sub.unsubscribe()
    task.stop(status=TaskStatus.SUCCESS,
              message="Unsubscribed from '{}'".format(colored(sub.name, COLOR_INPUT)))

    # Reindex fonts
    task = Task('Reindexing fonts...')
    count = search.unindex_fonts(sub.local_path)
    task.stop(status=TaskStatus.SUCCESS,
              message="Removed {} typeface(s) from index".format(colored(count, 'cyan')))

@cli_source.command(name='list')
def list_():
    '''List all subscribed sources'''
    subscriptions = Subscription.load_entries()
    count = 1
    for sub in subscriptions:
        s = sub.pprint(join=False)

        # Add numbering to output
        count_str = '[{}] '.format(count)
        s[0] = count_str + s[0]

        # Indent
        INDENT_COUNT = len(count_str)
        for i in range(1, len(s)):
            s[i] = (' ' * INDENT_COUNT) + s[i]

        # Output to console
        click.echo('\n'.join(s))
        click.echo('')

        count += 1



@cli_source.command()
@click.option('--force', '-f', is_flag=True)
def update(force: bool):
    '''Update all sources'''

    # Delete search index directory if `force` flag is True
    if force:
        shutil.rmtree(SEARCH_INDEX_PATH)

    subscriptions = Subscription.load_entries()

    if not subscriptions:
        click.echo('No sources to update')

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
