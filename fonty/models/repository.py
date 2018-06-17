'''repository.py'''
import json
from typing import List

from fonty.lib.variants import FontAttribute
from fonty.models.font import RemoteFontFamily, RemoteFont

class Repository(object):
    '''`Repository` is a class that provides an interface to manage a repository
    and its list of families.

    The `Repository` class does not manage subscriptions. For that, refer to the
    `Subscriptions` model instead.

    Attributes:
        `families` (List[RemoteFontFamily]): Font families available in this repository.
    '''

    #: The schema identifier for this schema
    schema_identifier: str = "fonty_json_schema_v1"

    #: The name of this repository
    name: str

    #: The font families available in this repository
    families: List[RemoteFontFamily]

    #: The remote path of this repository
    remote_path: str

    #: Sets if this repository is a public repository
    public: bool

    def __init__(
        self,
        name: str,
        families: List[RemoteFontFamily] = None,
        schema_identifier: str = None,
        remote_path: str = None,
        public: bool = False
    ) -> None:
        self.name = name
        self.families = families
        self.public = public
        self.remote_path = remote_path
        self.schema_identifier = schema_identifier if schema_identifier else self.schema_identifier

    def get_family(self, name):
        '''Returns a RemoteFontFamily object.'''
        return next((f for f in self.families if f.name == name), None)

    @staticmethod
    def load_from_json(json_data):
        '''Load a repository from a JSON string.'''
        repo = json_data
        if not isinstance(json_data, dict):
            repo = json.loads(json_data)
        schema_identifier = repo.get('schema_identifier', 'no_schema')

        # Convert all families into `RemoteFontFamily` instances
        remote_families = []

        # Parse `fonty_json_schema_v1`
        if schema_identifier == 'fonty_json_schema_v1':
            for family in repo['typefaces']:
                remote_families.append(RemoteFontFamily(
                    name=family['name'],
                    fonts=[
                        RemoteFont(
                            remote_path=RemoteFont.Path(
                                path=data['url'],
                                type=RemoteFont.Path.Type.HTTP_REMOTE
                            ),
                            filename=data['filename'],
                            family=family['name'],
                            variant=FontAttribute.parse(variant)
                        ) for variant, data in family['fonts'].items()
                    ]
                ))

        # Unknown schema
        else:
            raise Exception("Unknown repository schema '{}'.".format(schema_identifier))

        return Repository(
            name=repo['name'],
            families=remote_families,
            schema_identifier=schema_identifier,
            public=repo['public'],
            remote_path=repo['source'],
        )

    @staticmethod
    def load_from_path(path):
        '''Load a repository from a file.'''
        with open(path, encoding='utf-8') as f:
            data = f.read()

        return Repository.load_from_json(data)
