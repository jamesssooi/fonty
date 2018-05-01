'''subscriptions.py'''
import os
import json
import hashlib
from datetime import datetime
from typing import List, Tuple, Union, Any, cast

import timeago
import requests
import dateutil.parser
from termcolor import colored
from fonty.lib.constants import SUBSCRIPTIONS_PATH, REPOSITORY_DIR, JSON_DUMP_OPTS
from fonty.models.repository import Repository

class Subscription:
    '''Subscriptions is a class that provides an interface to manage a subscription.

    The Subscriptions class merely manages what repositories are available, and
    has no knowledge of its contents. To interface with a repository, refer to
    the Repository model.

    Attributes:
        `name` (str): Name of this repository.
        `remote_path` (str): Remote URL of this repository.
        `local_path` (str): Path to local copy of the repository.
        `last_updated` (datetime): Last updated date.
        `repo` (Repository): The repository this subscription contains.
    '''

    #: The name of the remote source.
    name: str

    #: The remote path to the remote copy of the source.
    remote_path: str

    #: The local path to the local copy of the source.
    local_path: str

    #: The repository instance.
    repository: Repository

    #: The timestamp of when the local copy was last synced with the remote copy.
    last_updated: datetime

    def __init__(
        self,
        name: str,
        remote_path: str,
        local_path: str = None,
        repo: Repository = None,
        last_updated: Union[str, datetime] = None
    ) -> None:
        self.name = name
        self.remote_path = remote_path
        self.local_path = local_path
        self.repo = repo
        self.id_ = hashlib.md5(self.remote_path.encode('utf-8')).hexdigest()

        # Parse last updated date
        if isinstance(last_updated, str):
            self.last_updated = dateutil.parser.parse(cast(str, last_updated))
        else:
            self.last_updated = cast(datetime, last_updated)

    def fetch(self, save_to_local: bool = False) -> Tuple['Subscription', bool]:
        '''Update local copy of repository with remote.

        Returns a tuple of `(self, has_changes)`
        '''
        # Fetch remote repository
        request = requests.get(self.remote_path)
        data = request.content

        # Check if valid Repository schema
        try:
            repo = Repository.load_from_json(data)
        except ValueError:
            raise NotJSONError('Data not valid JSON') from None

        # Compare MD5 hash
        local_md5 = self.get_local_md5()
        remote_md5 = hashlib.md5(data).hexdigest()
        has_changes = True if local_md5 != remote_md5 else False

        # Update attributes
        self.repo = repo
        self.last_updated = datetime.now()

        # Replace local copy of repository with latest
        if save_to_local:
            self.save_to_local(data)

        # Update subscription entry list
        Subscription.update_entry(self)

        return self, has_changes

    def save_to_local(self, bytes_: bytes) -> str:
        '''Saves a local copy of the repository. Returns a path to the local file.'''
        # Check if repository directory exists
        if not os.path.exists(REPOSITORY_DIR):
            os.makedirs(REPOSITORY_DIR, exist_ok=True)

        # Write to file
        path = os.path.join(REPOSITORY_DIR, self.id_ + '.json')
        with open(path, 'wb') as f:
            f.write(bytes_)

        # Update attribtues
        self.local_path = path

        return path

    def get_local_repository(self) -> Repository:
        '''Gets the local copy of the repository.

        Returns:
            `Repository` A Repository instance of the local repository file.
        '''
        if not self.local_path:
            raise Exception

        return Repository.load_from_path(self.local_path)

    def get_local_md5(self) -> str:
        '''Returns a MD5 hash representation of the local repository file.

        Returns:
            `str` MD5 hash string of the local repository file.
            `None` if no local copy exists.
        '''
        if not self.local_path:
            return None

        if not os.path.isfile(self.local_path):
            return None

        with open(self.local_path, mode='rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def subscribe(self) -> 'Subscription':
        '''Add this subscription to the user's subscription list.

        This method is a convenience wrapper around the `fetch` method. The
        The `fetch` automatically appends the data to the subscriptions list if
        no existing similar entry is found.
        '''
        # Check if source is already subscribed
        if os.path.isfile(SUBSCRIPTIONS_PATH):
            with open(SUBSCRIPTIONS_PATH, encoding='utf-8') as f:
                data = json.loads(f.read())

            if 'subscriptions' in data:
                idx = next((
                    idx for idx, val in enumerate(data['subscriptions'])
                    if val['id'] == self.id_
                ), None)

                if idx is not None:
                    raise AlreadySubscribedError

        subscription, _ = self.fetch(save_to_local=True)
        return subscription

    def unsubscribe(self) -> None:
        '''Remove this subscription from the user's subscription list.'''

        if not os.path.isfile(SUBSCRIPTIONS_PATH):
            return

        # Get list of subscriptions from subscriptions.json
        data: dict = {}
        with open(SUBSCRIPTIONS_PATH, encoding='utf-8') as f:
            data = json.loads(f.read())

        if 'subscriptions' not in data:
            return

        # Get index value to replace, or `None` if there is no existing entry
        id_ = self.id_
        idx = next((idx for idx, val in enumerate(data['subscriptions']) if val['id'] == id_), None)

        if idx is not None:
            del data['subscriptions'][idx]

        # Write to file
        with open(SUBSCRIPTIONS_PATH, 'w') as f:
            json.dump(data, f, **JSON_DUMP_OPTS)

    def pprint(self, output: bool = False, ansi: bool = True,
               join: bool = True) -> Union[str, List[str]]:
        '''Pretty prints the details of this subscription.'''
        format_ = [
            '{name} @ {url}',
            '- ID: {id_}',
            '- Families available: {count}',
            '- Last updated: {last_updated}',
        ]

        # Generate details
        repo = self.get_local_repository()
        name = colored(repo.name, 'cyan') if ansi else repo.name
        url = colored(self.remote_path, attrs=['dark']) if ansi else self.remote_path
        id_ = colored(self.id_, attrs=['dark']) if ansi else self.id_
        count = colored(str(len(repo.families)), attrs=['dark']) \
                if ansi else str(len(repo.families))

        last_updated = timeago.format(self.last_updated)
        last_updated = colored(last_updated, attrs=['dark']) if ansi else last_updated

        lines = [line.format(
            name=name,
            url=url,
            id_=id_,
            count=count,
            last_updated=last_updated
        ) for line in format_]

        if output:
            print('\n'.join(lines))

        if join:
            return '\n'.join(lines)

        return lines

    @staticmethod
    def update_entry(subscription: 'Subscription') -> None:
        '''Update an entry in the subscriptions list.

        Args:
            subscription (Subscription): The `Subscription` instance to be updated.
        '''

        # Get list of subscriptions from subscriptions.json
        data: Any = {}
        if os.path.isfile(SUBSCRIPTIONS_PATH):
            with open(SUBSCRIPTIONS_PATH, encoding='utf-8') as f:
                content = f.read()
                if not content:
                    data = {}
                else:
                    data = json.loads(content)

        if 'subscriptions' not in data:
            data['subscriptions'] = []

        # Get index value to replace, or `None` if there is no existing entry
        id_ = subscription.id_
        idx = next((
            idx for idx, val in enumerate(data['subscriptions'])
            if 'id' in val and val['id'] == id_
        ), None)

        # Update with new value
        subscription_data = {
            'id': subscription.id_,
            'name': subscription.name,
            'remote_path': subscription.remote_path,
            'local_path': subscription.local_path,
            'last_updated': subscription.last_updated.isoformat()
        }
        if idx is not None:
            data['subscriptions'][idx] = subscription_data
        elif idx is None:
            data['subscriptions'].append(subscription_data)

        # Write to file (subscriptions.json)
        with open(SUBSCRIPTIONS_PATH, 'w') as f:
            json.dump(data, f, **JSON_DUMP_OPTS)

    @staticmethod
    def load_entries(path: str = None) -> List['Subscription']:
        '''Load all subscribed repositories.

        Returns:
            `List[Subscription]` A list of Subscription instances
        '''
        if not path:
            path = SUBSCRIPTIONS_PATH

        # Get list of subscriptions from subscriptions.json
        if not os.path.isfile(path):
            return []
        with open(path, encoding='utf-8') as f:
            data = json.loads(f.read())

        subscriptions = []
        for sub in data['subscriptions']:
            subscriptions.append(Subscription(
                name=sub.get('name', None),
                remote_path=sub.get('remote_path', None),
                local_path=sub.get('local_path', None),
                last_updated=sub.get('last_updated', None)
            ))

        return subscriptions

    @staticmethod
    def load_from_url(url: str) -> 'Subscription':
        '''Load a subscription from a repository URL.'''
        request = requests.get(url)
        data = request.content

        # Check if valid Repository schema
        try:
            repo = Repository.load_from_json(data)
        except ValueError:
            raise NotJSONError('Data not a valid JSON file') from None

        return Subscription(name=repo.name, remote_path=url, repo=repo)

    @staticmethod
    def get(id_: str) -> 'Subscription':
        '''Finds and returns a subscription.'''
        subscriptions = Subscription.load_entries()

        return next((
            sub for sub in subscriptions if sub.remote_path == id_
            or sub.name == id_
            or sub.id_ == id_
        ), None)


class AlreadySubscribedError(Exception):
    pass

class NotJSONError(ValueError):
    pass