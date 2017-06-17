'''subscriptions.py'''
import os
import json
from datetime import datetime
from typing import List

import hashlib
import requests
from fonty.lib.constants import SUBSCRIPTIONS_PATH, REPOSITORY_DIR, JSON_DUMP_OPTS
from fonty.models.repository import Repository

class Subscription:
    '''Subscriptions is a class that provides an interface to manage a subscription.

    The Subscriptions class merely manages what repositories are available, and
    has no knowledge of its contents. To interface with a repository, refer to
    the Repository model.

    Attributes:
        `remote_path` (str): Remote URL of this repository.
        `local_path` (str): Path to local copy of the repository.
        `last_updated` (datetime): Last updated date.
    '''

    def __init__(self, remote_path: str, local_path: str, last_updated=None) -> None:
        self.remote_path = remote_path
        self.local_path = local_path
        self.last_updated = last_updated
        self.id_ = hashlib.md5(self.remote_path.encode('utf-8')).hexdigest()

    def fetch(self) -> bool:
        '''Update local copy of repository with remote.'''
        path = os.path.join(REPOSITORY_DIR, self.id_ + '.json')

        # Check if repository directory exists
        if not os.path.exists(REPOSITORY_DIR):
            os.makedirs(REPOSITORY_DIR, exist_ok=True)

        # Fetch remote repository
        request = requests.get(self.remote_path)
        data = request.content

        # Compare MD5 hash
        local_md5 = self.get_local_md5()
        remote_md5 = hashlib.md5(data).hexdigest()
        has_changes = True if local_md5 != remote_md5 else False

        # Replace local copy of repository with latest
        if has_changes:
            with open(path, 'wb') as f:
                f.write(data)

        # Update entry in subscriptions listing
        self.last_updated = datetime.now().isoformat()
        self.local_path = path
        Subscription.update_entry(self)

        return has_changes

    def get_local_repository(self) -> Repository:
        '''Gets the local copy of the repository.

        Returns:
            `Repository` A Repository instance of the local repository file.
        '''
        if not self.local_path:
            raise Exception

        return Repository.load_from_json(self.local_path)

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

    @staticmethod
    def update_entry(subscription: Subscription) -> None:
        '''Update an entry in the subscriptions list.

        Args:
            subscription (Subscription): The `Subscription` instance to be updated.
        '''

        # Get list of subscriptions from subscriptions.json
        data = {}
        if os.path.isfile(SUBSCRIPTIONS_PATH):
            with open(SUBSCRIPTIONS_PATH) as f:
                data = json.loads(f.read())

        # Get index value to replace, or `None` if there is no existing entry
        id_ = subscription.id_
        idx = next((idx for idx, val in enumerate(data['subscriptions']) if val['id'] == id_), None)

        # Update with new value
        subscription_data = {
            'id': subscription.id_,
            'remotePath': subscription.remote_path,
            'localPath': subscription.local_path,
            'lastUpdated': subscription.last_updated
        }
        if idx is not None:
            data[idx] = subscription_data
        elif idx is None:
            data.append(subscription_data)

        # Write to file (subscriptions.json)
        with open(SUBSCRIPTIONS_PATH, 'w') as f:
            json.dump({'subscriptions': data}, f, **JSON_DUMP_OPTS)

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
        with open(path) as f:
            data = json.loads(f.read())

        subscriptions = []
        for sub in data['subscriptions']:
            subscriptions.append(Subscription(
                remote_path=sub.get('remotePath', None),
                local_path=sub.get('localPath', None),
                last_updated=sub.get('lastUpdated', None)
            ))

        return subscriptions
