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
            subscriptions = {}

        # Check if source is already subscribed
        # TODO: Implement exception
        if self.source in subscriptions:
            raise Exception

        subscriptions[self.source] = {
            'source': self.source,
            'last_updated': datetime.now().isoformat()
        }

        # Write to file
        with open(SUBSCRIPTIONS_PATH, 'w') as outfile:
            json.dump(subscriptions, outfile, ensure_ascii=False)

        return self


    def unsubscribe(self):
        '''Remove this repository from users's subscription list.'''
        # Load existing subscription list
        subscriptions = None
        if os.path.exists(SUBSCRIPTIONS_PATH):
            with open(SUBSCRIPTIONS_PATH) as data:
                subscriptions = json.loads(data.read())
        else:
            subscriptions = {}
        
        # Check if source is already unsubscribed
        # TODO: Implement exception
        if self.source not in subscriptions:
            raise Exception

        del subscriptions[self.source]

        # Write to file
        with open(SUBSCRIPTIONS_PATH, 'w') as outfile:
            json.dump(subscriptions, outfile, ensure_ascii=False)

        return self

    @staticmethod
    def load_from_json(json_string):
        '''Load a repository from a JSON string.'''
        repo = json.loads(json_string)

        # Convert all font objects into Font instances
        typefaces = []
        for typeface in repo['typefaces']:
            fonts = [Font(v, k) for k, v in typeface['fonts'].items()]
            typefaces.append(Typeface(typeface['name'], fonts))

        return Repository(repo['source'], typefaces)

    @staticmethod
    def load_from_external_json(url):
        '''Load an external repository.'''
        pass
