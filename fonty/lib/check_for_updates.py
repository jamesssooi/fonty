'''
    check_for_updates.py
    ~~~~~~~~~~~~~~~~~~~~
    Module to check for newer versions of fonty.
'''
from threading import Thread
from datetime import datetime

import requests
from packaging import version
from fonty.version import __version__
from fonty.lib.meta_store import MetaStore

FONTY_PYPI_URL = 'https://pypi.org/pypi/fonty/json'

def is_update_available() -> bool:
    '''Notify user to update fonty if a newer version is available.'''
    if __version__ is None or MetaStore.latest_version is None:
        return False

    current = version.parse(__version__)
    latest = version.parse(MetaStore.latest_version)
    return latest > current

def cache_latest_version() -> None:
    '''Get the latest fonty version from PyPi and stores in the local cache.'''

    # Check for updates at most once a day
    if MetaStore.last_check_for_update is not None:
        if (datetime.now() - MetaStore.last_check_for_update).total_seconds() < 86400:
            return

    def handler(): #pylint: disable=C0111
        try:
            r = requests.get(FONTY_PYPI_URL)
            d = r.json()
            version_string = d.get('info').get('version')
            if version_string:
                MetaStore.latest_version = version_string
                MetaStore.last_check_for_update = datetime.now()
                MetaStore.save()
        except: #pylint: disable=W0702
            pass

    Thread(target=handler, daemon=True).start()
