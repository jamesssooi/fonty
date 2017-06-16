'''repository.py'''

import json
import os
from datetime import datetime
from pprint import pprint
from fonty.lib.constants import APP_DIR, SUBSCRIPTIONS_PATH
from fonty.models.typeface import Typeface
from fonty.models.font import Font

class Repository(object):
    '''A model for a repository'''

    def __init__(self, source, typefaces=None):
        self.source = source
        self.typefaces = typefaces

    def subscribe(self):
        '''Add this repository to user's subscription list.'''
        if not os.path.exists(APP_DIR):
            os.makedirs(APP_DIR, exist_ok=True)

        # Load existing subscription list
        subscriptions = None
        if os.path.exists(SUBSCRIPTIONS_PATH):
            with open(SUBSCRIPTIONS_PATH) as data:
                subscriptions = json.loads(data.read())
        else:
            subscriptions = []

        # Check if source is already subscribed
        # TODO: Implement exception
        repository = next((item for item in subscriptions['sources'] if item['remotePath'] == self.source), None)
        if repository:
            raise Exception
        
        subscriptions['sources'].append({
            'remotePath': self.source,
            'lastUpdated': datetime.now().isoformat()
        })

        # Write to file
        with open(SUBSCRIPTIONS_PATH, 'w') as f:
            json.dump(subscriptions, f, ensure_ascii=False)

        return self

    def unsubscribe(self):
        '''Remove this repository from users's subscription list.'''
        # Load existing subscription list
        subscriptions = None
        if os.path.exists(SUBSCRIPTIONS_PATH):
            with open(SUBSCRIPTIONS_PATH) as data:
                subscriptions = json.loads(data.read())
        else:
            subscriptions = []

        # Check if source is already unsubscribed
        # TODO: Implement exception
        repository = next((item for item in subscriptions['sources'] if item['remotePath'] == self.source), None)
        if not repository:
            raise Exception

        subscriptions.remove(repository)

        # Write to file
        with open(SUBSCRIPTIONS_PATH, 'w') as outfile:
            json.dump(subscriptions, outfile, ensure_ascii=False)

        return self

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

        # Convert all font objects into Font instances
        typefaces = []
        for typeface in repo['typefaces']:
            typefaces.append(Typeface.load_from_json(typeface))

        return Repository(repo['source'], typefaces)

    @staticmethod
    def load_from_local(source):
        '''Load a local repository.'''

        # Get local path to repository
        with open(SUBSCRIPTIONS_PATH) as f:
            sources = json.loads(f.read())
        repository = next((item for item in sources['sources'] if item['remotePath'] == source), None)

        if not repository: raise Exception

        # Read local repository file and create Repository instance
        with open(repository['localPath']) as f: data = f.read()
        return Repository.load_from_json(data)

    @staticmethod
    def load_all():
        '''Load all subscribed repositories.'''

        # Get list of subscriptions
        with open(SUBSCRIPTIONS_PATH) as f:
            sources = json.loads(f.read())
        
        # Get local repositories
        repositories = []
        for source in sources['sources']:
            with open(source['localPath']) as f: data = f.read()
            repositories.append(Repository.load_from_json(data))
        
        return repositories
