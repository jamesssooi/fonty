'''repository.py'''
import json
import os
import hashlib
from typing import List
from datetime import datetime

import requests
from fonty.lib.constants import APP_DIR, SUBSCRIPTIONS_PATH, REPOSITORY_DIR
from fonty.models.typeface import Typeface

class Repository(object):
    '''`Repository` is a class that provides an interface to manage a repository
    and its list of typefaces.

    The `Repository` class does not manage subscriptions. For that, refer to the
    `Subscriptions` model instead.

    Attributes:
        `typefaces` (List[Typeface]): Typefaces available in this repository.
    '''

    def __init__(self, typefaces: List[Typeface] = None):
        self.typefaces = typefaces

    # def subscribe(self):
    #     '''Add this repository to user's subscription list.'''
    #     if not os.path.exists(APP_DIR):
    #         os.makedirs(APP_DIR, exist_ok=True)

    #     # Load existing subscription list
    #     subscriptions = None
    #     if os.path.exists(SUBSCRIPTIONS_PATH):
    #         with open(SUBSCRIPTIONS_PATH) as data:
    #             subscriptions = json.loads(data.read())
    #     else:
    #         subscriptions = {}

    #     # Check if source is already subscribed
    #     # TODO: Implement exception
    #     if self.source in subscriptions:
    #         raise Exception

    #     subscriptions[self.source] = {
    #         'source': self.source,
    #         'last_updated': datetime.now().isoformat()
    #     }

    #     # Write to file
    #     with open(SUBSCRIPTIONS_PATH, 'w') as outfile:
    #         json.dump(subscriptions, outfile, ensure_ascii=False)

    #     return self

    # def unsubscribe(self):
    #     '''Remove this repository from users's subscription list.'''
    #     # Load existing subscription list
    #     subscriptions = None
    #     if os.path.exists(SUBSCRIPTIONS_PATH):
    #         with open(SUBSCRIPTIONS_PATH) as data:
    #             subscriptions = json.loads(data.read())
    #     else:
    #         subscriptions = {}

    #     # Check if source is already unsubscribed
    #     # TODO: Implement exception
    #     if self.source not in subscriptions:
    #         raise Exception

    #     del subscriptions[self.source]

    #     # Write to file
    #     with open(SUBSCRIPTIONS_PATH, 'w') as outfile:
    #         json.dump(subscriptions, outfile, ensure_ascii=False)

    #     return self

    def get_typeface(self, name):
        '''Returns a Typeface object.'''
        typeface = next((x for x in self.typefaces if x.name == name), None)
        if typeface is None:
            raise Exception

        return typeface

    @staticmethod
    def load_from_json(json_data):
        '''Load a repository from a JSON string.'''
        repo = json_data
        if not isinstance(json_data, dict):
            repo = json.loads(json_data)

        # Convert all typefaces into `Typeface` instances
        typefaces = []
        for typeface in repo['typefaces']:
            typefaces.append(Typeface.load_from_json(typeface))

        return Repository(typefaces)
    
    @staticmethod
    def load_from_path(path):
        '''Load a repository from a file.'''
        with open(path) as f:
            return Repository.load_from_json(f.read())

    @staticmethod
    def load_from_local(source):
        '''Load a local repository.'''

        # Get local path to repository
        with open(SUBSCRIPTIONS_PATH) as f:
            sources = json.loads(f.read())
        repository = next((
            item for item in sources['sources'] if item['remotePath'] == source
        ), None)

        if not repository:
            raise Exception

        # Read local repository file and create Repository instance
        with open(repository['localPath']) as f:
            data = f.read()
        return Repository.load_from_json(data)
