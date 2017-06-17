'''repository.py'''
import json
from typing import List

from fonty.models.typeface import Typeface

class Repository(object):
    '''`Repository` is a class that provides an interface to manage a repository
    and its list of typefaces.

    The `Repository` class does not manage subscriptions. For that, refer to the
    `Subscriptions` model instead.

    Attributes:
        `typefaces` (List[Typeface]): Typefaces available in this repository.
    '''

    def __init__(self, name: str, typefaces: List[Typeface] = None):
        self.name = name
        self.typefaces = typefaces

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

        return Repository(name=repo['name'],
                          typefaces=typefaces)

    @staticmethod
    def load_from_path(path):
        '''Load a repository from a file.'''
        with open(path, encoding='utf-8') as f:
            data = f.read()

        return Repository.load_from_json(data)
