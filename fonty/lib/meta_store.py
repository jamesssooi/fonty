'''
    meta_store.py
    ~~~~~~~~~~~~~
    Module for the storage and retrieval of persistent values throughout the
    usage of fonty on a single device.
'''
import os
import pickle
from typing import Dict, List
from datetime import datetime

from fonty.version import __version__
from fonty.lib.constants import META_STORE_PATH

class BaseMetaStore(dict):
    '''The MetaStore contains meta information about fonty.'''

    #: Define a list of attributes that are readonly
    _read_only_attrs: List[str] = []

    #: The latest version of fonty
    latest_version: str = None

    #: The last check for update that occurred
    last_check_for_update: datetime = None

    def __setattr__(self, key, value):
        '''Override to prevent modification of readonly attributes.'''
        if key in self._read_only_attrs:
            raise Exception('Cannot set readonly attribute {}'.format(key))
        super(BaseMetaStore, self).__setattr__(key, value)

    def __init__(self) -> None:
        super().__init__()

        # Create default meta store if it doesn't exist
        if not os.path.isfile(META_STORE_PATH):
            with open(META_STORE_PATH, 'wb+') as f:
                pickle.dump({}, f)

        # Load existing meta store from disk
        with open(META_STORE_PATH, 'rb') as f:
            d = pickle.load(f)
            self.set_dict(d)

    def reset(self) -> None:
        '''Resets the meta store to defaults.'''
        with open(META_STORE_PATH, 'wb+') as f:
            pickle.dump({}, f)
        self.__dict__ = {}

    def save(self) -> None:
        '''Save all changes to the disk.'''
        with open(META_STORE_PATH, 'wb+') as f:
            pickle.dump(self.get_dict(), f)

    def set_dict(self, d) -> None:
        '''Updates the meta store with the provided dict.'''
        self.__dict__.update(d)

    def get_dict(self) -> Dict:
        '''Gets the dict representation of the current meta store.'''
        d = {}
        for key, value in [(k, getattr(self, k)) for k in dir(self)
                           if not callable(getattr(self, k)) and not k.startswith('__')]:
            d[key] = value
        return d

# MetaStore is an initialised instance of BaseMetaStore.
MetaStore = BaseMetaStore()
