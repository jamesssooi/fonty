'''repository.py'''
import json
from typing import List

from fonty.lib.variants import FontAttribute
from fonty.models.font import FontFamily, RemoteFontFamily, RemoteFont

class Repository(object):
    '''`Repository` is a class that provides an interface to manage a repository
    and its list of families.

    The `Repository` class does not manage subscriptions. For that, refer to the
    `Subscriptions` model instead.

    Attributes:
        `families` (List[RemoteFontFamily]): Font families available in this repository.
    '''

    def __init__(self, name: str, families: List[RemoteFontFamily] = None):
        self.name = name
        self.families = families

    def get_family(self, name):
        '''Returns a RemoteFontFamily object.'''
        return next((f for f in self.families if f.name == name), None)

    @staticmethod
    def load_from_json(json_data):
        '''Load a repository from a JSON string.'''
        repo = json_data
        if not isinstance(json_data, dict):
            repo = json.loads(json_data)

        # Convert all families into `RemoteFontFamily` instances
        remote_families = []
        for family in repo['typefaces']:
            remote_families.append(RemoteFontFamily(
                name=family['name'],
                fonts=[
                    RemoteFont(
                        remote_path=data['url'],
                        filename=data['filename'],
                        family=family['name'],
                        variant=FontAttribute.parse(variant)
                    ) for variant, data in family['fonts'].items()
                ]
            ))

        return Repository(
            name=repo['name'],
            families=remote_families
        )

    @staticmethod
    def load_from_path(path):
        '''Load a repository from a file.'''
        with open(path, encoding='utf-8') as f:
            data = f.read()

        return Repository.load_from_json(data)
